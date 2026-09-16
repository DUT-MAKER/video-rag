import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: "/dashboard/ingestion",
        destination: "/dashboard/ingest",
        permanent: true,
      },
      {
        source: "/dashboard/sessions",
        destination: "/dashboard",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
