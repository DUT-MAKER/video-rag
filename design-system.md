# Nocturne Design System (Next.js 16 & Tailwind CSS v4)

**Nocturne** là hệ thống thiết kế giao diện tối êm dịu, cô đọng (quiet, compact dark interface): nền xanh xám cận trung tính (`#161826`), kiểu chữ **Inter**, bo góc mềm `8px` (`rounded-lg`), và màu nhấn blurple (`#9184d9`) được sử dụng tinh tế dưới dạng đường nét (line) và phát sáng mờ (glow) thay vì đổ mảng màu đậm (flood).

Hệ thống được tích hợp đồng bộ vào frontend **Next.js 16 (App Router)**, **React 19**, **Tailwind CSS v4** và **Lucide React**.

---

## 1. Nguyên Tắc Cốt Lõi (Design Principles)

1. **Quiet & Desaturated Ground**:
   - Không sử dụng đen thuần (`#000000`) hay xám đơn điệu. Nền là xanh xám tối sâu (`#161826`), mang lại chiều sâu và giảm mỏi mắt khi làm việc lâu trong Studio.
   - Bề mặt (`surface`) được nâng cấp dần theo sắc độ OKLCH (`#1d2035` -> `#262a45`).
2. **Accent as Line & Glow, Never as a Flood**:
   - Màu nhấn Blurple (`#9184d9`) chỉ xuất hiện ở các chi tiết đắt giá: đường viền 1px, ánh sáng viền khi hover (`box-shadow: 0 0 12px rgba(145,132,217,0.25)`), `:focus-visible` ring và icon hành động.
   - Tuyệt đối không đổ nền đặc accent trên diện tích lớn (trừ các badge phân loại nhỏ hoặc banner đặc thù).
3. **Fading Rules & Asymmetry**:
   - Đường phân cách (dividers) không dừng đột ngột mà mờ dần về trong suốt ở hai đầu qua 48px (`.divider-fade`).
   - Bố cục ưu tiên căn trái, khoảng trắng thoáng đãng phía bên phải.
4. **Natural Image Blending (`.lighten`)**:
   - Toàn bộ ảnh thumbnail hoặc hình chụp nền tối được áp dụng `mix-blend-mode: lighten` qua lớp `.lighten` để hòa tan hoàn toàn nền đen của ảnh vào màu nền của giao diện.

---

## 2. Bảng Design Tokens (CSS Variables & Tailwind v4)

Khai báo tại [`web/src/app/globals.css`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/app/globals.css):

```css
@import "tailwindcss";

:root {
  /* Nocturne Base Ground & Surfaces */
  --background: #161826;       /* Nền xanh xám tối sâu */
  --foreground: #e9e9ed;       /* Văn bản chính sáng dịu */
  --surface: #1d2035;          /* Bề mặt panel, card, sidebar */
  --surface-hover: #262a45;    /* Trạng thái hover của bề mặt */
  --surface-elevated: #22263d; /* Container nổi (Modal, Dropdown) */
  --muted: #c5c7d5;            /* Văn bản thứ cấp */
  --muted-foreground: #9396aa; /* Nhãn phụ, placeholder, timestamp */
  --border: #2e3352;           /* Viền giao diện tiêu chuẩn */
  --border-subtle: #23273e;    /* Viền ngăn cách phụ */

  /* Nocturne Blurple Accent */
  --accent: #9184d9;           /* Sắc blurple đặc trưng của Nocturne */
  --accent-foreground: #ffffff;
  --primary: #9184d9;
  --primary-foreground: #161826;

  /* Domain-Specific Video RAG Accents */
  --accent-hook: #fb923c;      /* Cam: Phân tích Hook 3s đầu */
  --accent-ai: #9184d9;        /* Tím Nocturne: Tác vụ sinh kịch bản RAG */
  --accent-success: #34d399;   /* Xanh ngọc: Chỉ số Viral & Retention cao */
  --section: #20233b;          /* Nền phân đoạn nội dung đậm chất */
}
```

---

## 3. Kiểu Chữ (Typography) & Biểu Tượng (Icons)

