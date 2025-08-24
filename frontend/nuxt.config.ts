// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";

// eslint-disable-next-line node/no-process-env
const supabaseUrl = process.env.SUPABASE_URL;
// eslint-disable-next-line node/no-process-env
const supabaseKey = process.env.SUPABASE_ANON_KEY;

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
      supabaseUrl,
      supabaseKey,
    },
  },
  supabase: {
    url: supabaseUrl,
    key: supabaseKey,
    redirectOptions: {
      login: "/login", // Where to redirect guest users
      callback: "/index", // Where to redirect authenticated users
      exclude: ["/signup"], // Pages that don't require login
    },
  },
});
