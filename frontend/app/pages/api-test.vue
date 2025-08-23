// frontend/pages/index.vue
<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { useApi } from "../composables/use-api";

const router = useRouter();

function goBack() {
  router.back();
}

const api = useApi();

// Health check
const healthLoading = ref(false);
const healthResult = ref(null);

async function checkHealth() {
  healthLoading.value = true;
  try {
    const response = await $fetch("http://localhost:8080/health");
    healthResult.value = response;
  }
  catch (error) {
    healthResult.value = { error: error.message };
  }
  finally {
    healthLoading.value = false;
  }
}

// Ping
const pingLoading = ref(false);
const pingResult = ref(null);

async function pingService() {
  pingLoading.value = true;
  try {
    const response = await api.ping();
    pingResult.value = response;
  }
  catch (error) {
    pingResult.value = { message: `Error: ${error.message}` };
  }
  finally {
    pingLoading.value = false;
  }
}

// Completion
const prompt = ref("Write a haiku about coding");
const completionLoading = ref(false);
const completionResult = ref(null);

async function testCompletion() {
  completionLoading.value = true;
  try {
    const response = await api.getCompletion({
      prompt: prompt.value,
      model: "test-model",
      max_tokens: 100,
    });
    completionResult.value = response;
  }
  catch (error) {
    completionResult.value = { completion: `Error: ${error.message}` };
  }
  finally {
    completionLoading.value = false;
  }
}

// Optimization
const optimizationInput = ref({
  problem_type: "linear_programming",
  constraints_json: "{\"x + y\": \"<=10\", \"x\": \">=0\", \"y\": \">=0\"}",
  objectives_json: "{\"maximize\": \"2x + 3y\"}",
  timeout_seconds: 30,
});
const optimizationLoading = ref(false);
const currentJob = ref(null);

async function testOptimization() {
  optimizationLoading.value = true;
  try {
    const response = await api.optimize({
      problem_type: optimizationInput.value.problem_type,
      constraints_json: optimizationInput.value.constraints_json,
      objectives_json: optimizationInput.value.objectives_json,
      timeout_seconds: Number.parseInt(optimizationInput.value.timeout_seconds),
    });
    currentJob.value = response;

    // Poll for updates
    pollJobStatus();
  }
  catch (error) {
    currentJob.value = { error: error.message };
  }
  finally {
    optimizationLoading.value = false;
  }
}

async function refreshJobStatus() {
  if (!currentJob.value?.job_id)
    return;

  try {
    const response = await api.getJobStatus(currentJob.value.job_id);
    currentJob.value = response;
  }
  catch (error) {
    console.error("Failed to refresh job status:", error);
  }
}

function pollJobStatus() {
  const interval = setInterval(async () => {
    if (!currentJob.value?.job_id) {
      clearInterval(interval);
      return;
    }

    await refreshJobStatus();

    if (["completed", "failed"].includes(currentJob.value.status)) {
      clearInterval(interval);
    }
  }, 2000);
}

// Initialize
onMounted(() => {
  checkHealth();
});
</script>

<template>
  <div class="container mx-auto p-6">
    <div class="mb-6">
      <button
        class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        @click="goBack"
      >
        ← Back
      </button>
    </div>

    <h1 class="text-3xl font-bold mb-8">
      Local Development Test
    </h1>

    <!-- Service Status -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="border rounded-lg p-4">
        <h2 class="text-xl font-semibold mb-4">
          Service Health
        </h2>
        <button
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          :disabled="healthLoading"
          @click="checkHealth"
        >
          {{ healthLoading ? 'Checking...' : 'Check Health' }}
        </button>
        <pre v-if="healthResult" class="mt-4 bg-gray-100 p-3 rounded text-sm">{{ JSON.stringify(healthResult, null, 2) }}</pre>
      </div>

      <div class="border rounded-lg p-4">
        <h2 class="text-xl font-semibold mb-4">
          Quick Ping
        </h2>
        <button
          class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          :disabled="pingLoading"
          @click="pingService"
        >
          {{ pingLoading ? 'Pinging...' : 'Ping Service' }}
        </button>
        <p v-if="pingResult" class="mt-4 text-sm">
          {{ pingResult.message }}
        </p>
      </div>
    </div>

    <!-- LLM Completion Test -->
    <div class="border rounded-lg p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4">
        LLM Completion Test
      </h2>
      <div class="space-y-4">
        <textarea
          v-model="prompt"
          placeholder="Enter your prompt here..."
          class="w-full p-3 border rounded-lg h-24 resize-none"
        />
        <button
          class="bg-purple-500 text-white px-6 py-2 rounded hover:bg-purple-600"
          :disabled="completionLoading || !prompt.trim()"
          @click="testCompletion"
        >
          {{ completionLoading ? 'Generating...' : 'Get Completion' }}
        </button>
        <div v-if="completionResult" class="bg-gray-50 p-4 rounded-lg">
          <h3 class="font-semibold mb-2">
            Response:
          </h3>
          <p class="mb-2">
            {{ completionResult.completion }}
          </p>
          <small class="text-gray-600">
            Model: {{ completionResult.model }} | Tokens: {{ completionResult.tokens_used }}
          </small>
        </div>
      </div>
    </div>

    <!-- Optimization Test -->
    <div class="border rounded-lg p-6">
      <h2 class="text-xl font-semibold mb-4">
        Optimization Test
      </h2>
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            v-model="optimizationInput.problem_type"
            placeholder="Problem type (e.g., linear_programming)"
            class="p-3 border rounded-lg"
          >
          <input
            v-model="optimizationInput.timeout_seconds"
            type="number"
            placeholder="Timeout (seconds)"
            class="p-3 border rounded-lg"
          >
        </div>
        <textarea
          v-model="optimizationInput.constraints_json"
          placeholder="Constraints JSON (e.g., {&quot;x + y&quot;: &quot;<=10&quot;})"
          class="w-full p-3 border rounded-lg h-20 resize-none"
        />
        <textarea
          v-model="optimizationInput.objectives_json"
          placeholder="Objectives JSON (e.g., {&quot;maximize&quot;: &quot;2x + 3y&quot;})"
          class="w-full p-3 border rounded-lg h-20 resize-none"
        />
        <button
          class="bg-orange-500 text-white px-6 py-2 rounded hover:bg-orange-600"
          :disabled="optimizationLoading"
          @click="testOptimization"
        >
          {{ optimizationLoading ? 'Solving...' : 'Start Optimization' }}
        </button>

        <!-- Job Status -->
        <div v-if="currentJob" class="bg-blue-50 p-4 rounded-lg">
          <h3 class="font-semibold mb-2">
            Job Status
          </h3>
          <p><strong>ID:</strong> {{ currentJob.job_id }}</p>
          <p>
            <strong>Status:</strong>
            <span
              :class="{
                'text-yellow-600': currentJob.status === 'queued',
                'text-blue-600': currentJob.status === 'running',
                'text-green-600': currentJob.status === 'completed',
                'text-red-600': currentJob.status === 'failed',
              }"
            >
              {{ currentJob.status }}
            </span>
          </p>
          <button
            class="mt-2 bg-blue-500 text-white px-4 py-1 text-sm rounded hover:bg-blue-600"
            @click="refreshJobStatus"
          >
            Refresh Status
          </button>
          <pre v-if="currentJob.result" class="mt-4 bg-gray-100 p-3 rounded text-sm">{{ currentJob.result }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>
