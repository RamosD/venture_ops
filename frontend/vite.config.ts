import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// Estratégia local: mesma origem via proxy de desenvolvimento (decisão de
// arranque §10). O frontend chama caminhos relativos `/api/...`; em dev, o Vite
// encaminha `/api` para o backend, evitando CORS. O alvo do backend é
// configurável (VITE_BACKEND_ORIGIN) para funcionar em Docker Compose
// (`http://backend:8000`); por defeito assume a porta Django convencional.
const backendOrigin = process.env.VITE_BACKEND_ORIGIN ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": {
        target: backendOrigin,
        // changeOrigin: false — preserva o Host do browser para que a
        // verificação de Origin do CSRF (Django) corresponda à origem real.
        changeOrigin: false,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/setupTests.ts",
    css: false,
  },
});
