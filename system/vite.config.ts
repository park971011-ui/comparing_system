import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// repo 이름으로 변경 필요 (예: '/comparing_system/')
export default defineConfig({
  base: '/comparing_system/',
  plugins: [react()],
})
