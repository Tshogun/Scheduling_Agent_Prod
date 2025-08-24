<script setup>
import { computed, onMounted, ref } from "vue";

// CHANGE 1: Import the new ChatPanel component we just created.
import ChatPanel from "~/components/chat-panel.vue";

// CHANGE 2: Add a new reactive variable to control the chat's visibility.
const isChatOpen = ref(true); // The chat will be open by default.

// Reactive data
const csvData = ref([]);
const employeeData = ref([]);
const loading = ref(true);
const error = ref(null);

// Load and parse CSV data (This logic remains exactly the same)
async function loadCsvData() {
  try {
    loading.value = true;
    const shiftResponse = await fetch("/data/shifts.csv");
    if (!shiftResponse.ok) {
      throw new Error(`Failed to load shifts.csv: ${shiftResponse.status} ${shiftResponse.statusText}`);
    }
    const shiftCsvText = await shiftResponse.text();
    const shiftLines = shiftCsvText.trim().split("\n");
    const shiftHeaders = shiftLines[0].split(",").map(h => h.trim());
    const shiftData = shiftLines.slice(1).map((line) => {
      const values = line.split(",");
      const row = {};
      shiftHeaders.forEach((header, index) => {
        row[header] = values[index]?.trim() || "";
      });
      return row;
    });
    csvData.value = shiftData;
    const employeeResponse = await fetch("/data/employees.csv");
    if (!employeeResponse.ok) {
      throw new Error(`Failed to load employees.csv: ${employeeResponse.status} ${employeeResponse.statusText}`);
    }
    const employeeCsvText = await employeeResponse.text();
    const employeeLines = employeeCsvText.trim().split("\n");
    const employeeHeaders = employeeLines[0].split(",").map(h => h.trim());
    const empData = employeeLines.slice(1).map((line) => {
      const values = line.split(",");
      const row = {};
      employeeHeaders.forEach((header, index) => {
        row[header] = values[index]?.trim() || "";
      });
      return row;
    });
    employeeData.value = empData;
  }
  catch (err) {
    error.value = `Failed to load CSV data: ${err.message}`;
  }
  finally {
    loading.value = false;
  }
}

const uniqueDates = computed(() => {
  const dates = [...new Set(csvData.value.map(row => row.date))];
  return dates.sort();
});
const uniqueEmployees = computed(() => {
  const employeeMap = new Map();
  csvData.value.forEach((row) => {
    if (row.employee_id && !employeeMap.has(row.employee_id)) {
      employeeMap.set(row.employee_id, {
        employee_id: row.employee_id,
        employee_name: row.employee_name,
        employee_initials: row.employee_initials,
      });
    }
  });
  return Array.from(employeeMap.values());
});

function getEmployeeShift(employeeId, date) {
  return csvData.value.find(row => row.employee_id === employeeId && row.date === date);
}
function getEmployeePreferences(employeeId) {
  return employeeData.value.find(emp => emp.employee_id === employeeId) || {};
}
function isPreferred(employeeId, date) {
  const preferences = getEmployeePreferences(employeeId);
  return preferences.preferred_shift_date === date;
}
function isUnavailable(employeeId, date) {
  const preferences = getEmployeePreferences(employeeId);
  return preferences.unavailable_shift_date === date;
}
function getEmployeeInitialsClass(employeeId) {
  const colors = [
    "bg-purple-100 text-purple-600",
    "bg-blue-100 text-blue-600",
    "bg-green-100 text-green-600",
    "bg-yellow-100 text-yellow-600",
    "bg-red-100 text-red-600",
    "bg-indigo-100 text-indigo-600",
    "bg-pink-100 text-pink-600",
    "bg-teal-100 text-teal-600",
    "bg-orange-100 text-orange-600",
    "bg-cyan-100 text-cyan-600",
  ];
  const hash = String(employeeId).split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}
function getShiftClass(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  if (!shift)
    return "";
  const baseClasses = "text-white";
  const shiftType = shift.shift_type?.toLowerCase() || "";
  if (shiftType.includes("night"))
    return `${baseClasses} bg-purple-900`;
  if (shiftType.includes("morning") || shiftType.includes("early"))
    return `${baseClasses} bg-purple-700`;
  if (shiftType.includes("evening") || shiftType.includes("late"))
    return `${baseClasses} bg-purple-500`;
  if (shiftType.includes("cleaning"))
    return `${baseClasses} bg-purple-400`;
  return `${baseClasses} bg-purple-500`;
}
function getShiftStyle(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  if (!shift)
    return {};
  // eslint-disable-next-line unused-imports/no-unused-vars
  const time = shift.time || "00:00";
  const shiftType = shift.shift_type?.toLowerCase() || "";
  if (shiftType.includes("night"))
    return { left: "0%", width: "33.33%" };
  if (shiftType.includes("morning") || shiftType.includes("early"))
    return { left: "33.33%", width: "33.33%" };
  if (shiftType.includes("evening") || shiftType.includes("late"))
    return { left: "66.66%", width: "33.33%" };
  if (shiftType.includes("cleaning"))
    return { left: "25%", width: "50%" };
  return { left: "0%", width: "100%" };
}
function getShiftText(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  return shift?.shift_type?.toUpperCase() || "";
}
function formatDate(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "long", day: "numeric" });
  }
  catch { return dateStr; }
}
function formatDay(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { weekday: "long" });
  }
  catch { return ""; }
}
onMounted(() => {
  loadCsvData();
});
</script>

