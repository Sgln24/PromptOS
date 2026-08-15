import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        // Change this from 8001 to 8002
        destination: "http://backend:8002/api/:path*", 
      },
    ];
  },
};

export default nextConfig;