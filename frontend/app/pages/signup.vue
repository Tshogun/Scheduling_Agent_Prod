<script setup>
const supabase = useSupabaseClient()
const router = useRouter()

// Controls which step of the form is visible
const step = ref(1) 

// Form data
const email = ref('')
const fullName = ref('')
const institutionName = ref('') // Changed from employeeId
const jobTitle = ref('')
const password = ref('')
const confirmPassword = ref('')

// UI state
const loading = ref(false)
const errorMessage = ref(null)

// Job title options for the dropdown
const jobTitles = ['Registered Nurse', 'Doctor', 'Surgeon', 'Admin Staff', 'Technician']

// --- Step 1: Check Email ---
const handleEmailContinue = () => {
  if (email.value) {
    step.value = 2
  } else {
    errorMessage.value = "Please enter a valid email address."
  }
}

// --- Step 2: Handle Final Signup ---
const handleSignUp = async () => {
  if (password.value !== confirmPassword.value) {
    errorMessage.value = "Passwords do not match."
    return
  }

  try {
    loading.value = true
    errorMessage.value = null

    // Call Supabase signUp
    const { data, error } = await supabase.auth.signUp({
      email: email.value,
      password: password.value,
      options: {
        data: {
          full_name: fullName.value,
          institution_name: institutionName.value, // Changed here
          job_title: jobTitle.value,
        }
      }
    })

    if (error) throw error

    alert("Success! Please check your email to confirm your account.")
    router.push('/login')

  } catch (error) {
    if (error.message.includes("User already registered")) {
        alert("This email is already registered. Please log in.")
        router.push('/')
    } else {
        errorMessage.value = error.message
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800">MediSync</h1>
        <p class="text-gray-500 mt-2">Create an Account</p>
      </div>

      <!-- STEP 1: Email Form -->
      <form v-if="step === 1" @submit.prevent="handleEmailContinue">
        <div class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email Address</label>
            <input 
              v-model="email"
              type="email" 
              id="email" 
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <button type="submit" class="w-full flex justify-center py-2 px-4 border rounded-md text-white bg-purple-600 hover:bg-purple-700">
              Continue
            </button>
          </div>
        </div>
      </form>

      <!-- STEP 2: Personal Details Form -->
      <form v-if="step === 2" @submit.prevent="handleSignUp">
        <div class="space-y-4">
          <!-- Full Name -->
          <div>
            <label for="fullName" class="block text-sm font-medium text-gray-700">Full Name</label>
            <input v-model="fullName" type="text" id="fullName" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <!-- Institution Name -->
          <div>
            <label for="institutionName" class="block text-sm font-medium text-gray-700">Institution Name</label>
            <input v-model="institutionName" type="text" id="institutionName" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <!-- Job Title Dropdown -->
          <div>
            <label for="jobTitle" class="block text-sm font-medium text-gray-700">Job Title</label>
            <select v-model="jobTitle" id="jobTitle" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-white">
              <option disabled value="">Please select one</option>
              <option v-for="title in jobTitles" :key="title" :value="title">{{ title }}</option>
            </select>
          </div>
          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input v-model="password" type="password" id="password" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <!-- Confirm Password -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">Confirm Password</label>
            <input v-model="confirmPassword" type="password" id="confirmPassword" required class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" />
          </div>
          <!-- Sign Up Button -->
          <div>
            <button type="submit" :disabled="loading" class="w-full flex justify-center py-2 px-4 border rounded-md text-white bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300">
              {{ loading ? 'Signing Up...' : 'Sign Up' }}
            </button>
          </div>
        </div>
      </form>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
        <p>{{ errorMessage }}</p>
      </div>

      <!-- Back to Login Link -->
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


