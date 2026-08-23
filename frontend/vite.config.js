import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    allowedHosts: ['draftforge-2-1.onrender.com']
  },
  preview: {
    port: 3000,
    host: true,
    allowedHosts: ['draftforge-2-1.onrender.com']
  }
});