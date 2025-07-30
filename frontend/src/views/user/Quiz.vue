<template>
  <main class="attempt-wrapper">
    <!-- Header with timer & progress bar -->
    <header class="quiz-head" v-if="quiz && questions.length">
      <h2>{{ quiz.title }}</h2>
      <div class="meta">
        <span class="timer" :class="{ urgent: remaining <= 15 }">
          ⏱ {{ prettyTime }}
        </span>
        <span>{{ current + 1 }} / {{ questions.length }}</span>
      </div>
      <!-- Progress bar -->
      <div class="progress-wrapper">
        <div class="bar">
          <div class="fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <small>{{ progressPercent.toFixed(0) }} %</small>
      </div>
    </header>

    <!-- Loading -->
    <p v-if="loading" class="loading">Loading quiz…</p>
    <p v-else-if="!questions.length" class="empty">No questions available for this quiz.</p>

    <!-- Question carousel -->
    <section v-else-if="!finished && questions.length" class="question-box">
      <h3 class="q-text">
        Q{{ current + 1 }}. {{ currentQ.question_statement }}
      </h3>
      <ul class="options">
        <li v-for="num in 4" :key="num">
          <label>
            <input
              type="radio"
              :value="num"
              v-model="answers[currentQ.id]"
              :disabled="finished"
              @change="onSelect(currentQ.id, num)"
            />
            {{ currentQ['option' + num] }}
          </label>
        </li>
      </ul>
      <!-- feedback (hidden until submit) -->
      <!-- nav buttons -->
      <div class="nav">
        <button class="btn" @click="prev" :disabled="current === 0">Prev</button>
        <button class="btn" @click="next" :disabled="current === questions.length - 1">Next</button>
        <button
          class="btn primary"
          @click="submit"
          :disabled="Object.keys(answers).length < questions.length"
        >
          Submit
        </button>
      </div>
    </section>

    <!-- Result view -->
    <section v-else-if="finished && questions.length" class="result">
      <h2>Your Score</h2>
      <p class="big">{{ score }} / {{ questions.length }}</p>
      <div v-for="(q, idx) in questions" :key="q.id" class="review-row">
        <div class="review-q">Q{{ idx+1 }}. {{ q.question_statement }}</div>
        <div class="review-a">
          <span :class="answers[q.id] === q.correct_option ? 'correct' : 'wrong'">
            Your answer: {{ q['option'+answers[q.id]] || '—' }}
          </span>
          <span v-if="answers[q.id] !== q.correct_option" class="correct">
            | Correct: {{ q['option'+q.correct_option] }}
          </span>
        </div>
      </div>
      <button class="btn primary" @click="goHome">Back to dashboard</button>
    </section>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const API    = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const route  = useRoute()
const router = useRouter()
const quizId = route.params.id

/* State */
const loading    = ref(true)
const quiz       = ref(null)
const questions  = ref([])
const answers    = ref({})
const current    = ref(0)
const finished   = ref(false)
const score      = ref(0)
const showFeedback = ref(false) // not used anymore

/* Timer */
let tick
const remaining = ref(0)
const prettyTime = computed(() => {
  const m = String(Math.floor(remaining.value / 60)).padStart(2, '0')
  const s = String(remaining.value % 60).padStart(2, '0')
  return `${m}:${s}`
})

/* Progress bar percentage */
const progressPercent = computed(() => {
  if (!questions.value.length) return 0
  return ((current.value + 1) / questions.value.length) * 100
})

/* Fetch data */
onMounted(loadQuiz)
onBeforeUnmount(() => clearInterval(tick))

async function loadQuiz() {
  try {
    const hdr = { Authorization: `Bearer ${localStorage.token}` }
    const { data: qData }  = await axios.get(`${API}/quizzes/${quizId}`, { headers: hdr })
    const { data: qsData } = await axios.get(`${API}/quizzes/${quizId}/questions`, { headers: hdr })
    quiz.value       = qData.quiz
    questions.value  = qsData.questions || []
    if (!questions.value.length) {
      loading.value = false
      return
    }
    remaining.value  = parseDuration(quiz.value.time_duration || '00:10')
    tick = setInterval(() => {
      if (--remaining.value <= 0) {
        clearInterval(tick)
        submit()
      }
    }, 1000)
  } finally {
    loading.value = false
  }
}

