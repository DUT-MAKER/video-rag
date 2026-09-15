import { Card } from "@/components/ui/card";

const stats = [
  { label: "Active modules", value: "4" },
  { label: "Open tasks", value: "12" },
  { label: "API status", value: "Ready" },
];

export function DashboardOverview() {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-slate-950">Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600">
          Replace this overview with the first real feature of your project.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map((stat) => (
          <Card key={stat.label} className="p-5">
            <p className="text-sm font-medium text-slate-500">{stat.label}</p>
            <p className="mt-3 text-2xl font-semibold text-slate-950">
              {stat.value}
            </p>
          </Card>
        ))}
      </div>
    </section>
  );
}
