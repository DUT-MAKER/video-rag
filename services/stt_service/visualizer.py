from __future__ import annotations

import pathlib
from typing import Any, List, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def plot_pipeline_steps(
    audio_arr: np.ndarray,
    sample_rate: int = 16000,
    vad_segments: Optional[List[dict]] = None,
    raw_asr_segments: Optional[List[dict]] = None,
    aligned_segments: Optional[List[dict]] = None,
    diarize_segments: Optional[Any] = None,
    output_image_path: str = "debug_pipeline_timeline.png",
    title: str = "WhisperX STT + Diarization Step-by-Step Pipeline Debug",
) -> str:
    """Generate a multi-track timeline visualization of each step in the pipeline.

    Tracks:
    1. Audio Waveform
    2. Voice Activity Detection (VAD)
    3. Raw Whisper ASR Chunks
    4. Word-Level Forced Alignment (Wav2Vec2)
    5. Pyannote Speaker Diarization
    6. Final Attributed Segments (Speaker + Text)
    """
    duration = len(audio_arr) / sample_rate
    num_tracks = 6
    fig, axes = plt.subplots(
        num_tracks, 1, figsize=(16, 12), sharex=True, gridspec_kw={"hspace": 0.35}
    )
    plt.suptitle(f"{title} (Duration: {duration:.2f}s)", fontsize=14, fontweight="bold", y=0.98)

    time_axis = np.linspace(0, duration, len(audio_arr))

    # -------------------------------------------------------------
    # Track 1: Audio Waveform
    # -------------------------------------------------------------
    ax1 = axes[0]
    downsample_factor = max(1, len(audio_arr) // 10000)
    ax1.plot(
        time_axis[::downsample_factor],
        audio_arr[::downsample_factor],
        color="#3b82f6",
        linewidth=0.6,
        alpha=0.8,
    )
    ax1.set_ylabel("Amplitude", fontsize=9, fontweight="bold")
    ax1.set_title("Input Audio Waveform", fontsize=10, loc="left", fontweight="bold", color="#1e40af")
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.set_ylim(-1.05, 1.05)

    # -------------------------------------------------------------
    # Track 2: VAD (Voice Activity Detection)
    # -------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title("Step 1: Voice Activity Detection (VAD Segments)", fontsize=10, loc="left", fontweight="bold", color="#15803d")
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.grid(True, linestyle="--", alpha=0.4)

    if vad_segments:
        for seg in vad_segments:
            start = seg.get("start", 0.0)
            end = seg.get("end", start)
            rect = patches.Rectangle(
                (start, 0.15),
                end - start,
                0.7,
                linewidth=1,
                edgecolor="#166534",
                facecolor="#22c55e",
                alpha=0.65,
            )
            ax2.add_patch(rect)
            ax2.text(
                (start + end) / 2,
                0.5,
                f"{start:.1f}s - {end:.1f}s",
                ha="center",
                va="center",
                fontsize=8,
                color="#052e16",
                fontweight="bold",
            )
    else:
        ax2.text(duration / 2, 0.5, "No VAD segments / Fallback mode", ha="center", va="center", color="gray")

    # -------------------------------------------------------------
    # Track 3: Raw Whisper ASR Chunks
    # -------------------------------------------------------------
    ax3 = axes[2]
    ax3.set_title("Step 2: Whisper ASR Raw Chunks", fontsize=10, loc="left", fontweight="bold", color="#0369a1")
    ax3.set_ylim(0, 1)
    ax3.set_yticks([])
    ax3.grid(True, linestyle="--", alpha=0.4)

    if raw_asr_segments:
        for i, seg in enumerate(raw_asr_segments):
            start = seg.get("start", 0.0)
            end = seg.get("end", start)
            text = seg.get("text", "").strip()
            truncated_text = (text[:22] + "...") if len(text) > 22 else text
            rect = patches.Rectangle(
                (start, 0.15),
                end - start,
                0.7,
                linewidth=1,
                edgecolor="#075985",
                facecolor="#38bdf8",
                alpha=0.6,
            )
            ax3.add_patch(rect)
            ax3.text(
                (start + end) / 2,
                0.5,
                f'"{truncated_text}"',
                ha="center",
                va="center",
                fontsize=8,
                color="#082f49",
                fontweight="bold",
            )
    else:
        ax3.text(duration / 2, 0.5, "No ASR segments found", ha="center", va="center", color="gray")

    # -------------------------------------------------------------
    # Track 4: Word-Level Forced Alignment
    # -------------------------------------------------------------
    ax4 = axes[3]
    ax4.set_title("Step 3: Forced Alignment (Word-Level Timestamps)", fontsize=10, loc="left", fontweight="bold", color="#6b21a8")
    ax4.set_ylim(0, 1)
    ax4.set_yticks([])
    ax4.grid(True, linestyle="--", alpha=0.4)

    all_words = []
    if aligned_segments:
        for seg in aligned_segments:
            for w in seg.get("words", []):
                if "start" in w and "end" in w:
                    all_words.append(w)

    if all_words:
        for w in all_words:
            start = w["start"]
            end = w["end"]
            word_text = w.get("word", "")
            rect = patches.Rectangle(
                (start, 0.15),
                max(end - start, 0.04),
                0.7,
                linewidth=0.8,
                edgecolor="#581c87",
                facecolor="#c084fc",
                alpha=0.7,
            )
            ax4.add_patch(rect)
            if end - start > 0.12 or len(word_text) <= 4:
                ax4.text(
                    (start + end) / 2,
                    0.5,
                    word_text,
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="#3b0764",
                    rotation=0,
                )
    else:
        ax4.text(duration / 2, 0.5, "No word-level alignment data", ha="center", va="center", color="gray")

    # -------------------------------------------------------------
    # Track 5: Speaker Diarization Tracks
    # -------------------------------------------------------------
    ax5 = axes[4]
    ax5.set_title("Step 4: Pyannote Speaker Diarization Tracks", fontsize=10, loc="left", fontweight="bold", color="#9a3412")
    ax5.grid(True, linestyle="--", alpha=0.4)

    speaker_colors = {
        "SPEAKER_00": "#f97316",
        "SPEAKER_01": "#ec4899",
        "SPEAKER_02": "#14b8a6",
        "SPEAKER_03": "#8b5cf6",
        "SPEAKER_04": "#eab308",
    }

    detected_speakers = []
    if diarize_segments is not None:
        # Check if pandas DataFrame or dict or list
        if hasattr(diarize_segments, "iterrows"):
            for _, row in diarize_segments.iterrows():
                start = float(row.get("start", 0.0))
                end = float(row.get("end", start))
                spk = str(row.get("speaker", "SPEAKER_00"))
                if spk not in detected_speakers:
                    detected_speakers.append(spk)
                color = speaker_colors.get(spk, "#f97316")
                spk_idx = detected_speakers.index(spk)
                rect = patches.Rectangle(
                    (start, spk_idx * 0.4 + 0.1),
                    end - start,
                    0.3,
                    linewidth=1,
                    edgecolor="#7c2d12",
                    facecolor=color,
                    alpha=0.75,
                )
                ax5.add_patch(rect)
                ax5.text(
                    (start + end) / 2,
                    spk_idx * 0.4 + 0.25,
                    spk,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )
        elif isinstance(diarize_segments, list):
            for seg in diarize_segments:
                start = seg.get("start", 0.0)
                end = seg.get("end", start)
                spk = seg.get("speaker", "SPEAKER_00")
                if spk not in detected_speakers:
                    detected_speakers.append(spk)
                color = speaker_colors.get(spk, "#f97316")
                spk_idx = detected_speakers.index(spk)
                rect = patches.Rectangle(
                    (start, spk_idx * 0.4 + 0.1),
                    end - start,
                    0.3,
                    linewidth=1,
                    facecolor=color,
                    alpha=0.75,
                )
                ax5.add_patch(rect)

        ax5.set_ylim(0, max(len(detected_speakers) * 0.4 + 0.2, 1))
        ax5.set_yticks(
            [i * 0.4 + 0.25 for i in range(len(detected_speakers))],
            labels=detected_speakers if detected_speakers else [""],
            fontsize=8,
        )
    else:
        ax5.set_ylim(0, 1)
        ax5.set_yticks([])
        ax5.text(duration / 2, 0.5, "Diarization disabled / not run", ha="center", va="center", color="gray")

    # -------------------------------------------------------------
    # Track 6: Final Attributed Segments (Speaker + Text)
    # -------------------------------------------------------------
    ax6 = axes[5]
    ax6.set_title("Step 5: Final Result (Speaker-Attributed Subtitles)", fontsize=10, loc="left", fontweight="bold", color="#111827")
    ax6.set_ylim(0, 1)
    ax6.set_yticks([])
    ax6.grid(True, linestyle="--", alpha=0.4)
    ax6.set_xlabel("Time (seconds)", fontsize=10, fontweight="bold")

    if aligned_segments:
        for seg in aligned_segments:
            start = seg.get("start", 0.0)
            end = seg.get("end", start)
            spk = seg.get("speaker", "SPEAKER_00")
            text = seg.get("text", "").strip()
            color = speaker_colors.get(spk, "#3b82f6")
            rect = patches.Rectangle(
                (start, 0.15),
                end - start,
                0.7,
                linewidth=1.2,
                edgecolor="#1f2937",
                facecolor=color,
                alpha=0.8,
            )
            ax6.add_patch(rect)
            ax6.text(
                (start + end) / 2,
                0.5,
                f"[{spk}] {text[:28]}",
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )
    else:
        ax6.text(duration / 2, 0.5, "No final segments", ha="center", va="center", color="gray")

    ax6.set_xlim(0, max(duration, 0.1))

    # Save to image
    output_path = pathlib.Path(output_image_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=180, bbox_inches="tight")
    plt.close(fig)

    return str(output_path)
