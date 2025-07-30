<template>
  <main class="sum-wrapper">
    <h1 class="title">Quiz Summary Report</h1>

    <!-- OVERALL STATS -->
    <section v-if="!loading && rows.length" class="overall">
      <article class="stat"><h3>{{ rows.length }}</h3><p>Attempts</p></article>
      <article class="stat"><h3>{{ totalPoints }}</h3><p>Total Points</p></article>
      <article class="stat"><h3>{{ avgPercent.toFixed(1) }}%</h3><p>Average %</p></article>
      <article class="stat"><h3>{{ bestPercent.toFixed(1) }}%</h3><p>Best %</p></article>
    </section>

    <!-- CHARTS -->
    <section v-if="!loading && rows.length" class="charts">
      <div class="card chart-card">
        <h3>Performance per Attempt</h3>
        <canvas ref="barRef"></canvas>
      </div>

      <div class="card chart-card">
        <h3>Score Distribution</h3>
        <canvas ref="pieRef"></canvas>
      </div>
    </section>

    <!-- LOADING -->
    <p v-if="loading" class="loading">Loading summary…</p>

    <!-- DATA TABLE -->
    <div v-else class="card">
      <div class="export-csv-bar">
        <button class="btn export" @click="exportUserCSV" :disabled="exporting">
          {{ exporting ? 'Exporting...' : 'Download My Quiz History (CSV)' }}
        </button>
      </div>
      <p v-if="!rows.length" class="empty">No quiz data yet.</p>
      <table v-else class="tbl">
        <thead>
          <tr><th>Date</th><th>Quiz</th><th>Score</th><th>%</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ fmtDate(r.attempted_at) }}</td>
            <td>{{ r.quiz_title ?? `Quiz #${r.quiz_id}` }}</td>
            <td>
              {{ r.total_score }}
              <template v-if="r.max_score">/ {{ r.max_score }}</template>
            </td>
            <td>{{ percent(r).toFixed(1) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import { Chart } from 'chart.js/auto'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'

const loading = ref(true)
const exporting = ref(false)
const rows = ref([])

const barRef = ref(null)
const pieRef = ref(null)
let barChart = null
let pieChart = null

const exportUserCSV = async () => {
  exporting.value = true
  try {
    await axios.post(`${API}/export/user-csv`, {}, {
      headers: { Authorization: `Bearer ${localStorage.token}` }
    })
    alert('Export started! Check your email soon.')
  } catch (e) {
    alert('Failed to start export')
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`${API}/scores`, {
      headers: { Authorization: `Bearer ${localStorage.token}` }
    })
    rows.value = data.scores || []
    if (rows.value.length) initCharts()
  } catch (err) {
    console.error("Failed to load scores:", err)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  barChart?.destroy()
  pieChart?.destroy()
})

const fmtDate = iso =>
  new Date(iso).toLocaleDateString(undefined, { dateStyle: 'medium' })

const percent = r =>
  r.max_score ? (r.total_score / r.max_score) * 100 : r.total_score

const totalPoints = computed(() =>
  rows.value.reduce((sum, r) => sum + r.total_score, 0)
)

const avgPercent = computed(() =>
  rows.value.length
    ? rows.value.reduce((sum, r) => sum + percent(r), 0) / rows.value.length
    : 0
)

const bestPercent = computed(() =>
  rows.value.reduce((max, r) => Math.max(max, percent(r)), 0)
)

function initCharts () {
  const sortedRows = [...rows.value].sort((a, b) => new Date(a.attempted_at) - new Date(b.attempted_at))
  const labels = sortedRows.map(r => fmtDate(r.attempted_at))
  const dataP  = sortedRows.map(r => +percent(r).toFixed(1))

  barChart = new Chart(barRef.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Score %', data: dataP, backgroundColor: '#3b82f6' }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  })

  const bands = [0, 0, 0, 0]
  dataP.forEach(p => {
    if (p < 40) bands[0]++
    else if (p < 60) bands[1]++
    else if (p < 80) bands[2]++
    else bands[3]++
  })

  pieChart = new Chart(pieRef.value, {
    type: 'doughnut',
    data: {
      labels: ['<40%', '40‑59%', '60‑79%', '80‑100%'],
      datasets: [{
        data: bands,
        backgroundColor: ['#f87171', '#fbbf24', '#34d399', '#3b82f6']
      }]
    },
    options: {
      responsive: true
    }
  })
}
</script>

<style scoped>
/* Export CSV */
.export-csv-bar {
  margin: 1.5rem 0 1rem 0;
  text-align: right;
}
.btn.export {
  background: #2563eb;
  color: #fff;
  border-radius: 6px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}
.btn.export:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* layout */
.sum-wrapper {
  max-width: 960px;
  margin: auto;
  padding: 2rem 1.25rem;
  font-family: 'Inter', sans-serif;
}
.title {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0 0 1.4rem;
  color: #1e293b;
}

/* stats bar */
.overall {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.2rem;
}
.stat {
  background: #f1f5f9;
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}
.stat h3 {
  margin: 0;
  font-size: 1.55rem;
  color: #2563eb;
}
.stat p {
  margin: .25rem 0 0;
  font-size: .9rem;
  color: #475569;
}

/* chart cards */
.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.2rem;
  margin-bottom: 1.4rem;
}
.chart-card {
  padding: 1rem;
}
.chart-card h3 {
  margin: 0 0 .75rem;
  font-size: 1.05rem;
  color: #1f2937;
  text-align: center;
}
canvas {
  width: 100% !important;
  max-height: 280px;
}

/* table */
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, .05);
  padding: 1rem;
}
.tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: .9rem;
}
.tbl th, .tbl td {
  padding: .65rem .8rem;
  border-bottom: 1px solid #f8fafc;
}
.tbl th {
  background: #f9fafb;
  text-align: left;
}
.tbl tr:nth-child(even) {
  background: #fafafa04;
}

.loading, .empty {
  text-align: center;
  padding: 2rem 0;
  color: #64748b;
  font-size: 1rem;
}
</style>
