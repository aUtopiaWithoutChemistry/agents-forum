import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker中使用Node.js服务器，不需要静态导出
  // 但保留配置以备后用
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

export default nextConfig;
