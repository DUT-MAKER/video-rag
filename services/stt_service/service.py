from __future__ import annotations

import gc
import os
import pathlib
import bentoml
from loguru import logger
from pydantic import BaseModel, Field
import torch
import whisperx
from whisperx.diarize import DiarizationPipeline
from whisperx.vads import Pyannote as VadPyannote

from services.stt_service.visualizer import plot_pipeline_steps

image = bentoml.images.Image(python_version="3.11").python_packages(
    "whisperx>=3.3.0",
    "pyannote.audio>=3.1.0",
    "torch>=2.2.0",
    "torchaudio>=2.2.0",
    "tokenizers>=0.22.0,<=0.23.0",
    "pydantic>=2.0.0",
    "loguru>=0.7.0",
)


class TranscriptSegmentDTO(BaseModel):
    """Timestamped transcript segment with speaker attribution."""

    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    text: str = Field(description="Transcribed text content")
    speaker: str = Field(default="SPEAKER_00", description="Speaker ID label")


class TranscriptionResponseDTO(BaseModel):
    """Full speech-to-text and diarization response."""

    full_text: str = Field(description="Complete transcript plain text")
    segments: list[TranscriptSegmentDTO] = Field(
        default_factory=list, description="Speaker-attributed segments"
    )
    speaker_count: int = Field(default=0, description="Total distinct speakers detected")
    language: str = Field(default="vi", description="Language code")
    duration_seconds: float = Field(default=0.0, description="Audio duration in seconds")
    debug_chart_path: str | None = Field(
        default=None, description="Path to generated 6-track visual debug timeline PNG"
    )


