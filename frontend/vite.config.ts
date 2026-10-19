import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath, URL } from "node:url";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

const copyMapWorker = () => {
  const destination = resolve("public/maplibre-gl-worker.mjs");
  mkdirSync(resolve("public"), { recursive: true });
  copyFileSync(resolve("node_modules/maplibre-gl/dist/maplibre-gl-worker.mjs"), destination);
};

const maplibreWorker = (): Plugin => ({
  name: "maplibre-worker",
  buildStart: copyMapWorker,
  configureServer(server) {
    copyMapWorker();
    const workerPath = resolve("public/maplibre-gl-worker.mjs");
    server.middlewares.use((req, res, next) => {
      const url = req.url?.split("?")[0];
      if (url !== "/maplibre-gl-worker.mjs") {
        next();
        return;
      }
      res.setHeader("Content-Type", "text/javascript");
      res.end(readFileSync(workerPath));
    });
  },
});

export default defineConfig({
  tsconfig: "./tsconfig.app.json",
  plugins: [react(), tailwindcss(), maplibreWorker()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
    tsconfigPaths: true,
  },
  envDir: "..",
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
