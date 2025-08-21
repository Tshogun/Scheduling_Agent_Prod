<script setup>
import { computed, onMounted, ref } from "vue";

// Reactive data
const csvData = ref([]);
const employeeData = ref([]);
const loading = ref(true);
const error = ref(null);

// Load and parse CSV data
async function loadCsvData() {
  try {
    loading.value = true;
    console.log("Starting to load CSV files...");

    // Load shift data
    console.log("Fetching shifts.csv...");
    const shiftResponse = await fetch("/data/shifts.csv");
    console.log("Shift response status:", shiftResponse.status, shiftResponse.statusText);

    if (!shiftResponse.ok) {
      throw new Error(`Failed to load shifts.csv: ${shiftResponse.status} ${shiftResponse.statusText}`);
    }

    const shiftCsvText = await shiftResponse.text();
    console.log("Raw shift CSV text:", `${shiftCsvText.substring(0, 200)}...`);

    const shiftLines = shiftCsvText.trim().split("\n");
    const shiftHeaders = shiftLines[0].split(",").map(h => h.trim());
    console.log("Shift headers:", shiftHeaders);

    const shiftData = shiftLines.slice(1).map((line) => {
      const values = line.split(",");
      const row = {};
      shiftHeaders.forEach((header, index) => {
        row[header] = values[index]?.trim() || "";
      });
      return row;
    });

    csvData.value = shiftData;
    console.log("Parsed shift data:", shiftData);

    // Load employee data
    console.log("Fetching employees.csv...");
    const employeeResponse = await fetch("/data/employees.csv");
    console.log("Employee response status:", employeeResponse.status, employeeResponse.statusText);

    if (!employeeResponse.ok) {
      throw new Error(`Failed to load employees.csv: ${employeeResponse.status} ${employeeResponse.statusText}`);
    }

    const employeeCsvText = await employeeResponse.text();
    console.log("Raw employee CSV text:", `${employeeCsvText.substring(0, 200)}...`);

    const employeeLines = employeeCsvText.trim().split("\n");
    const employeeHeaders = employeeLines[0].split(",").map(h => h.trim());
    console.log("Employee headers:", employeeHeaders);

    const empData = employeeLines.slice(1).map((line) => {
      const values = line.split(",");
      const row = {};
      employeeHeaders.forEach((header, index) => {
        row[header] = values[index]?.trim() || "";
      });
      return row;
    });

    employeeData.value = empData;
    console.log("Parsed employee data:", empData);
    console.log("Unique dates from shifts:", [...new Set(shiftData.map(row => row.date))]);
    console.log("Employee preferences:", empData.map(emp => ({
      id: emp.employee_id,
      preferred: emp.preferred_shift_date,
      unavailable: emp.unavailable_shift_date,
    })));
  }
  catch (err) {
    error.value = `Failed to load CSV data: ${err.message}`;
    console.error("CSV loading error:", err);
  }
  finally {
    loading.value = false;
  }
}

// Computed properties for unique dates and employees
const uniqueDates = computed(() => {
  const dates = [...new Set(csvData.value.map(row => row.date))];
  return dates.sort();
});

const uniqueEmployees = computed(() => {
  const employeeMap = new Map();
  csvData.value.forEach((row) => {
    if (!employeeMap.has(row.employee_id)) {
      employeeMap.set(row.employee_id, {
        employee_id: row.employee_id,
        employee_name: row.employee_name,
        employee_initials: row.employee_initials,
      });
    }
  });
  return Array.from(employeeMap.values());
});

// Helper functions
function getEmployeeShift(employeeId, date) {
  return csvData.value.find(row =>
    row.employee_id === employeeId && row.date === date,
  );
}

function getEmployeePreferences(employeeId) {
  return employeeData.value.find(emp => emp.employee_id === employeeId) || {};
}

