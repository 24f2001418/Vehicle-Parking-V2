<template>
  <main class="home-wrapper">
    <h2 class="greet">Welcome to QuizMaster</h2>

    <!-- Search Bar -->
    <div class="user-search">
      <input
        v-model="query"
        type="text"
        placeholder="Search quizzes or subjects..."
        @input="performSearch"
      />
      <div v-if="results.length">
        <h3>Results</h3>
        <ul>
          <li v-for="(item, idx) in results" :key="idx">
            <strong>{{ item.type }}:</strong> {{ item.name }}
          </li>
        </ul>
      </div>
      <div v-else-if="query">
        <p>No results found.</p>
      </div>
    </div>

    <section class="card-grid">
      <!-- Browse Quizzes -->
      <RouterLink to="/user/subject" class="card">
        <h3>Browse&nbsp;Quizzes</h3>
        <p>Pick a subject, choose a quiz and start practising.</p>
      </RouterLink>

      <!-- My Scores -->
      <RouterLink to="/score" class="card">
        <h3>My&nbsp;Scores</h3>
        <p>View your past attempts and track your progress.</p>
      </RouterLink>

      <!-- Profile -->
      <RouterLink to="/summary" class="card">
        <h3>Summary</h3>
        <p>Update personal info or change your password.</p>
      </RouterLink>
    </section>
  </main>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { ref, onMounted } from 'vue'

const userName = ref('User')
const query = ref('')
const results = ref([])

onMounted(() => {
  const stored = JSON.parse(localStorage.getItem('user') || '{}')
  userName.value = stored.full_name || 'User'
})

const performSearch = async () => {
  if (!query.value.trim()) {
    results.value = []
    return
  }
  const res = await fetch(`/api/search/user/quizsubject?q=${encodeURIComponent(query.value)}`)
  if (res.ok) {
    const data = await res.json()
    results.value = []
    if (data.subjects) {
      results.value.push(...data.subjects.map(s => ({ type: 'Subject', name: s.name })))
    }
    if (data.quizzes) {
      results.value.push(...data.quizzes.map(q => ({ type: 'Quiz', name: q.title })))
    }
  } else {
    results.value = []
  }
}
</script>

<style scoped>
/* Layout */
.home-wrapper {
  max-width: 950px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  font-family: 'Inter', sans-serif;
}

/* Greeting */
.greet {
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #1f2937;
}

/* Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
}
.card h3 {
  margin: 0 0 0.6rem;
  font-size: 1.25rem;
  color: #2563eb;
}
.card p {
  margin: 0;
  font-size: 0.95rem;
  color: #475569;
}
/* User Search */
.user-search {
  margin: 2rem auto 2.5rem auto;
  max-width: 500px;
  text-align: center;
}
.user-search input {
  width: 100%;
  padding: 0.7rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-bottom: 1rem;
}
.user-search ul {
  list-style: none;
  padding: 0;
}
.user-search li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}
</style>
