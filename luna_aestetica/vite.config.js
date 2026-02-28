import { defineConfig } from 'vite'
import { nodePolyfills } from 'vite-plugin-node-polyfills'
import aurelia from '@aurelia/vite-plugin'
import babel from 'vite-plugin-babel'
import path from 'path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  server: {
    open: !process.env.CI,
    port: 9000,
  },
  esbuild: {
    target: 'es2022'
  },
  plugins: [
    aurelia({
      useDev: true,
      useInHtml: true 
    }),
    babel(),
    nodePolyfills(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})