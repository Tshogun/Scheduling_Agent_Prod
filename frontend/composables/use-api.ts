// frontend/composables/useApi.ts

export function useApi() {
  const config = useRuntimeConfig(); // Nuxt 3 will provide this automatically
  const baseURL = config.public.apiBase || "http://localhost:8080";

  const api = $fetch.create({
    baseURL: `${baseURL}/api/v1`,
    headers: {
      "Content-Type": "application/json",
    },
  });

  return {
    // Health check
    ping: () => api<{ message: string; timestamp: string }>("/ping"),

    // LLM completion
    getCompletion: (payload: {
      prompt: string;
      model?: string;
      max_tokens?: number;
    }) =>
      api<{
        completion: string;
        tokens_used: number;
        model: string;
      }>("/completion", {
        method: "POST",
        body: payload,
      }),

    // Optimization
    optimize: (payload: {
      problem_type: string;
      constraints_json: string;
      objectives_json: string;
      timeout_seconds?: number;
    }) =>
      api<{
        job_id: string;
        status: string;
        result: string;
      }>("/optimize", {
        method: "POST",
        body: payload,
      }),

    // Job status
    getJobStatus: (jobId: string) =>
      api<{
        job_id: string;
        status: string;
        result: string;
        error: string;
        created_at: number;
        completed_at: number;
      }>(`/job/${jobId}`),
  };
}