### Kiểu chữ: Inter
Được nhúng trực tiếp qua `next/font/google` trong [`web/src/app/layout.tsx`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/app/layout.tsx):
- Tiêu đề (`headings`) và nội dung (`body`) đều sử dụng **Inter** với trọng số tối đa **font-semibold** (`500 - 600`), tránh dùng font quá đậm để giữ sự thanh lịch.
- Mã code, Timestamps kịch bản video, và Prompt JSON sử dụng class `.font-mono-code`:
  ```css
  .font-mono-code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }
  ```

### Biểu tượng: Lucide React
- Sử dụng **`lucide-react`** với stroke-width từ `1.5` đến `2`.
- Kích thước chuẩn: `w-3.5 h-3.5` hoặc `w-4 h-4` cho buttons/chips, `w-5 h-5` cho header navigation.

---

## 4. Danh Mục Thành Phần Giao Diện (Component Catalog)

### Nút Bấm ([`Button`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/components/ui/button.tsx))
Hành động chính (`primary`) trong Nocturne là **nút viền 1px accent phát sáng nhẹ**, không dùng nền đặc:

```tsx
// Nút Primary viền Accent chuẩn Nocturne
<Button variant="primary">
  <span>Tạo Kịch Bản</span>
</Button>

// Nút phụ (Secondary)
<Button variant="secondary">Hủy</Button>

// Nút Ghost
<Button variant="ghost">Chi tiết</Button>
```

- **Keyboard Focus chuẩn Nocturne**:
  ```css
  :focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
  ```

### Thẻ Nhãn ([`Badge`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/components/ui/badge.tsx))
- `variant="accent"` / `variant="ai"`: Viền `#9184d9/50`, nền `#9184d9/15`, chữ `#c5bdf0`.
- `variant="hook"`: Viền `orange-400/40`, nền `orange-500/10`, chữ `orange-200`.
- `variant="mono"`: Hiển thị thời lượng (`00:03 - 00:15`) hoặc tag nền tảng (`TikTok`, `Reels`).

### Thẻ Bề Mặt ([`Card`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/components/ui/card.tsx))
- Nền: `bg-[#1d2035]` (`--surface`).
- Viền: `border-[#2e3352]` (`--border`).
- Bo góc: `rounded-lg` (`8px`).

### Ô Nhập Liệu ([`Input`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/components/ui/input.tsx) & [`Textarea`](file:///Users/vuongngochau/Workplace/projects/rag-viral-video/web/src/components/ui/textarea.tsx))
- Nền: `bg-[#161826]`.
- Viền: `border-[#2e3352]`, focus kích hoạt viền `border-[#9184d9]` và ring `ring-[#9184d9]`.

---

## 5. Lớp Tiện Ích Đặc Thù Của Nocturne

### 1. Đường Kẻ Mờ Hai Đầu (`.divider-fade`)
Thay vì đường kẻ ngang cứng nhắc cắt đứt giao diện, Nocturne sử dụng hiệu ứng tan dần vào nền:
```html
<div className="divider-fade my-6 w-full" />
```

### 2. Hòa Tan Hình Ảnh (`.lighten`)
Bọc bất kỳ ảnh minh họa hoặc ảnh chụp mẫu nào để các sắc độ tối tự động hòa vào nền xanh xám của trang:
```html
<div className="lighten rounded-lg overflow-hidden">
  <img src="/thumbnail.jpg" alt="Preview" />
</div>
```

---

## 6. Quy Tắc Khi Phát Triển UI (Do & Don't)

### Do (Nên làm)
- Giữ sắc độ màu (chroma) thấp ở toàn bộ các phần nền và viền, chỉ để sắc tím blurple `#9184d9` và cam `#fb923c` đóng vai trò dẫn dắt thị giác.
- Sử dụng bo góc cố định `8px` (`rounded-lg`) để tạo sự gọn gàng, chặt chẽ cho giao diện studio chuyên nghiệp.
- Cho phép hiệu ứng `active:scale-[0.98]` khi click chuột để tăng phản hồi xúc giác.

### Don't (Không nên làm)
- Không dùng màu đen thuần `#000000` hoặc trắng gắt `#ffffff` làm nền các khối lớn.
- Không phủ màu tím đặc lên toàn bộ các nút bấm lớn gây chói và mất đi vẻ điềm tĩnh (quiet) của Nocturne.
- Không tăng `font-weight` của các tiêu đề vượt quá `600`; tạo sự phân cấp thông qua kích thước font chữ và khoảng cách (space).