@bentoml.service(
    name="whisperx_stt",
    image=image,
    resources={"gpu": 1},
    traffic={"timeout": 300},
)
class WhisperXService:
    """BentoML Service with Dynamic RAM-to-VRAM Offloading for WhisperX + Pyannote."""

    def __init__(self) -> None:
        self.whisper_model_name = os.getenv("WHISPER_MODEL", "large-v3-turbo")
        self.device_preference = os.getenv(
            "WHISPER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.user_compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "")
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.batch_size = 8
        self.diarization_device = os.getenv("DIARIZATION_DEVICE", "cpu")
        self.diarization_model = os.getenv(
            "DIARIZATION_MODEL", "pyannote/speaker-diarization-3.1"
        )

        self.default_language = "vi"
        # In-memory RAM caches
        self._align_models_cpu: dict[str, tuple[torch.nn.Module, dict]] = {}


        logger.info(
            f"Initialized WhisperXService (Pref: {self.device_preference}, Model: {self.whisper_model_name}, Lang: {self.default_language})"
        )


    
        logger.info(
            f"Pre-loading Pyannote Diarization Pipeline ({self.diarization_model}) into Host RAM (CPU)..."
        )
        self.diarize_pipeline = DiarizationPipeline(
            model_name=self.diarization_model,
            token=self.hf_token,
            device="cpu",
        )
        logger.info("Pyannote Diarization Pipeline successfully pre-loaded in RAM.")


        # 2. Preload VAD (Voice Activity Detection) Model in Host RAM (CPU)
        self.vad_onset = 0.500
        self.vad_offset = 0.363
        logger.info(
            f"Pre-loading VAD (Voice Activity Detection) Model (onset={self.vad_onset}, offset={self.vad_offset}) into Host RAM (CPU)..."
        )
        self.vad_model = VadPyannote(
            device="cpu",
            token=self.hf_token,
            vad_onset=self.vad_onset,
            vad_offset=self.vad_offset,
        )
        logger.info("VAD Model successfully pre-loaded in RAM.")

        logger.info(
            f"Pre-loading Forced Alignment Model for '{self.default_language}' into Host RAM (CPU)..."
        )
        self._get_or_load_align_model(self.default_language)
        logger.info(
            f"Forced Alignment Model ('{self.default_language}') successfully pre-loaded in RAM."
        )

    def _cleanup_memory(self) -> None:
        """Release CUDA memory and force Python garbage collection."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def _get_free_vram_mb(self) -> float:
        """Return free CUDA VRAM in megabytes."""
        if not torch.cuda.is_available():
            return 0.0
        try:
            free_bytes, _ = torch.cuda.mem_get_info()
            return free_bytes / (1024 * 1024)
        except Exception:
            return 0.0

    def _resolve_runtime_device(self, required_vram_mb: int = 1200) -> tuple[str, str]:
        """Dynamically decide whether to run on CUDA or fallback to CPU based on free VRAM."""
        if self.device_preference != "cuda" or not torch.cuda.is_available():
            return "cpu", "int8"

        free_mb = self._get_free_vram_mb()
        logger.info(f"Available GPU VRAM: {free_mb:.1f} MB (Required: {required_vram_mb} MB)")

        if free_mb >= required_vram_mb:
            compute_type = self.user_compute_type or "int8_float16"
            return "cuda", compute_type
        else:
            logger.warning(
                f"Low VRAM ({free_mb:.1f} MB < {required_vram_mb} MB). Offloading to CPU (int8)."
            )
            return "cpu", "int8"

    def _get_or_load_align_model(self, language_code: str) -> tuple[torch.nn.Module, dict]:
        """Get pre-cached alignment model from Host RAM (CPU) or load it."""
        if language_code not in self._align_models_cpu:
            logger.info(f"Loading alignment model for '{language_code}' into Host RAM (CPU)...")
            align_model, align_metadata = whisperx.load_align_model(
                language_code=language_code,
                device="cpu",
            )
            self._align_models_cpu[language_code] = (align_model, align_metadata)
        return self._align_models_cpu[language_code]

    @bentoml.api
    def transcribe(
        self,
        audio: pathlib.Path,
        language: str = "vi",
        enable_diarization: bool = True,
        debug_chart_path: str | None = None,
    ) -> TranscriptionResponseDTO:
        """Transcribe an audio file with timestamps and speaker attribution.

        Args:
            audio: Path to the input audio file (WAV/MP3).
            language: Target language code (default 'vi').
            enable_diarization: Whether to run pyannote speaker diarization.
            debug_chart_path: Optional output file path to save a 6-track visual debug PNG chart.

        Returns:
            TranscriptionResponseDTO containing full_text, segments with speakers, and speaker count.
        """
        audio_str = str(audio)
        if not os.path.exists(audio_str):
            raise bentoml.exceptions.InvalidArgument(f"Audio file not found: {audio_str}")

        # 1. Load Audio into Host RAM
        logger.info(f"Loading audio file: {audio_str}")
        audio_arr = whisperx.load_audio(audio_str)
        duration_seconds = float(len(audio_arr) / 16000.0)

        # 2. Dynamic ASR Device Allocation
        run_device, run_compute_type = self._resolve_runtime_device(required_vram_mb=1200)
        
        asr_options = {
            "repetition_penalty": 1.25,
            "no_repeat_ngram_size": 3,
            "hallucination_silence_threshold": 2.0,
        }

        asr_model = whisperx.load_model(
            self.whisper_model_name,
            device=run_device,
            compute_type=run_compute_type,
            language=language,
            asr_options=asr_options,
            vad_model=self.vad_model,
            vad_options={"vad_onset": self.vad_onset, "vad_offset": self.vad_offset},
        )
        logger.info(
            f"Step 1/3: Running ASR on {run_device.upper()} (Compute: {run_compute_type}, Batch: {self.batch_size})..."
        )

        raw_result = asr_model.transcribe(
            audio_arr,
            batch_size=self.batch_size,
            language=language,
        )
        # Immediate VRAM release after ASR
        del asr_model
        self._cleanup_memory()

        detected_language = raw_result.get("language", language) or language
        segments_data = raw_result.get("segments", [])
        if not segments_data:
            return TranscriptionResponseDTO(
                full_text="",
                segments=[],
                speaker_count=0,
                language=detected_language,
                duration_seconds=duration_seconds,
            )

        # 3. Dynamic Forced Alignment
        logger.info(f"Step 2/3: Running Forced Alignment for '{detected_language}'...")
        try:
            align_model, align_metadata = self._get_or_load_align_model(detected_language)
            align_device, _ = self._resolve_runtime_device(required_vram_mb=800)

            if align_device == "cuda":
                # Temporarily transfer model to VRAM for fast alignment
                align_model.to(torch.device("cuda"))
                target_dev = "cuda"
            else:
                target_dev = "cpu"

            aligned_result = whisperx.align(
                segments_data,
                align_model,
                align_metadata,
                audio_arr,
                target_dev,
                return_char_alignments=False,
            )

            # Bring model back to Host RAM and clean up VRAM
            if align_device == "cuda":
                align_model.to(torch.device("cpu"))
                self._cleanup_memory()

        except Exception as exc:
            logger.warning(f"Alignment fallback to unaligned segments: {exc}")
            aligned_result = {"segments": segments_data}
            self._cleanup_memory()

        # 4. Dynamic Speaker Diarization
        if enable_diarization:
            logger.info("Step 3/3: Running Speaker Diarization...")
            diarize_pipeline = self.diarize_pipeline
            try:
                # If GPU has ample VRAM, move pipeline to CUDA temporarily
                diarize_dev, _ = self._resolve_runtime_device(required_vram_mb=1800)
                if diarize_dev == "cuda" and self.diarization_device == "cuda":
                    diarize_pipeline.to(torch.device("cuda"))
                    exec_dev = "cuda"
                else:
                    exec_dev = "cpu"

                diarize_segments = diarize_pipeline(audio_arr)
                aligned_result = whisperx.assign_word_speakers(
                    diarize_segments, aligned_result
                )

                if exec_dev == "cuda":
                    diarize_pipeline.to(torch.device("cpu"))
                    self._cleanup_memory()

            except Exception as exc:
                logger.warning(f"Diarization skipped due to error: {exc}")
                self._cleanup_memory()

        # 5. Assemble DTO Response
        segments: list[TranscriptSegmentDTO] = []
        speaker_set: set[str] = set()
        full_text_parts: list[str] = []

        for seg in aligned_result.get("segments", []):
            text = seg.get("text", "").strip()
            if not text:
                continue
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", start))
            speaker = seg.get("speaker", "SPEAKER_00")
            speaker_set.add(speaker)
            full_text_parts.append(text)
            segments.append(
                TranscriptSegmentDTO(
                    start=start,
                    end=end,
                    text=text,
                    speaker=speaker,
                )
            )

        speaker_count = max(len(speaker_set), 1) if segments else 0
        full_text = " ".join(full_text_parts)

        # 6. Automatic Visual Debug Chart Rendering
        target_chart_path = debug_chart_path or "debug_output/latest_transcribe_timeline.png"
        saved_chart: str | None = None
        try:
            # Extract VAD segments for visual debugging
            vad_segments_list = []
            if self.vad_model is not None:
                try:
                    waveform = self.vad_model.preprocess_audio(audio_arr)
                    raw_vad = self.vad_model({"waveform": waveform, "sample_rate": 16000})
                    vad_merged = self.vad_model.merge_chunks(
                        raw_vad,
                        chunk_size=30,
                        onset=self.vad_onset,
                        offset=self.vad_offset,
                    )
                    for chunk in vad_merged:
                        vad_segments_list.append({
                            "start": float(chunk["start"]),
                            "end": float(chunk["end"]),
                        })
                except Exception as vad_err:
                    logger.warning(f"Failed to extract VAD segments for debug plot: {vad_err}")

            plot_pipeline_steps(
                audio_arr=audio_arr,
                vad_segments=vad_segments_list if vad_segments_list else None,
                raw_asr_segments=segments_data,
                aligned_segments=aligned_result.get("segments", []),
                diarize_segments=diarize_segments if enable_diarization and "diarize_segments" in locals() else None,
                output_image_path=target_chart_path,
            )
            saved_chart = target_chart_path
            logger.info(f"🖼️ [DEBUG TIMELINE] Visual 6-track chart saved to: {target_chart_path}")
        except Exception as exc:
            logger.warning(f"Failed to generate debug chart: {exc}")

        logger.info(
            f"Transcription complete: {len(segments)} segments, {speaker_count} speakers, {duration_seconds:.1f}s audio"
        )

        return TranscriptionResponseDTO(
            full_text=full_text,
            segments=segments,
            speaker_count=speaker_count,
            language=detected_language,
            duration_seconds=duration_seconds,
            debug_chart_path=saved_chart,
        )
