<template>
  <main class="home-wrapper">
    <h2 class="greet">Welcome to QuizMaster</h2>

    <!-- Centered Search -->
    <div class="user-search">
      <input
        v-model="query"
        type="text"
        placeholder="🔍 Search quizzes or subjects..."
        @input="performSearch"
      />
      <div v-if="results.length" class="results-box">
        <ul>
          <li v-for="(item, idx) in results" :key="idx">
            <strong>{{ item.type }}:</strong> {{ item.name }}
          </li>
        </ul>
      </div>
      <p v-else-if="query" class="no-results">No results found.</p>
    </div>

    <!-- Card Navigation -->
    <section class="card-grid">
      <RouterLink to="/user/subject" class="card">
        <h3>Browse&nbsp;Quizzes</h3>
        <p>Select a subject and quiz to start practicing.</p>
      </RouterLink>

      <RouterLink to="/score" class="card">
        <h3>My&nbsp;Scores</h3>
        <p>Check past attempts and view your progress.</p>
      </RouterLink>

      <RouterLink to="/summary" class="card">
        <h3>Summary</h3>
        <p>Update your profile and manage credentials.</p>
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
  padding: 2rem 1rem;
  font-family: 'Segoe UI', sans-serif;
  text-align: center;
}

/* Greeting */
.greet {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #1f2937;
}

/* Search */
.user-search {
  margin-bottom: 2.5rem;
  max-width: 500px;
  margin-inline: auto;
}
.user-search input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: border 0.2s ease-in-out;
}
.user-search input:focus {
  outline: none;
  border-color: #3b82f6;
}
.results-box {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-top: 1rem;
  padding: 0.75rem;
  text-align: left;
}
.user-search ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.user-search li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}
.user-search li:last-child {
  border-bottom: none;
}
.no-results {
  color: #6b7280;
  margin-top: 0.75rem;
}

/* Cards */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  text-decoration: none;
  color: #111827;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.card h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: #2563eb;
}
.card p {
  font-size: 0.95rem;
  color: #475569;
}
</style>
