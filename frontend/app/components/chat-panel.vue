<script setup>
import { onUnmounted, ref } from "vue";

import { useApi } from "../../composables/use-api"; // Adjust path if needed

// Props from parent
// eslint-disable-next-line unused-imports/no-unused-vars
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(["close"]);

// State
const chatWidth = ref(450);
const isResizing = ref(false);
const messages = ref([
  {
    id: 1,
    sender: "ai",
    text: "Hello! How can I help you with the schedule today?",
  },
]);
const newMessage = ref("");
const isThinking = ref(false);

// API instance
const { getCompletion } = useApi();

// Resizing handlers
function handleMouseDown(_event) {
  isResizing.value = true;
  window.addEventListener("mousemove", handleMouseMove);
  window.addEventListener("mouseup", handleMouseUp);
}

function handleMouseMove(event) {
  if (isResizing.value) {
    const newWidth = window.innerWidth - event.clientX;
    if (newWidth > 300 && newWidth < 800) {
      chatWidth.value = newWidth;
    }
  }
}

function handleMouseUp() {
  isResizing.value = false;
  window.removeEventListener("mousemove", handleMouseMove);
  window.removeEventListener("mouseup", handleMouseUp);
}

// 🧠 Chat send handler
async function sendMessage() {
  const input = newMessage.value.trim();
  if (!input)
    return;

  const userMsg = {
    id: Date.now(),
    sender: "user",
    text: input,
  };

  messages.value.push(userMsg);
  newMessage.value = "";
  isThinking.value = true;

  try {
    const res = await getCompletion({
      prompt: input,
      // Optionally: model: "llama3-8b-8192", max_tokens: 300
    });

    messages.value.push({
      id: Date.now() + 1,
      sender: "ai",
      text: res.completion,
    });
  }
  catch (error) {
    console.error("AI error:", error);
    messages.value.push({
      id: Date.now() + 1,
      sender: "ai",
      text: "Sorry, something went wrong while generating a response.",
    });
  }
  finally {
    isThinking.value = false;
  }
}

onUnmounted(() => {
  window.removeEventListener("mousemove", handleMouseMove);
  window.removeEventListener("mouseup", handleMouseUp);
});
</script>

<template>
  <div
    v-if="isOpen"
    class="flex-shrink-0 bg-white border-l border-gray-200 shadow-lg flex flex-col relative"
    :style="{ width: `${chatWidth}px` }"
  >
    <!-- Draggable Handle -->
    <div
      class="w-2 h-full absolute top-0 left-0 cursor-col-resize z-50"
      @mousedown="handleMouseDown"
    />

    <!-- Chat Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
      <h2 class="text-lg font-semibold text-gray-800">
        AI Assistant
      </h2>
      <button class="text-gray-400 hover:text-gray-600" @click="emit('close')">
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        ><path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        /></svg>
      </button>
    </div>

    <!-- Message Display Area -->
    <div class="flex-1 p-4 overflow-y-auto">
      <div class="space-y-4">
        <div
          v-for="message in messages"
          :key="message.id"
          class="flex"
          :class="message.sender === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg"
            :class="message.sender === 'user' ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-800'"
          >
            <p>{{ message.text }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input Area -->
    <div class="p-4 border-t border-gray-200 flex-shrink-0">
      <form class="flex items-center space-x-2" @submit.prevent="sendMessage">
        <input
          v-model="newMessage"
          type="text"
          placeholder="Ask a question..."
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
        >
        <button
          type="submit"
          class="px-4 py-2 bg-purple-600 text-white font-semibold rounded-md hover:bg-purple-700"
        >
          Send
        </button>
      </form>
    </div>
  </div>
</template>
