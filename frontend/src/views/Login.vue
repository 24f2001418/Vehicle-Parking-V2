<template>
  <main class="login-wrapper">
    <section class="login-card">
      <h2 class="title">Log in to QuizMaster</h2>

      <form @submit.prevent="handleLogin">
        <!-- email -->
        <div class="field">
          <label for="email">Email</label>
          <input
            v-model.trim="email"
            id="email"
            type="email"
            placeholder="you@example.com"
            autocomplete="username"
            required
          />
        </div>

        <!-- password -->
        <div class="field">
          <label for="password">Password</label>
          <input
            v-model="password"
            id="password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            minlength="6"
            required
          />
        </div>

        <button class="btn" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Log in' }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <p class="alt">
        Don’t have an account?
        <router-link to="/register">Register here</router-link>
      </p>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''

      try {
        const { data } = await axios.post('/api/auth/login', {
          email: this.email,
          password: this.password
        })

        /* store token + user role */
        localStorage.setItem('token', data.token)
        const role = data.user?.role || 'user'

        /* route by role */
        this.$router.push(role === 'admin' ? '/admin' : '/user')
      } catch (err) {
        this.error =
          err.response?.data?.msg || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #eef4ff;
  padding: 2rem;
}

.login-card {
  max-width: 420px;
  width: 100%;
  background: #fff;
  border-radius: 14px;
  padding: 2.5rem 2rem;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.title {
  font-size: 1.9rem;
  font-weight: 700;
  margin-bottom: 1.75rem;
  color: #333;
}

.alt {
  margin-top: 1.5rem;
  font-size: 0.95rem;
}

.alt a {
  color: #007bff;
  text-decoration: underline;
}

.error {
  margin-top: 1rem;
  color: #d9534f;
  font-weight: 500;
}

.field {
  margin-bottom: 1.1rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: 600;
  color: #444;
}

input {
  width: 100%;
  padding: 0.7rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 1rem;
  transition: border 0.2s;
}

input:focus {
  outline: none;
  border-color: #007bff;
}

.btn {
  width: 100%;
  padding: 0.8rem;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.btn:hover {
  background: #0069d9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
