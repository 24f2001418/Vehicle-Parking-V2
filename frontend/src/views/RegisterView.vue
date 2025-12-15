<template>
  <main class="register-wrapper">
    <section class="register-card">
      <h2 class="title">Create a ParkEase Account</h2>

      <form @submit.prevent="handleRegister">
        <!-- Name -->
        <div class="field">
          <label for="name">Name</label>
          <input
            v-model.trim="name"
            id="name"
            type="text"
            placeholder="Your name"
            autocomplete="name"
            required
          />
        </div>

        <!-- Email -->
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

        <!-- Password -->
        <div class="field">
          <label for="password">Password</label>
          <input
            v-model="password"
            id="password"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
            minlength="6"
            required
          />
        </div>

        <!-- Confirm Password -->
        <div class="field">
          <label for="confirmPassword">Confirm Password</label>
          <input
            v-model="confirmPassword"
            id="confirmPassword"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
            minlength="6"
            required
          />
        </div>

        <button class="btn" :disabled="loading">
          {{ loading ? 'Creating Account…' : 'Register' }}
        </button>

        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="success" class="success">{{ success }}</p>
      </form>

      <p class="alt">
        Already have an account?
        <router-link to="/login">Log in here</router-link>
      </p>
    </section>
  </main>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterPage',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      loading: false,
      error: '',
      success: ''
    };
  },
  methods: {
    async handleRegister() {
      this.error = '';
      this.success = '';

      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match.';
        return;
      }

      this.loading = true;

      try {
        await axios.post('http://127.0.0.1:5000/api/auth/register', {
          name: this.name,
          email: this.email,
          password: this.password
        });

        this.success = 'Account created! Redirecting to login…';
        setTimeout(() => {
          this.$router.push('/login');
        }, 1500);
      } catch (e) {
        this.error =
          e?.response?.data?.msg || 'Registration failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Layout */
.register-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #eef4ff;
  padding: 2rem;
}

.register-card {
  width: 100%;
  max-width: 460px;
  background: #ffffff;
  border-radius: 14px;
  padding: 2.5rem 2rem;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  text-align: center;
}

/* Typography */
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

.success {
  margin-top: 1rem;
  color: #28a745;
  font-weight: 500;
}

/* Form Fields */
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

/* Button */
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
