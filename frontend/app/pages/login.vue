<script setup>
// Get the Supabase client and router
const supabase = useSupabaseClient();
const router = useRouter();

// Refs for the form inputs
const email = ref("");
const password = ref("");
const errorMessage = ref(null);
const loading = ref(false);

// Function to handle the login process
async function handleLogin() {
  try {
    loading.value = true;
    errorMessage.value = null;

    // Use Supabase's signInWithPassword method
    const { error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });

    // If there's an error, display it
    if (error)
      throw error;

    // If login is successful, redirect to the scheduling page
    router.push("/");
  }
  catch (error) {
    errorMessage.value = error.message;
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
          Hi, Welcome Back!
        </p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin">
        <div class="space-y-6">
          <!-- Email Input -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              placeholder="you@example.com"
            >
          </div>

          <!-- Password Input -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-purple-500 focus:border-purple-500"
              placeholder="Your Password"
            >
          </div>

          <!-- Login Button -->
          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:bg-purple-300"
            >
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </div>
        </div>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
        <p>{{ errorMessage }}</p>
      </div>

      <!-- Sign Up Link -->
      <div class="mt-6 text-center text-sm text-gray-500">
        <p>
          New user?
          <NuxtLink to="/signup" class="font-medium text-purple-600 hover:text-purple-500">
            Click here to sign up
          </NuxtLink>
        </p>
      </div>
    </div>
  </div>
</template>
