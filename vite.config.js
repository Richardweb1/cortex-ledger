import { defineConfig } from 'vite'

export default defineConfig({
  root: 'public',
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: {
        main: './public/index.html',
        submit: './public/submit.html'
      }
    }
  },
  server: {
    port: 5173,
    open: true
  }
})