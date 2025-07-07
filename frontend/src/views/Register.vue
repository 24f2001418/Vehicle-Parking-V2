<template>
  <div class="register-container">
    <div class="register-box">
      <h2>Create Your <span class="highlight">QuizMaster</span> Account</h2>

      <div v-if="error" class="error">{{ error }}</div>

      <form @submit.prevent="handleRegister" novalidate>
        <!-- Full Name -->
        <label for="fullName">Full Name</label>
        <input v-model="fullName" type="text" id="fullName" placeholder="Your name" required>

        <!-- Email -->
        <label for="email">Email</label>
        <input v-model="email" type="email" id="email" placeholder="you@example.com" required>

        <!-- Password with eye toggle -->
        <label for="password">Password</label>
        <div class="password-wrapper">
          <input
            v-model="password"
            :type="showPwd ? 'text' : 'password'"
            id="password"
            placeholder="••••••••"
            required>
          <button type="button" class="eye-btn" @click="showPwd = !showPwd" :aria-label="showPwd ? 'Hide password' : 'Show password'">
            <svg v-if="showPwd" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94a10.06 10.06 0 1 1 0-11.88"/>
              <path d="M1 1l22 22"/>
            </svg>
          </button>
        </div>

        <!-- Qualification -->
        <label for="qualification">Qualification</label>
        <input v-model="qualification" type="text" id="qualification" placeholder="e.g. B.Sc. Physics">

        <!-- Date of Birth -->
        <label for="dob">Date of Birth</label>
        <input v-model="dob" type="date" id="dob">

        <!-- Submit -->
        <button :disabled="loading">
          {{ loading ? 'Registering…' : 'Register' }}
        </button>
      </form>

      <p class="login-link">
        Already have an account?
        <RouterLink to="/login">Sign in here</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'

const router = useRouter()
const fullName      = ref('')
const email         = ref('')
const password      = ref('')
const qualification = ref('')
const dob           = ref('')
const showPwd       = ref(false)
const error         = ref('')
const loading       = ref(false)

async function handleRegister () {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: fullName.value,
        email: email.value,
        password: password.value,
        qualification: qualification.value,
        dob: dob.value
      })
    })
    if (!res.ok) {
      const msg = await res.json().catch(() => null)
      throw new Error(msg?.msg || 'Registration failed')
    }
    router.push('/login')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Reset & base */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; font-family: 'Segoe UI', sans-serif; }

/* Layout */
.register-container { display: flex; align-items: center; justify-content: center; height: 100vh; background: #f3f7ff; }

.register-box {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  animation: fadeIn 0.4s ease;
}

.register-box h2 { margin-bottom: 1.5rem; text-align: center; font-weight: 600; color: #333; }
.highlight { color: #2563eb; }

/* Form styles */
form { display: flex; flex-direction: column; }
label { margin-bottom: 0.25rem; font-weight: 500; color: #444; }
input {
  padding: 0.6rem 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  transition: border 0.2s ease;
}
input:focus { border-color: #2563eb; outline: none; }

/* Password wrapper */
.password-wrapper { position: relative; }
.password-wrapper input { width: 100%; padding-right: 2.5rem; }
.eye-btn {
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  color: #666;
}
.eye-btn:hover { color: #2563eb; }

button {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
button:hover:enabled { background: #1e40af; }
button:disabled { opacity: 0.6; cursor: not-allowed; }

/* Error message */
.error { background: #fee2e2; color: #b91c1c; padding: 0.75rem; margin-bottom: 1rem; border-radius: 8px; font-size: 0.9rem; text-align: center; }

/* Link */
.login-link { text-align: center; margin-top: 1rem; font-size: 0.9rem; }
.login-link a { color: #2563eb; text-decoration: none; }
.login-link a:hover { text-decoration: underline; }

/* Animation */
@keyframes fadeIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
