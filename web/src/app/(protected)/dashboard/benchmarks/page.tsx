import { BenchmarkLibrary } from "@/features/benchmarks/components/benchmark-library";

export const metadata = {
  title: "Benchmark Library | ViralCopilot AI",
  description: "Kho video đối sánh triệu view từ pgvector và MinIO.",
};

export default function BenchmarksPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <BenchmarkLibrary />
    </div>
  );
}