function isPreferred(employeeId, date) {
  const preferences = getEmployeePreferences(employeeId);
  const preferredDate = preferences.preferred_shift_date;
  console.log(`Checking preferred for ${employeeId} on ${date}, preferred date: ${preferredDate}`);
  return preferredDate === date;
}

function isUnavailable(employeeId, date) {
  const preferences = getEmployeePreferences(employeeId);
  const unavailableDate = preferences.unavailable_shift_date;
  console.log(`Checking unavailable for ${employeeId} on ${date}, unavailable date: ${unavailableDate}`);
  return unavailableDate === date;
}

function getEmployeeInitialsClass(employeeId) {
  // Generate consistent colors for each employee's initials
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

  // Use employee_id to get consistent color index
  const hash = employeeId.toString().split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

function getShiftClass(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  if (!shift)
    return "";

  const baseClasses = "text-white";
  const shiftType = shift.shift_type?.toLowerCase() || "";

  if (shiftType.includes("night")) {
    return `${baseClasses} bg-purple-700`;
  }
  else if (shiftType.includes("morning") || shiftType.includes("early")) {
    return `${baseClasses} bg-purple-500`;
  }
  else if (shiftType.includes("evening") || shiftType.includes("late")) {
    return `${baseClasses} bg-purple-600`;
  }
  else if (shiftType.includes("cleaning")) {
    return `${baseClasses} bg-purple-400`;
  }
  else {
    return `${baseClasses} bg-purple-500`;
  }
}

function getShiftStyle(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  if (!shift)
    return {};

  const time = shift.time || "00:00";
  const shiftType = shift.shift_type?.toLowerCase() || "";

  // Position based on time and shift type
  if (shiftType.includes("night") || time.startsWith("00:")) {
    return { left: "0%", width: "50%" }; // Night shift covers 00:00 to 12:00
  }
  else if (shiftType.includes("morning") || shiftType.includes("early")) {
    return { left: "0%", width: "50%" }; // Morning shift covers 00:00 to 12:00
  }
  else if (shiftType.includes("evening") || shiftType.includes("late")) {
    return { left: "50%", width: "50%" }; // Evening shift covers 12:00 to 24:00
  }
  else if (shiftType.includes("cleaning")) {
    return { left: "25%", width: "50%" }; // Cleaning covers 06:00 to 18:00
  }
  else {
    return { left: "0%", width: "100%" }; // Full day if unknown
  }
}

function getShiftText(employeeId, date) {
  const shift = getEmployeeShift(employeeId, date);
  const shiftType = shift?.shift_type || "";
  return shiftType.toUpperCase();
}

function formatDate(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
    });
  }
  catch {
    return dateStr;
  }
}

function formatDay(dateStr) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
    });
  }
  catch {
    return "";
  }
}

