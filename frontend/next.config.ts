import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "5000",
        pathname: "/imagenes_reportes/**",
      },
    ],
  },
  async rewrites() {
    const backendOrigin = process.env.BACKEND_API_ORIGIN || "http://localhost:5000";

    return [
      {
        source: "/backend/:path*",
        destination: `${backendOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
