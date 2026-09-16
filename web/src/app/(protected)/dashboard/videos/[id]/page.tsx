import { VideoDetailView } from "@/features/videos/components/video-detail-view";

interface PageProps {
  params: Promise<{
    id: string;
  }>;
}

export const metadata = {
  title: "Chi Tiết Video | ViralCopilot AI",
  description: "Toàn bộ thông tin trích xuất, phân vai người nói và kịch bản video.",
};

export default async function VideoDetailPage({ params }: PageProps) {
  const { id } = await params;

  return (
    <div className="flex-1 overflow-y-auto">
      <VideoDetailView videoId={id} />
    </div>
  );
}
