import { VideoManagementList } from "@/features/videos/components/video-management-list";

export const metadata = {
  title: "Quản Lý Dữ Liệu Video | ViralCopilot AI",
  description: "Danh sách và quản lý toàn bộ các video đã được trích xuất AI và lưu trữ trong pgvector.",
};

export default function VideosPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <VideoManagementList />
    </div>
  );
}
