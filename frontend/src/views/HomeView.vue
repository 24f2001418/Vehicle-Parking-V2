<template>
  <div class="home-container">
    <section class="hero fade-in">
      <h1>Welcome to ParkEase</h1>
      <p class="tagline">Find and manage parking spots effortlessly and securely.</p>

      <div class="auth-buttons">
        <router-link to="/login" class="btn login-btn">Login</router-link>
        <router-link to="/register" class="btn register-btn">Register</router-link>
      </div>
    </section>

    <section class="info-section slide-up">
      <h2>Why ParkEase?</h2>
      <ul>
        <li>📍 Live spot availability near your location.</li>
        <li>⚡ One-click reservations with instant confirmation.</li>
        <li>🔐 Safe entry, exit, and payment process.</li>
        <li>🧠 Stress-free parking with smart recommendations.</li>
      </ul>

      <p class="note">Please <strong>log in</strong> or <strong>sign up</strong> to start parking smarter.</p>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
};
</script>

<style scoped>
/* --------------------- Layout --------------------- */
.home-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  color: #1f2937;
}

/* --------------------- Hero Section --------------------- */
.hero {
  background: linear-gradient(to right, #1e293b, #0f172a);
  padding: 3rem 2rem;
  border-radius: 16px;
  text-align: center;
  color: #f8fafc;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
  animation: fadeIn 1s ease-out;
}

.hero h1 {
  font-size: 2.75rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.tagline {
  font-size: 1.2rem;
  margin-top: 0.5rem;
  color: #cbd5e1;
}

/* --------------------- Auth Buttons --------------------- */
.auth-buttons {
  margin-top: 2.5rem;
}

.btn {
  text-decoration: none;
  padding: 0.75rem 1.75rem;
  margin: 0 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
}

.login-btn {
  background-color: #10b981; /* green */
  color: white;
}

.login-btn:hover {
  background-color: #059669;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);
}

.register-btn {
  background-color: #3b82f6; /* blue */
  color: white;
}

.register-btn:hover {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
}

/* --------------------- Info Section --------------------- */
.info-section {
  margin-top: 3.5rem;
  text-align: left;
  background-color: #f9fafb;
  padding: 2.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  animation: slideUp 1s ease-out;
}

.info-section h2 {
  font-size: 1.75rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.info-section ul {
  list-style: none;
  padding-left: 0;
  margin-bottom: 1.5rem;
}

.info-section li {
  margin-bottom: 0.75rem;
  font-size: 1.05rem;
  padding-left: 1.5rem;
  position: relative;
  color: #374151;
}

.info-section li::before {
  content: "✔️";
  position: absolute;
  left: 0;
}

.note {
  font-style: italic;
  color: #64748b;
}

/* --------------------- Animations --------------------- */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 1s ease-out;
}

.slide-up {
  animation: slideUp 1s ease-out;
}
</style>