/* Helpers */
function parseDuration(hhmm) {
  const [h, m] = hhmm.split(':').map(Number)
  return (h * 60 + m) * 60
}
const currentQ = computed(() => questions.value[current.value] || {})

function locked(id)      { return id in answers.value }
function isCorrect(id)   {
  const q = questions.value.find(x => x.id === id)
  return answers.value[id] === q?.correct_option
}
function optionClass(num) {
  // No color feedback before submit
  return ''
}
const correctOptionText = computed(() => {
  const q = currentQ.value
  if (!q) return ''
  return q['option' + q.correct_option]
})

/* Navigation */
function next() { if (current.value < questions.value.length - 1) { current.value++; } }
function prev() { if (current.value > 0) { current.value--; } }

/* Selection */
function onSelect(qid, option) {
  answers.value[qid] = option
}

/* Submit */
async function submit() {
  if (finished.value) return
  clearInterval(tick)
  score.value = questions.value.reduce(
    (sum, q) => sum + (answers.value[q.id] === q.correct_option ? 1 : 0),
    0
  )
  try {
    const hdr = { Authorization: `Bearer ${localStorage.token}` }
    await axios.post(`${API}/quizzes/${quizId}/attempt`, { answers: answers.value }, { headers: hdr })
  } catch (e) {
    console.error('Submission error:', e)
  } finally {
    finished.value = true
  }
}
function goHome() {
  router.push('/user')
}
</script>

<style scoped>
/* Layout */
.attempt-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1.25rem;
  font-family: 'Inter', sans-serif;
}
.quiz-head h2 {
  margin: 0 0 0.3rem;
  font-size: 1.55rem;
}
.meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.95rem;
  color: #475569;
}
.timer {
  font-weight: 600;
}
.timer.urgent {
  color: #dc2626;
}

/* Progress bar */
.progress-wrapper {
  margin-top: 0.4rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.bar {
  flex: 1 1 auto;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: #22c55e;
  transition: width 0.25s ease;
}

/* Question box */
.question-box {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.q-text {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #1f2937;
}
.options {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;
}
.options li {
  margin-bottom: 0.7rem;
}
label {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  cursor: pointer;
}
input[type="radio"] {
  accent-color: #2563eb;
}
.opt.correct {
  background: #dcfce7;
  font-weight: 600;
}
.opt.wrong {
  background: #fee2e2;
  font-weight: 600;
}
.feedback {
  font-weight: 600;
  color: #334155;
}

/* Navigation buttons */
.nav {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}
.btn {
  background: #e5e7eb;
  border: none;
  border-radius: 6px;
  padding: 0.6rem 1.1rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn.primary {
  background: #2563eb;
  color: #fff;
}
.btn.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

/* Result */
.result {
  text-align: center;
  padding: 2rem;
}
.big {
  font-size: 2.4rem;
  font-weight: 700;
  margin: 0 0 2rem;
}

/* Review answers */
.review-row {
  margin: 1.2rem 0 0.7rem 0;
  padding: 0.7rem 1rem;
  background: #f8fafc;
  border-radius: 7px;
  font-size: 1.01rem;
  box-shadow: 0 1px 2px #0001;
}
.review-q {
  font-weight: 500;
  margin-bottom: 0.2rem;
}
.review-a {
  font-size: 0.98rem;
}
.review-a .correct {
  color: #22c55e;
  font-weight: 600;
}
.review-a .wrong {
  color: #ef4444;
  font-weight: 600;
}

/* Status text */
.loading, .empty {
  text-align: center;
  padding: 2rem 0;
  font-size: 1rem;
  color: #64748b;
}
.options li label {
  background: none !important;
}
</style>
