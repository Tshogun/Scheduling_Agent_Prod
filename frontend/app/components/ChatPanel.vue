<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// Props to control visibility from the parent
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: true,
  },
});

// Emits to communicate back to the parent
const emit = defineEmits(['close']);

// --- State Management ---
const chatWidth = ref(450); // Initial width of the chat panel in pixels
const isResizing = ref(false);
const messages = ref([
  { id: 1, sender: 'ai', text: 'Hello! How can I help you with the schedule today?' }
]);
const newMessage = ref('');

// --- Resizing Logic ---
const handleMouseDown = (event) => {
  isResizing.value = true;
  // Add listeners to the whole window to track mouse movement everywhere
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('mouseup', handleMouseUp);
};

const handleMouseMove = (event) => {
  if (isResizing.value) {
    // Calculate new width based on mouse position from the right edge of the screen
    const newWidth = window.innerWidth - event.clientX;
    // Set boundaries for resizing
    if (newWidth > 300 && newWidth < 800) {
      chatWidth.value = newWidth;
    }
  }
};

const handleMouseUp = () => {
  isResizing.value = false;
  // IMPORTANT: Clean up the window event listeners
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('mouseup', handleMouseUp);
};

// --- Chat Logic ---
const sendMessage = () => {
  if (newMessage.value.trim() === '') return;
  // Add user message to the chat
  messages.value.push({ id: Date.now(), sender: 'user', text: newMessage.value });
  newMessage.value = '';
  // Here, your friend will later add the logic to send the message to an LLM
};

// Clean up listeners when the component is removed from the page
onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('mouseup', handleMouseUp);
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
    ></div>


    <!-- Chat Header -->
    <div class="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
      <h2 class="text-lg font-semibold text-gray-800">AI Assistant</h2>
      <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </div>

    <!-- Message Display Area -->
    <div class="flex-1 p-4 overflow-y-auto">
      <div class="space-y-4">
        <div v-for="message in messages" :key="message.id" class="flex" :class="message.sender === 'user' ? 'justify-end' : 'justify-start'">
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
      <form @submit.prevent="sendMessage" class="flex items-center space-x-2">
        <input 
          v-model="newMessage"
          type="text" 
          placeholder="Ask a question..."
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-purple-500 focus:border-purple-500"
        />
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
