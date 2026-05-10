import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const metamoTarget = env.VITE_METAMO_TARGET || 'http://localhost:8010'
  const plnragTarget = env.VITE_PLNRAG_TARGET || 'http://localhost:8001'

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/metamo': {
          target: metamoTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/metamo/, ''),
        },
        '/plnrag': {
          target: plnragTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/plnrag/, ''),
        },
      },
    },
  }
})