// Load data on component mount
onMounted(() => {
  loadCsvData();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 px-5 py-6">
    <div class="w-full max-w-none">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-8">
        <div class="flex items-center bg-purple-600 text-white px-4 py-2 rounded-full font-medium">
          <svg
            class="w-5 h-5 mr-2"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          EMPLOYEES
        </div>
        <div class="flex items-center text-purple-400 font-medium">
          <svg
            class="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
            />
            <polyline points="12,6 12,12 16,14" />
          </svg>
          SHIFT
        </div>
      </div>

      <!-- Schedule Container with Fixed Headers -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200">
        <!-- Scrollable Content Container -->
        <div class="h-[calc(100vh-150px)] overflow-auto">
          <div class="relative">
            <!-- Fixed Header Row -->
            <div class="flex border-b border-gray-200 bg-white sticky top-0 z-20">
              <!-- Fixed Employee Header -->
              <div class="flex-shrink-0 w-48 p-4 border-r border-gray-200 bg-white sticky left-0 z-30 font-semibold">
                Employee
              </div>

              <!-- Scrollable Date Headers -->
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
              <!-- Fixed Empty Cell -->
              <div class="flex-shrink-0 w-48 p-2 border-r border-gray-200 bg-gray-50 sticky left-0 z-20" />

              <!-- Scrollable Time Headers -->
              <div class="flex min-w-0">
                <div
                  v-for="date in uniqueDates"
                  :key="`time-${date}`"
                  class="flex-shrink-0 w-80 p-2 border-r border-gray-200 last:border-r-0 bg-gray-50"
                >
                  <div class="grid grid-cols-4 text-xs text-gray-400 text-center">
                    <span>00:00</span>
                    <span>06:00</span>
                    <span>12:00</span>
                    <span>18:00</span>
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
              <!-- Fixed Employee Info -->
              <div class="flex-shrink-0 w-48 p-4 border-r border-gray-200 bg-white sticky left-0 z-10">
                <div class="flex items-center">
                  <div :class="getEmployeeInitialsClass(employee.employee_id)" class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mr-3">
                    {{ employee.employee_initials }}
                  </div>
                  <span class="font-medium text-gray-900">{{ employee.employee_name }}</span>
                </div>
              </div>

              <!-- Schedule Cells -->
              <div class="flex min-w-0">
                <div
                  v-for="date in uniqueDates"
                  :key="`${employee.employee_id}-${date}`"
                  class="flex-shrink-0 w-80 border-r border-gray-200 last:border-r-0 relative"
                >
                  <div class="h-20 bg-gray-50 relative p-2">
                    <!-- Unavailable Full Day Block -->
                    <div
                      v-if="isUnavailable(employee.employee_id, date) && !getEmployeeShift(employee.employee_id, date)"
                      class="absolute inset-2 bg-red-100 border-l-4 border-red-500 rounded-r-lg flex items-center justify-center"
                    >
                      <span class="text-red-600 font-bold text-xs uppercase tracking-wide">UNAVAILABLE</span>
                    </div>

                    <!-- Preferred Full Day Block -->
                    <div
                      v-else-if="isPreferred(employee.employee_id, date) && !getEmployeeShift(employee.employee_id, date)"
                      class="absolute inset-2 bg-green-100 border-l-4 border-green-500 rounded-r-lg flex items-center justify-center"
                    >
                      <span class="text-green-600 font-bold text-xs uppercase tracking-wide">PREFERRED</span>
                    </div>

                    <!-- Time-based shift block with preference indicators -->
                    <div
                      v-if="getEmployeeShift(employee.employee_id, date)"
                      class="relative h-full"
                    >
                      <!-- Main shift block -->
                      <div
                        :class="getShiftClass(employee.employee_id, date)"
                        :style="getShiftStyle(employee.employee_id, date)"
                        class="absolute h-full flex items-center justify-center text-xs font-bold text-white rounded-lg shadow-sm"
                      >
                        {{ getShiftText(employee.employee_id, date) }}
                      </div>

                      <!-- Preferred indicator on shift -->
                      <div
                        v-if="isPreferred(employee.employee_id, date)"
                        class="absolute -top-1 -right-1 bg-green-100 border-l-4 border-green-500 rounded-r-lg px-2 py-1 z-10"
                      >
                        <span class="text-green-600 font-bold text-xs uppercase tracking-wide">PREFERRED</span>
                      </div>

                      <!-- Unavailable indicator on shift -->
                      <div
                        v-if="isUnavailable(employee.employee_id, date)"
                        class="absolute -top-1 -left-1 bg-red-100 border-l-4 border-red-500 rounded-r-lg px-2 py-1 z-10"
                      >
                        <span class="text-red-600 font-bold text-xs uppercase tracking-wide">UNAVAILABLE</span>
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
</template>

<style scoped>
/* Custom scrollbar for better UX */
.overflow-x-auto::-webkit-scrollbar,
.overflow-y-auto::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.overflow-x-auto::-webkit-scrollbar-track,
.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.overflow-x-auto::-webkit-scrollbar-thumb,
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover,
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
