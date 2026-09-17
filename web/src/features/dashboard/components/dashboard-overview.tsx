import { Card } from "@/components/ui/card";
import { Sparkles, Video, Database, CheckCircle2 } from "lucide-react";

const stats = [
  { label: "Active Pipelines", value: "4", icon: Sparkles, color: "text-[#ff7442]", bg: "bg-[#fff0eb]" },
  { label: "Indexed Viral Videos", value: "1,248", icon: Video, color: "text-blue-500", bg: "bg-blue-50" },
  { label: "pgvector Index Health", value: "Optimal", icon: Database, color: "text-emerald-600", bg: "bg-emerald-50" },
];

export function DashboardOverview() {
  return (
    <section className="space-y-6">
      <div className="border-b border-[#ffe6dc] pb-5">
        <h1 className="font-heading text-3xl font-extrabold tracking-tight text-[#0f172a]">
          Bảng Điều Khiển Tổng Quan
        </h1>
        <p className="mt-2 text-xs text-[#667085]">
          Theo dõi trạng thái các module RAG, vector database và quy trình sản xuất nội dung viral video.
        </p>
      </div>
      <div className="grid gap-5 md:grid-cols-3">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card
              key={stat.label}
              className="rounded-[22px] border-[#f1f5f9] bg-white p-6 shadow-xs transition-all hover:-translate-y-1 hover:border-[#ffe0d5] hover:shadow-md"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold uppercase tracking-wider text-[#667085]">
                  {stat.label}
                </p>
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${stat.bg} ${stat.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <p className="mt-4 font-heading text-3xl font-extrabold text-[#0f172a]">
                {stat.value}
              </p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
