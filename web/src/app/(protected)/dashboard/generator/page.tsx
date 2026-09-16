import { ScriptGeneratorForm } from "@/features/generator/components/script-generator-form";

export const metadata = {
  title: "1-Click Generator | ViralCopilot AI",
  description: "Sinh kịch bản video ngắn triệu view chỉ với 1 click.",
};

export default function GeneratorPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <ScriptGeneratorForm />
    </div>
  );
}
