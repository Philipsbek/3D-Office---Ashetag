import type { NextConfig } from 'next'
import path from 'node:path'

const nextConfig: NextConfig = {
  // keep Turbopack rooted in this folder (a stray lockfile higher up confuses it)
  turbopack: { root: path.resolve(__dirname) },
}

export default nextConfig