<template>
  <!-- CHANGE 3: The main container is now a flexbox to hold the schedule and chat side-by-side. -->
  <div class="flex h-screen w-screen overflow-hidden">
    <!-- This is your original scheduling UI. It will now shrink and grow to make room for the chat. -->
    <div class="flex-1 min-h-screen bg-gray-50 px-5 py-6 overflow-auto">
      <div class="w-full max-w-none">
        <!-- Header -->
        <div class="flex items-center justify-between gap-4 mb-8">
          <div class="flex items-center">
            <div class="flex items-center bg-purple-600 text-white px-4 py-2 rounded-full font-medium">
              <svg
                class="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              ><circle
                cx="12"
                cy="12"
                r="10"
              /><polyline points="12,6 12,12 16,14" /></svg>
              SCHEDULE SHIFT
            </div>
            <div class="flex items-center text-purple-400 font-medium ml-4">
              <svg
                class="w-5 h-5 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              ><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              EMPLOYEES
            </div>
          </div>
          <!-- CHANGE 4: This is the button to re-open the chat panel when it's closed. -->
          <button
            v-if="!isChatOpen"
            class="p-2 rounded-full bg-purple-600 text-white hover:bg-purple-700"
            @click="isChatOpen = true"
          >
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
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            /></svg>
          </button>
        </div>

        <!-- Your original schedule container -->
        <div class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
          <div class="h-[calc(100vh-150px)] overflow-auto">
            <div class="relative">
              <!-- Fixed Header Row -->
              <div class="flex border-b border-gray-200 bg-white sticky top-0 z-20">
                <div class="flex flex-shrink-0 w-48 p-4 border-r border-gray-200 bg-white justify-center items-center sticky left-0 z-30 font-semibold">
                  Employees
                </div>
                <div class="flex min-w-0">
                  <div
                    v-for="date in uniqueDates"
                    :key="date"
                    class="flex-shrink-0 w-80 p-4 text-center border-r border-gray-200 last:border-r-0 bg-white"
                  >
                    <div class="text-sm text-gray-500 mb-1">
                      {{ formatDay(date) }}
                    </div>
                    <div class="font-semibold text-gray-900">
                      {{ formatDate(date) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Fixed Time Headers -->
              <div class="flex border-b border-gray-300 bg-gray-50 sticky top-16 z-10">
                <div class="flex-shrink-0 w-48 p-2 border-r border-gray-200 bg-gray-50 sticky left-0 z-20" />
                <div class="flex min-w-0">
                  <div
                    v-for="date in uniqueDates"
                    :key="`time-${date}`"
                    class="flex-shrink-0 w-80 p-2 border-r border-gray-200 last:border-r-0 bg-gray-50"
                  >
                    <div class="grid grid-cols-4 text-xs text-gray-400 text-center">
                      <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Employee Rows -->
              <div
                v-for="employee in uniqueEmployees"
                :key="employee.employee_id"
                class="flex border-b border-gray-200 last:border-b-0 hover:bg-gray-50"
              >
                <div class="flex-shrink-0 w-48 p-4 border-r border-gray-200 bg-white sticky left-0 z-10">
                  <div class="flex items-center">
                    <div :class="getEmployeeInitialsClass(employee.employee_id)" class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mr-3">
                      {{ employee.employee_initials }}
                    </div>
                    <span class="font-medium text-gray-900">{{ employee.employee_name }}</span>
                  </div>
                </div>
                <div class="flex min-w-0">
                  <div
                    v-for="date in uniqueDates"
                    :key="`${employee.employee_id}-${date}`"
                    class="flex-shrink-0 w-80 border-r border-gray-200 last:border-r-0 relative"
                  >
                    <div class="h-20 bg-gray-50 relative p-2">
                      <div v-if="isUnavailable(employee.employee_id, date) && !getEmployeeShift(employee.employee_id, date)" class="absolute inset-2 bg-red-100 border-l-4 border-red-500 rounded-r-lg flex items-center justify-center">
                        <span class="text-red-600 font-bold text-xs uppercase tracking-wide">UNAVAILABLE</span>
                      </div>
                      <div v-else-if="isPreferred(employee.employee_id, date) && !getEmployeeShift(employee.employee_id, date)" class="absolute inset-2 bg-green-100 border-l-4 border-green-500 rounded-r-lg flex items-center justify-center">
                        <span class="text-green-600 font-bold text-xs uppercase tracking-wide">PREFERRED</span>
                      </div>
                      <div v-if="getEmployeeShift(employee.employee_id, date)" class="relative h-full">
                        <div
                          :class="getShiftClass(employee.employee_id, date)"
                          :style="getShiftStyle(employee.employee_id, date)"
                          class="absolute h-full flex items-center justify-center text-xs font-bold text-white rounded-lg shadow-sm"
                        >
                          {{ getShiftText(employee.employee_id, date) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CHANGE 5: This is our new chat panel component.
         - :isOpen="isChatOpen" connects its visibility to our variable.
         - @close="isChatOpen = false" listens for the close event from the panel and updates our variable.
    -->
    <ChatPanel :is-open="isChatOpen" @close="isChatOpen = false" />
  </div>
</template>

<style scoped>
/* Custom scrollbar styles remain the same */
.overflow-auto::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}
.overflow-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}
.overflow-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
