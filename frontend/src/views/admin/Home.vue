<template>
  <div class="admin-page">
    <!-- Admin Search (Top Centered) -->
    <div class="admin-search">
      <h2>Welcome, Admin 👋</h2>
      <input
        v-model="query"
        type="text"
        placeholder="Search users, subjects, quizzes, or questions..."
        @input="performSearch"
      />
      <div v-if="results.length">
        <h3>Results</h3>
        <ul>
          <li v-for="(item, index) in results" :key="index">
            <strong>{{ item.type }}:</strong> {{ item.name }}
          </li>
        </ul>
      </div>
      <div v-else-if="query">
        <p>No results found.</p>
      </div>
    </div>

    <!-- Admin Welcome -->
    <div class="admin-welcome">

      <!-- Stats -->
      <div class="stats-container">
        <div class="stat-box" @click="router.push('/admin/users')">
          <h3>{{ stats.totalUsers }}</h3>
          <p>Users</p>
        </div>
        <div class="stat-box" @click="router.push('/admin/quizzes')">
          <h3>{{ stats.totalQuizzes }}</h3>
          <p>Quizzes</p>
        </div>
        <div class="stat-box" @click="router.push('/admin/questions')">
          <h3>{{ stats.totalQuestions }}</h3>
          <p>Questions</p>
        </div>
      </div>

      <!-- Manage Section -->
      <div class="manage-section">
        <div class="manage-item" @click="router.push('/admin/Subject')">
          <span class="icon">📚</span>
          <div>
            <h4>Manage Subjects</h4>
            <p>Create, edit & delete subjects</p>
          </div>
        </div>
        <div class="manage-item" @click="router.push('/admin/users')">
          <span class="icon">👤</span>
          <div>
            <h4>Manage Users</h4>
            <p>View & control users</p>
          </div>
        </div>
        <div class="manage-item" @click="router.push('/admin/summary')">
          <span class="icon">📊</span>
          <div>
            <h4>Summary</h4>
            <p>Track overall performance</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  totalUsers: 0,
  totalQuizzes: 0,
  totalQuestions: 0,
  activeSessions: 0
})

onMounted(async () => {
  await Promise.all([fetchUsers(), fetchQuizzes(), fetchQuestions()])
})

async function fetchUsers() {
  const res = await fetch('/api/users', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalUsers = (await res.json()).users?.length || 0
  }
}

async function fetchQuizzes() {
  const res = await fetch('/api/quizzes', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalQuizzes = (await res.json()).quizzes?.length || 0
  }
}

async function fetchQuestions() {
  const res = await fetch('/api/questions/count', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalQuestions = (await res.json()).count || 0
  }
  stats.value.activeSessions = Math.floor(Math.random() * 10) + 1
}

// Search logic
const query = ref('')
const results = ref([])

const performSearch = async () => {
  if (!query.value.trim()) {
    results.value = []
    return
  }

  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }

  const [usersRes, subjectsRes, chaptersRes, quizzesRes, questionsRes] = await Promise.all([
    fetch(`/api/search/users?q=${query.value}`, { headers }),
    fetch(`/api/search/subjects?q=${query.value}`, { headers }),
    fetch(`/api/search/chapters?q=${query.value}`, { headers }),
    fetch(`/api/search/quizzes?q=${query.value}`, { headers }),
    fetch(`/api/search/questions?q=${query.value}`, { headers })
  ])

  results.value = []

  if (usersRes.ok) {
    const users = await usersRes.json()
    results.value.push(...(users.users || []).map(u => ({ type: 'User', name: u.name })))
  }
  if (subjectsRes.ok) {
    const subjects = await subjectsRes.json()
    results.value.push(...(subjects.subjects || []).map(s => ({ type: 'Subject', name: s.name })))
  }
  if (chaptersRes.ok) {
    const chapters = await chaptersRes.json()
    results.value.push(...(chapters.chapters || []).map(c => ({ type: 'Chapter', name: c.name })))
  }
  if (quizzesRes.ok) {
    const quizzes = await quizzesRes.json()
    results.value.push(...(quizzes.quizzes || []).map(q => ({ type: 'Quiz', name: q.title })))
  }
  if (questionsRes.ok) {
    const questions = await questionsRes.json()
    results.value.push(...(questions.questions || []).map(q => ({ type: 'Question', name: q.text })))
  }
}
</script>

<style scoped>
.admin-page {
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  background: #f1f5f9;
  min-height: 100vh;
}

/* Centered Search */
.admin-search {
  max-width: 720px;
  margin: 0 auto 3rem auto;
  text-align: center;
}

.admin-search input {
  width: 100%;
  padding: 0.9rem 1.2rem;
  font-size: 1rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background-color: #fff;
  transition: box-shadow 0.2s;
}

.admin-search input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
}

.admin-search h3 {
  margin-top: 1.5rem;
  font-size: 1.25rem;
  color: #1e293b;
}

.admin-search ul {
  text-align: left;
  background: #ffffff;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 0.5rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
}

.admin-search li {
  padding: 0.6rem 0;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}
.admin-search li:last-child {
  border-bottom: none;
}

.admin-search p {
  color: #64748b;
  font-style: italic;
}

/* Header */
.admin-welcome h2 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 2rem;
  text-align: center;
}

/* Stats Grid */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stat-box {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  text-align: center;
  padding: 1.5rem 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
  cursor: pointer;
}

.stat-box:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

.stat-box h3 {
  margin: 0;
  font-size: 2.2rem;
  color: #2563eb;
  font-weight: 700;
}

.stat-box p {
  margin-top: 0.25rem;
  font-size: 1rem;
  color: #475569;
}

/* Manage Section */
.manage-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.manage-item {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: background 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
}

.manage-item:hover {
  background: #eff6ff;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
}

.icon {
  font-size: 1.8rem;
  color: #2563eb;
}

.manage-item h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
  font-weight: 600;
}

.manage-item p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #64748b;
}

</style>
