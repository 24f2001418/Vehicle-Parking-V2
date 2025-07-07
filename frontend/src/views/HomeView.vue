<template>
  <div class="home-container">
    <!-- Hero / Intro -->
    <section class="hero fade-in">
      <h1>Welcome to <span class="brand">QuizMaster</span></h1>
      <p class="tagline">Practice quizzes, track progress, and ace your exams with confidence.</p>

      <!-- Auth buttons -->
      <div class="auth-buttons">
        <router-link to="/login" class="btn login-btn">Login</router-link>
        <router-link to="/register" class="btn register-btn">Sign Up</router-link>
      </div>
    </section>

    <!-- Features / Benefits -->
    <section class="info-section slide-up">
      <h2>Why QuizMaster?</h2>
      <ul>
        <li>📝 Curated quizzes aligned to your syllabus.</li>
        <li>⏱️ Timed practice that simulates real exam pressure.</li>
        <li>📊 Smart analytics to reveal strengths and weaknesses.</li>
        <li>🔔 Daily reminders & progress streak tracking.</li>
      </ul>

      <p class="note">Create a free account and start mastering every subject today.</p>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
/***** Layout / Global *****/
.home-container {
  max-width: 1050px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  color: #1f2937;
}
.brand {
  color: #93c5fd; /* lighter blue for better contrast on dark hero */
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.35);
}

/***** Hero Section *****/
.hero {
  background: linear-gradient(120deg, #1e40af 0%, #2563eb 50%, #4338ca 100%);
  padding: 3.5rem 2rem;
  border-radius: 18px;
  text-align: center;
  color: #f8fafc;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
  animation: fadeIn 0.8s ease-out;
}
.hero h1 {
  font-size: clamp(2.2rem, 6vw, 3rem);
  font-weight: 800;
  margin-bottom: 1rem;
  line-height: 1.15;
}
.tagline {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  margin-top: 0.5rem;
  color: #dbeafe;
  max-width: 36rem;
  margin-left: auto;
  margin-right: auto;
}

/***** Auth Buttons *****/
.auth-buttons {
  margin-top: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}
@media (min-width: 480px) {
  .auth-buttons { flex-direction: row; }
}
.btn {
  text-decoration: none;
  padding: 0.8rem 1.9rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  display: inline-block;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}
.login-btn {
  background-color: #10b981; /* emerald */
  color: #fff;
}
.login-btn:hover {
  background-color: #059669;
  transform: translateY(-3px);
}
.register-btn {
  background-color: #3b82f6; /* blue */
  color: #fff;
}
.register-btn:hover {
  background-color: #2563eb;
  transform: translateY(-3px);
}

/***** Info Section *****/
.info-section {
  margin-top: 3.5rem;
  background-color: #ffffff;
  padding: 2.75rem 2rem;
  border-radius: 14px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.06);
  text-align: left;
  animation: slideUp 0.9s ease-out;
}
.info-section h2 {
  font-size: 1.9rem;
  margin-bottom: 1rem;
  font-weight: 700;
  color: #1e293b;
}
.info-section ul {
  list-style: none;
  padding-left: 0;
  margin-bottom: 1.75rem;
}
.info-section li {
  margin-bottom: 0.85rem;
  font-size: 1.05rem;
  padding-left: 2rem;
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

/***** Animations *****/
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(40px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 1s ease-out; }
.slide-up { animation: slideUp 1s ease-out; }

/***** Responsive tweaks *****/
@media (max-width: 420px) {
  .hero { padding: 2.5rem 1.5rem; }
  .info-section { padding: 2.25rem 1.5rem; }
  .btn { font-size: 0.92rem; padding: 0.7rem 1.4rem; }
}
</style>
