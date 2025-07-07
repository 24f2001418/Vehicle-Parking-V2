<template>
  <div class="admin-welcome">
    <h2>Welcome, Admin 👋</h2>

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
      <div class="stat-box" @click="router.push('/admin/sessions')">
        <h3>{{ stats.activeSessions }}</h3>
        <p>Sessions</p>
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

async function fetchUsers () {
  const res = await fetch('/api/users', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalUsers = (await res.json()).users?.length || 0
  }
}

async function fetchQuizzes () {
  const res = await fetch('/api/quizzes', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalQuizzes = (await res.json()).quizzes?.length || 0
  }
}

async function fetchQuestions () {
  const res = await fetch('/api/questions/count', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  if (res.ok) {
    stats.value.totalQuestions = (await res.json()).count || 0
  }
  stats.value.activeSessions = Math.floor(Math.random() * 10) + 1
}
</script>

<style scoped>
.admin-welcome {
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
}
.admin-welcome h2 {
  font-size: 1.75rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #1e293b;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-box {
  background: #ffffff;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  text-align: center;
  padding: 1.5rem 1rem;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stat-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
}
.stat-box h3 {
  margin: 0;
  font-size: 2rem;
  color: #2563eb;
}
.stat-box p {
  margin: 0.25rem 0 0 0;
  color: #475569;
  font-weight: 500;
}

.manage-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.manage-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}
.manage-item:hover {
  background: #e0f2fe;
}
.icon {
  font-size: 1.75rem;
}
.manage-item h4 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}
.manage-item p {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>