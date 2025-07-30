<template>
  <main class="summary-wrapper">
    <h1 class="title">Quiz Summary Report</h1>

    <!-- OVERALL STATS -->
    <section v-if="!loading && rows.length" class="summary-stats">
      <article class="stat"><h3>{{ rows.length }}</h3><p>Attempts</p></article>
      <article class="stat"><h3>{{ totalPoints }}</h3><p>Total Points</p></article>
      <article class="stat"><h3>{{ avgPercent.toFixed(1) }}%</h3><p>Average Score</p></article>
      <article class="stat"><h3>{{ bestPercent.toFixed(1) }}%</h3><p>Best Score</p></article>
    </section>

    <!-- CHARTS -->
    <section v-if="!loading && rows.length" class="chart-section">
      <div class="card chart-card">
        <h3>Performance Over Time</h3>
        <canvas ref="barRef"></canvas>
      </div>

      <div class="card chart-card">
        <h3>Score Distribution</h3>
        <canvas ref="pieRef"></canvas>
      </div>
    </section>

    <!-- LOADING -->
    <p v-if="loading" class="loading">Loading summary...</p>

    <!-- DATA TABLE -->
    <div v-else class="card">
      <div class="export-controls">
        <button class="btn export" @click="exportUserCSV" :disabled="exporting">
          {{ exporting ? 'Exporting...' : 'Download Quiz History (CSV)' }}
        </button>
      </div>
      <p v-if="!rows.length" class="no-data">No quiz data available.</p>
      <table v-else class="data-table">
        <thead>
          <tr><th>Date</th><th>Quiz</th><th>Score</th><th>%</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ fmtDate(r.attempted_at) }}</td>
            <td>{{ r.quiz_title ?? `Quiz  ${r.quiz_id}` }}</td>
            <td>{{ r.total_score }}<template v-if="r.max_score">/ {{ r.max_score }}</template></td>
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
    alert('Export initiated. Check your email shortly.')
  } catch (e) {
    alert('Export failed. Please try again later.')
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

const fmtDate = iso => new Date(iso).toLocaleDateString(undefined, { dateStyle: 'medium' })

const percent = r => {
  if (!r.max_score || r.max_score === 0) return 0
  return (r.total_score / r.max_score) * 100
}

const totalPoints = computed(() => rows.value.reduce((sum, r) => sum + r.total_score, 0))
const avgPercent = computed(() => rows.value.length ? rows.value.reduce((sum, r) => sum + percent(r), 0) / rows.value.length : 0)
const bestPercent = computed(() => rows.value.reduce((max, r) => Math.max(max, percent(r)), 0))

if (barChart) {
  barChart.destroy()
  barChart = null
}
if (pieChart) {
  pieChart.destroy()
  pieChart = null
}
function initCharts () {
  const sorted = [...rows.value].sort((a, b) => new Date(a.attempted_at) - new Date(b.attempted_at))
  const labels = sorted.map(r => fmtDate(r.attempted_at))
  const dataP  = sorted.map(r => +percent(r).toFixed(1))

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
    options: { responsive: true }
  })
}
</script>

<style scoped>
.summary-wrapper {
  max-width: 960px;
  margin: auto;
  padding: 2rem 1.25rem;
  font-family: 'Inter', sans-serif;
}
.title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1e293b;
  text-align: center;
}
.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.stat {
  background: #f1f5f9;
  border-radius: 10px;
  padding: 1rem;
}
.stat h3 {
  font-size: 1.6rem;
  color: #2563eb;
  margin: 0;
}
.stat p {
  margin-top: 0.25rem;
  font-size: 0.9rem;
  color: #475569;
}
.chart-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}
.chart-card {
  padding: 1rem;
}
.chart-card h3 {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  color: #1f2937;
}
canvas {
  width: 100% !important;
  max-height: 280px;
}
.export-controls {
  text-align: right;
  margin: 1.5rem 0 1rem;
}
.btn.export {
  background: linear-gradient(90deg, #2563eb 60%, #1e40af 100%);
  color: white;
  border: none;
  padding: 0.55rem 1.3rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(37,99,235,0.08);
  transition: background 0.2s, box-shadow 0.2s;
}
.btn.export:hover:not(:disabled) {
  background: linear-gradient(90deg, #1e40af 60%, #2563eb 100%);
  box-shadow: 0 4px 16px rgba(37,99,235,0.13);
}
.btn.export:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}
.data-table th, .data-table td {
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid #f1f5f9;
}
.data-table th {
  background-color: #f9fafb;
  text-align: left;
}
.data-table tr:nth-child(even) {
  background-color: #fafafa;
}
.loading, .no-data {
  text-align: center;
  font-size: 1rem;
  color: #64748b;
  padding: 2rem 0;
}
@media (max-width: 600px) {
  .summary-wrapper {
    padding: 1rem 0.5rem;
  }
  .summary-stats {
    grid-template-columns: 1fr 1fr;
  }
  .chart-section {
    grid-template-columns: 1fr;
  }
  .data-table th, .data-table td {
    padding: 0.4rem 0.3rem;
    font-size: 0.9rem;
  }
}
</style>
