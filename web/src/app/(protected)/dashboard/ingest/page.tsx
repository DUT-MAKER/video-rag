import { IngestHub } from "@/features/ingest/components/ingest-hub";

export const metadata = {
  title: "Knowledge Ingest | ViralCopilot AI",
  description: "Nạp và vector hóa dữ liệu video vào PostgreSQL pgvector.",
};

export default function IngestPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <IngestHub />
    </div>
  );
}
