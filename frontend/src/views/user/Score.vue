<template>
  <main class="scores-wrapper">
    <h1 class="title">My Quiz Scores</h1>

    <!-- SUMMARY -->
    <section v-if="!loading && scores.length" class="summary">
      <div><strong>{{ scores.length }}</strong> attempts</div>
      <div>
        <strong>{{ avgPercent.toFixed(1) }} %</strong>
        average
      </div>
      <div>
        <strong>{{ bestPercent.toFixed(1) }} %</strong>
        personal best
      </div>
    </section>

    <!-- LOADING -->
    <p v-if="loading" class="loading">Loading scores…</p>

    <!-- TABLE / EMPTY -->
    <div v-else class="card">
      <p v-if="!scores.length" class="empty">You haven’t taken any quizzes yet.</p>

      <table v-else class="score-table">
        <thead>
          <tr>
            <th @click="setSort('date')">Date <span :class="dirIf('date')" /></th>
            <th @click="setSort('quiz')">Quiz <span :class="dirIf('quiz')" /></th>
            <th @click="setSort('score')">Score <span :class="dirIf('score')" /></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in sorted" :key="s.id">
            <td>{{ fmtDate(s.attempted_at) }}</td>
            <td>{{ s.quiz_title || `Quiz #${s.quiz_id}` }}</td>
            <td>
              {{ s.total_score }}
              <template v-if="s.max_score"> / {{ s.max_score }}</template>
              ({{ percent(s).toFixed(0) }} %)
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API      = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const loading  = ref(true)
const scores   = ref([])

/* Fetch scores on mount */
onMounted(async () => {
  try {
    const { data } = await axios.get(`${API}/scores`, {
      headers: { Authorization: `Bearer ${localStorage.token}` }
    })
    scores.value = data.scores || []
  } finally { loading.value = false }
})

/* Helpers */
const percent = s =>
  s.max_score ? (s.total_score / s.max_score) * 100 : s.total_score
const fmtDate = iso =>
  new Date(iso).toLocaleString(undefined, { dateStyle:'medium', timeStyle:'short' })

/* Summary stats */
const avgPercent  = computed(() =>
  scores.value.length ? scores.value.reduce((a,s)=>a+percent(s),0)/scores.value.length : 0)
const bestPercent = computed(() =>
  scores.value.reduce((m,s)=>Math.max(m,percent(s)),0))

/* Sorting */
const sortKey = ref('date')      // 'date' | 'quiz' | 'score'
const sortDir = ref('desc')      // 'asc' | 'desc'
function setSort (key) {
  if (sortKey.value === key) sortDir.value = sortDir.value==='asc'?'desc':'asc'
  else { sortKey.value = key; sortDir.value = key==='quiz' ? 'asc' : 'desc' }
}
function dirIf (k) {
  return sortKey.value === k ? sortDir.value : ''
}
const sorted = computed(() => {
  return [...scores.value].sort((a,b) => {
    let res = 0
    switch (sortKey.value) {
      case 'quiz':
        res = (a.quiz_title||'').localeCompare(b.quiz_title||'')
        break
      case 'score':
        res = percent(b) - percent(a)
        break
      default: // date
        res = new Date(b.attempted_at) - new Date(a.attempted_at)
    }
    return sortDir.value === 'asc' ? -res : res
  })
})
</script>

<style scoped>
/* Layout / Card */
.scores-wrapper{max-width:900px;margin:auto;padding:2rem 1.25rem;font-family:'Inter',sans-serif;}
.title{font-size:1.6rem;font-weight:700;margin:0 0 1.25rem;color:#1e293b;}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:1rem;box-shadow:0 4px 12px rgba(0,0,0,.05);}
.loading,.empty{text-align:center;padding:2rem 0;color:#64748b;font-size:1rem;}

/* Summary bar */
.summary{display:flex;gap:1.5rem;margin-bottom:1rem;font-size:.95rem;color:#475569;}
.summary div{background:#f1f5f9;border-radius:8px;padding:.6rem 1rem;}
.summary strong{color:#1e40af;}

/* Table */
.score-table{width:100%;border-collapse:collapse;font-size:.9rem;}
.score-table th,.score-table td{padding:.65rem .8rem;border-bottom:1px solid #f8fafc;text-align:left;}
.score-table th{background:#f9fafb;cursor:pointer;user-select:none;}
.score-table tbody tr:nth-child(even){background:#fafafa;}

/* Sort arrow indicators */
th span{margin-left:4px;border:4px solid transparent;border-top-color:#64748b;display:inline-block;vertical-align:middle;transform:translateY(-1px);}
th .asc  {border-top-color:transparent;border-bottom-color:#64748b;}

/* Small responsiveness */
@media(max-width:640px){
  .score-table thead{display:none;}
  .score-table,tr,td{display:block;width:100%;}
  .score-table td{border:none;padding:.6rem .4rem;border-bottom:1px solid #f3f4f6;}
  .score-table td::before{content:attr(data-label);font-weight:600;display:inline-block;width:90px;color:#64748b;}
}
</style>
