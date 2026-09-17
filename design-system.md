# Markee Design System

This document is the source of truth for UI styling in this project. Any AI or developer building frontend screens must read this file before changing UI code.

The visual identity follows Markee: warm, bright, rounded, polished, AI-marketing focused. The interface should feel like a friendly operating desk for marketing teams and content creators, not a generic dark/cold SaaS dashboard.

## AI Implementation Checklist

Before coding any UI:

- Prefer warm orange primary colors, white cards, soft peach backgrounds, rounded pills, and soft shadows.
- Use `Plus Jakarta Sans` for headings and `Inter` for body text.
- Avoid purple/blue gradient-heavy UI unless the element is a secondary accent.
- Avoid flat gray admin UI. Operational screens can be dense, but must still use Markee's warm visual language.
- Do not introduce a new unrelated palette, font stack, card style, or button style.
- If building dashboards, internal tools, tables, forms, workflows, or cards, adapt this design system instead of inventing new styling.

## Brand Personality

ViralCopilot / Markee is:

- Warm and optimistic.
- AI-native but approachable.
- Video marketing-focused and action-oriented.
- Polished, bright, and modern.

It is not:

- Dark enterprise admin.
- Purple AI template.
- Plain Tailwind gray dashboard.
- Minimal to the point of feeling unfinished.

## Typography

Primary heading font:

```css
'Plus Jakarta Sans', sans-serif
```

Body font:

```css
'Inter', sans-serif
```

Use:

- `Plus Jakarta Sans` for H1, H2, large numbers, section titles, brand names, and strong dashboard labels.
- `Inter` for paragraphs, table cells, metadata, form labels, descriptions, and body text.
- Heavy heading weights: `700`, `800`, `900`.
- Body weights: `400`, `500`, `600`, `700`.

Recommended Tailwind snippets:

```tsx
className="[font-family:'Plus_Jakarta_Sans','Inter',sans-serif] font-black tracking-[-0.02em]"
```

```tsx
className="[font-family:'Inter','Segoe_UI',sans-serif] text-[#475569]"
```

## Color Tokens

Use these colors consistently.

### Primary Orange

| Token | Hex | Usage |
| --- | --- | --- |
| `primary` | `#ff7442` | Primary CTA, active nav, highlight text, brand accents |
| `primary-hover` | `#e6521e` | CTA hover, active text hover |
| `primary-mid` | `#ff8c64` | Gradient midpoint |
| `primary-end` | `#ffa382` | Logo gradient end |
| `primary-light` | `#fff0eb` | Badges, icon backgrounds, soft chips |
| `primary-lighter` | `#ffe4d9` | Hover backgrounds |
| `primary-subtle` | `#fffbf9` | Warm card/page fill |
| `primary-border` | `#ffe0d5` | Warm card borders |
| `primary-border-light` | `#ffe6dc` | Page frame borders |

### Yellow Accent

| Token | Hex | Usage |
| --- | --- | --- |
| `yellow` | `#ffd866` | AI highlights, warm indicator |
| `yellow-accent` | `#ffbd2e` | Gradient text end, warning accent |
| `yellow-light` | `#fef9c3` | Soft warning backgrounds |
| `yellow-dark` | `#d97706` | Warning text |

### Neutrals

| Token | Hex | Usage |
| --- | --- | --- |
| `dark` | `#0f172a` | Main text, dark cards |
| `text-dark` | `#101828` | Strong text |
| `gray` | `#475569` | Body text |
| `muted` | `#667085` | Secondary text |
| `slate-400` | `#94a3b8` | Metadata, disabled text |
| `slate-300` | `#cbd5e1` | Icons, light separators |
| `light-gray` | `#f8fafc` | Window headers, subtle table headers |
| `border-light` | `#f1f5f9` | Default card border |
| `border-medium` | `#e2e8f0` | Stronger border |
| `white-moly` | `#fffcfb` | Warm white page surface |

### Semantic Accents

| Token | Hex | Usage |
| --- | --- | --- |
| `success` | `#27c93f` | Positive status, window dot |
| `danger` | `#ff0000` | Critical status |
| `rose` | `#e1306c` | Social/TikTok-like accent, urgent but not destructive |
| `facebook-blue` | `#1877f2` | Facebook/channel accent |
| `twitter-blue` | `#1da1f2` | Informational secondary accent |
| `brown-dark` | `#432c24` | Dark warm card gradient |
| `brown-muted` | `#6a4f44` | Warm table header text |

## Gradients

Primary CTA:

```css
linear-gradient(90deg, #ff7442, #ff8c64)
```

Logo:

```css
linear-gradient(135deg, #ff7442, #ffa382)
```

Hero/page background:

```css
linear-gradient(135deg, #fff6f2 0%, #ffffff 48%, #ffeedd 100%)
```

Gradient text:

```css
linear-gradient(90deg, #ff7442 0%, #ffbd2e 100%)
```

Dark AI card:

```css
linear-gradient(135deg, #432c24, #0f172a)
```

## Page Structure

Use a warm framed shell for dashboard/internal product pages:

```tsx
<main className="min-h-screen bg-white text-[#0f172a] [font-family:'Inter','Segoe_UI',sans-serif]">
  <div className="bg-[linear-gradient(135deg,#fff6f2_0%,#ffffff_48%,#ffeedd_100%)] p-3 sm:p-5">
    <div className="mx-auto max-w-[1480px] rounded-[28px] border border-[#ffe6dc] bg-[#fffcfb]/95 p-3 shadow-[0_30px_80px_rgba(255,116,66,0.10)] sm:p-4 lg:p-5">
      {/* screen content */}
    </div>
  </div>
</main>
```

## Cards

Default card:

```tsx
className="rounded-[24px] border border-[#f1f5f9] bg-white p-5 shadow-[0_16px_38px_rgba(15,23,42,0.05)] text-[#0f172a]"
```

Stat card:

```tsx
className="rounded-[22px] border border-[#f1f5f9] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.04)] transition-transform hover:-translate-y-1"
```

Warm suggestion card:

```tsx
className="rounded-[20px] border border-[#ffe0d5] bg-[linear-gradient(135deg,#fff7f4,#ffffff)] p-4"
```

Dark AI card:

```tsx
className="rounded-[24px] border border-[#ffe0d5] bg-[linear-gradient(135deg,#432c24,#0f172a)] p-5 text-white shadow-[0_18px_42px_rgba(67,44,36,0.18)]"
```

## Buttons

Primary CTA:

```tsx
className="inline-flex items-center gap-2 rounded-full bg-[linear-gradient(90deg,#ff7442,#ff8c64)] px-5 py-3 text-sm font-black text-white shadow-[0_10px_25px_rgba(255,116,66,0.22)] transition-transform hover:-translate-y-0.5"
```

Secondary icon button:

```tsx
className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-[#ffe6dc] bg-white text-[#475569] shadow-[0_8px_20px_rgba(0,0,0,0.04)] hover:bg-[#fff7f4]"
```

Soft action:

```tsx
className="inline-flex items-center gap-2 rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-4 py-2 text-sm font-bold text-[#ff7442] hover:bg-[#ffe4d9]"
```

## Logo

```tsx
<div className="relative flex h-11 w-11 items-center justify-center rounded-full bg-[linear-gradient(135deg,#ff7442,#ffa382)] text-white font-black text-base shadow-[0_8px_20px_rgba(255,116,66,0.22)]">
  VC
  <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-white shadow-xs" />
</div>
```

Logo rules:
- Circular, not square.
- Orange gradient (`#ff7442` -> `#ffa382`).
- Small white dot in top-right.
- White text/mark inside.