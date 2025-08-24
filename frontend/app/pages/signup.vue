<script setup>
const supabase = useSupabaseClient();
const router = useRouter();

// Step control
const step = ref(1);

// Form data
const email = ref("");
const fullName = ref("");
const institutionName = ref("");
const jobTitle = ref("");
const password = ref("");
const confirmPassword = ref("");

// UI state
const loading = ref(false);
const errorMessage = ref(null);
const successMessage = ref(null);

// Job title options
const jobTitles = ["Registered Nurse", "Doctor", "Surgeon", "Admin Staff", "Technician"];

// Step 1: Email input
function handleEmailContinue() {
  if (email.value) {
    step.value = 2;
  }
  else {
    errorMessage.value = "Please enter a valid email address.";
  }
}

// Step 2: Full sign-up
async function handleSignUp() {
  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match.";
    return;
  }

  try {
    loading.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    // eslint-disable-next-line unused-imports/no-unused-vars
    const { data, error } = await supabase.auth.signUp({
      email: email.value,
      password: password.value,
      options: {
        data: {
          full_name: fullName.value,
          institution_name: institutionName.value,
          job_title: jobTitle.value,
        },
      },
    });

    if (error)
      throw error;

    successMessage.value = "Success! Please check your email to confirm your account.";

    // ✅ Wait 3 seconds so user can read the message
    setTimeout(() => {
      successMessage.value = null;
      router.push("/login");
    }, 3000);
  }
  catch (error) {
    if (error.message.includes("User already registered")) {
      successMessage.value = "This email is already registered. Redirecting to login...";
      setTimeout(() => {
        successMessage.value = null;
        router.push("/");
      }, 3000);
    }
    else {
      errorMessage.value = error.message;
    }
  }
  finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">
          MediSync
        </h1>
        <p class="text-gray-500 mt-2">
          Create an Account
        </p>
      </div>

      <!-- STEP 1: Email Form -->
      <form v-if="step === 1" @submit.prevent="handleEmailContinue">
        <div class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
              placeholder="you@example.com"
            >
          </div>
          <div>
            <button
              type="submit"
              class="w-full flex justify-center py-2 px-4 border rounded-md text-white bg-purple-600 hover:bg-purple-700"
            >
              Continue
            </button>
          </div>
        </div>
      </form>

      <!-- STEP 2: Personal Details Form -->
      <form v-if="step === 2" @submit.prevent="handleSignUp">
        <div class="space-y-4">
          <div>
            <label for="fullName" class="block text-sm font-medium text-gray-700">Full Name</label>
            <input
              id="fullName"
              v-model="fullName"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            >
          </div>

          <div>
            <label for="institutionName" class="block text-sm font-medium text-gray-700">Institution Name</label>
            <input
              id="institutionName"
              v-model="institutionName"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            >
          </div>

          <div>
            <label for="jobTitle" class="block text-sm font-medium text-gray-700">Job Title</label>
            <select
              id="jobTitle"
              v-model="jobTitle"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white"
            >
              <option disabled value="">
                Please select one
              </option>
              <option
                v-for="title in jobTitles"
                :key="title"
                :value="title"
              >
                {{ title }}
              </option>
            </select>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            >
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            >
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300"
            >
              {{ loading ? 'Signing Up...' : 'Sign Up' }}
            </button>
          </div>
        </div>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
        <p>{{ errorMessage }}</p>
      </div>

      <!-- Success Message -->
      <div v-if="successMessage" class="mt-4 text-center text-sm text-green-600">
        <p>{{ successMessage }}</p>
      </div>

      <!-- Back to Login -->
      <div class="mt-6 text-center text-sm text-gray-500">
        <p>
          Already have an account?
          <NuxtLink to="/" class="font-medium text-purple-600 hover:text-purple-500">
            Log in here
          </NuxtLink>
        </p>
      </div>
    </div>
  </div>
</template>
