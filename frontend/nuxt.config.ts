// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  vite: {
    plugins: [
      tailwindcss(),
      tsconfigPaths(),
    ],
  },
  css: ["../assets/css/main.css"],
  modules: ["@nuxt/eslint", "@nuxt/image", "@nuxt/ui", "@nuxt/test-utils", "@nuxtjs/supabase"],
  eslint: {
    config: {
      standalone: false,
    },
  },
  runtimeConfig: {
    public: {
      // eslint-disable-next-line node/no-process-env
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8080",
      supabase: { // eslint-disable-next-line node/no-process-env
        url: process.env.SUPABASE_URL,
        // eslint-disable-next-line node/no-process-env
        key: process.env.SUPABASE_KEY,
      },
    },
  },
  supabase: {
    redirectOptions: {
      login: "/login", // Where to redirect guest users
      callback: "/index", // Where to redirect authenticated users
      exclude: ["/signup"], // Pages that don't require login
    },
  },
});
