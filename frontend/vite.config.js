import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

const webserver_port = (() => {
  try {
    return require('../../../sites/common_site_config.json').webserver_port
  } catch {
    return 8000
  }
})()

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '^/(app|api|assets|files|private)': {
        target: `http://127.0.0.1:${webserver_port}`,
        ws: true,
        router(req) {
          const site = req.headers.host.split(':')[0]
          return `http://${site}:${webserver_port}`
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: '../zoezy/public/frontend',
    emptyOutDir: true,
    target: 'es2015',
  },
  optimizeDeps: {
    include: ['frappe-ui > feather-icons', 'showdown', 'engine.io-client'],
  },
})
