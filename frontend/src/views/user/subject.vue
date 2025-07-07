<template>
  <main class="dash-wrapper">
    <!-- Subjects list -->
    <section v-if="!selected" class="subject-grid" v-show="!loading">
      <h2 class="title">Available Subjects</h2>

      <div v-if="subjects.length" class="grid">
        <div
          v-for="s in subjects"
          :key="s.id"
          class="card"
          @click="selectSubject(s)"
        >
          <h3>{{ s.name }}</h3>
          <p>{{ s.description || '— No description —' }}</p>
        </div>
      </div>

      <p v-else class="empty">No subjects found.</p>
    </section>

    <!-- Quizzes in chosen subject -->
    <section v-else class="quiz-list" v-show="!loading">
      <button class="back-btn" @click="reset">← Back to subjects</button>
      <h2 class="title">{{ selected.name }} – Quizzes</h2>

      <div v-if="quizzes.length" class="grid">
        <div v-for="q in quizzes" :key="q.id" class="card card-quiz">
          <h3>{{ q.title }}</h3>
          <p>
            <strong>Duration:</strong>
            {{ q.time_duration || '—' }}
          </p>
          <button class="start" @click="goAttempt(q.id)">
            Start&nbsp;Quiz
          </button>
        </div>
      </div>

      <p v-else class="empty">No quizzes under this subject.</p>
    </section>

    <div v-if="loading" class="loading">Loading…</div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const router = useRouter()
const hdr = () => ({ Authorization: `Bearer ${localStorage.token}` })

const loading   = ref(true)
const subjects  = ref([])
const selected  = ref(null)     // currently picked subject object
const quizzes   = ref([])       // quizzes aggregated for that subject

/* Initial load – subjects */
onMounted(loadSubjects)
async function loadSubjects () {
  loading.value = true
  try {
    const { data } = await axios.get(`${API}/subjects`, { headers: hdr() })
    subjects.value = data.subjects || []
  } finally {
    loading.value = false
  }
}

/* When user clicks a subject */
async function selectSubject (subj) {
  selected.value = subj
  quizzes.value  = []
  loading.value  = true

  try {
    const { data: chData } = await axios.get(
      `${API}/subjects/${subj.id}/chapters`,
      { headers: hdr() }
    )
    const chapters = chData.chapters || []

    // Fetch quizzes for every chapter (parallel)
    const promises = chapters.map(c =>
      axios
        .get(`${API}/chapters/${c.id}/quizzes`, { headers: hdr() })
        .then(r => r.data.quizzes || [])
    )
    const chunks   = await Promise.all(promises)
    quizzes.value  = chunks.flat()
  } finally {
    loading.value = false
  }
}

/* Back to subjects list */
function reset () {
  selected.value = null
  quizzes.value  = []
}

/* Go to quiz attempt view */
function goAttempt (id) {
  router.push(`/quiz/${id}`)      // adjust route if different
}
</script>

<style scoped>
/* --- Layout wrappers --- */
.dash-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.25rem;
  font-family: 'Inter', sans-serif;
}
.title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  color: #1e293b;
}

/* --- Grid of cards --- */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}

/* --- Card --- */
.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.2rem 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
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

/* --- Quiz card custom --- */
.card-quiz {
  cursor: default;
}
.start {
  margin-top: 0.9rem;
  padding: 0.55rem 1.1rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #fff;
  background: #22c55e;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}
.start:hover {
  background: #16a34a;
}

/* --- Back button --- */
.back-btn {
  margin-bottom: 1rem;
  border: 1px solid #cbd5e1;
  background: #f1f5f9;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}

/* --- States --- */
.loading,
.empty {
  text-align: center;
  padding: 2rem 0;
  font-size: 1rem;
  color: #64748b;
}
</style>
