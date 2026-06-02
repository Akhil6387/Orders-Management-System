// vite.config.js – merge this test block into your existing vite.config.js

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  // ── Dev proxy (existing) ──────────────────────────────────────────────────
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },

  // ── Test configuration ────────────────────────────────────────────────────
  test: {
    // Use jsdom so DOM APIs are available in Node
    environment: "jsdom",

    // Import jest-dom matchers globally (toBeInTheDocument, etc.)
    setupFiles: ["./src/__tests__/setup.js"],

    // Code coverage via c8
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      reportsDirectory: "./coverage",
      include: ["src/**/*.{js,jsx}"],
      exclude: [
        "src/main.jsx",
        "src/__tests__/**",
        "src/**/*.test.{js,jsx}",
        "src/**/__mocks__/**",
      ],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 60,
        statements: 70,
      },
    },

    // Glob for test files
    include: ["src/**/*.{test,spec}.{js,jsx}"],

    // Suppress noisy React act() warnings in test output
    globals: true,
  },
});
