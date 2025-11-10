/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  
  // 性能优化
  compress: true,  // 启用gzip压缩
  
  // 图片优化
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },
  
  // 编译优化
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',  // 生产环境移除console
  },
  
  // 实验性功能
  experimental: {
    // optimizeCss: true,  // CSS优化 - 暂时禁用，需要额外依赖
    optimizePackageImports: ['lucide-react'],  // 优化包导入
  },
  
  // 环境变量
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
  },
  
  // Webpack优化
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // 减小客户端bundle大小
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          default: false,
          vendors: false,
          commons: {
            name: 'commons',
            chunks: 'all',
            minChunks: 2,
          },
        },
      }
    }
    return config
  },
}

module.exports = nextConfig

