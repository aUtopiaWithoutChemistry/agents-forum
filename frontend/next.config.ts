import type { NextConfig } from "next";

const internalApiUrl = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  env: {
    // Keep client requests same-origin by default, then proxy /api on server.
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "",
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${internalApiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
