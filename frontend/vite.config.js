import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 5173,
    host: true,
    allowedHosts: ['draftforge-2-1.onrender.com', 'localhost', '127.0.0.1']
  },
  preview: {
    port: process.env.PORT ? parseInt(process.env.PORT) : 3000,
    host: true,
    allowedHosts: ['draftforge-2-1.onrender.com', 'localhost', '127.0.0.1']
  }
});