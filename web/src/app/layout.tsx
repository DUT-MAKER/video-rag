import type { Metadata } from "next";
import NextTopLoader from "nextjs-toploader";
import Providers from "./providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "ViralCopilot — RAG Viral Video Studio",
  description:
    "AI-powered viral video storyboard and script engineering studio.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
      suppressHydrationWarning
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-full bg-white text-[#0f172a]" suppressHydrationWarning>
        <NextTopLoader color="#ff7442" height={3} showSpinner={false} />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

