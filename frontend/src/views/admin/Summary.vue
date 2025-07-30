<template>
  <main class="admin-summary-wrapper">
    <h1 class="title">User Performance Analytics</h1>

    <!-- Leaderboard -->
    <section class="leaderboard-section">
      <h2>Leaderboard</h2>
      <table class="leaderboard">
        <thead>
          <tr><th>Rank</th><th>User</th><th>Total Score</th><th>Attempts</th><th>Avg %</th></tr>
        </thead>
        <tbody>
          <tr v-for="(user, idx) in leaderboard" :key="user.id">
            <td>{{ idx + 1 }}</td>
            <td>{{ user.full_name }}</td>
            <td>{{ user.total_score }}</td>
            <td>{{ user.attempts }}</td>
            <td>{{ user.avg_percent.toFixed(1) }}%</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Progress Tracking Charts -->
    <section class="charts-section">
      <h2>Progress Tracking</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>Top 5 Users - Score Progress</h3>
          <canvas ref="lineChartRef"></canvas>
        </div>
        <div class="chart-card">
          <h3>Quiz Attempts Distribution</h3>
          <canvas ref="barChartRef"></canvas>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const leaderboard = ref([])
const userProgress = ref([])
const quizAttempts = ref([])
const lineChartRef = ref(null)
const barChartRef = ref(null)
let lineChart, barChart

onMounted(async () => {
  // Fetch leaderboard and analytics data
  const { data } = await axios.get(`${API}/admin/analytics`, {
    headers: { Authorization: `Bearer ${localStorage.token}` }
  })
  leaderboard.value = data.leaderboard
  userProgress.value = data.user_progress
  quizAttempts.value = data.quiz_attempts
  initCharts()
})

function initCharts() {
  // Line chart: Top 5 users' score progress
  const topUsers = userProgress.value.slice(0, 5)
  const labels = topUsers[0]?.progress.map(p => p.date) || []
  const datasets = topUsers.map(user => ({
    label: user.full_name,
    data: user.progress.map(p => p.score),
    fill: false
  }))
  if (lineChart) lineChart.destroy()
  lineChart = new Chart(lineChartRef.value, {
    type: 'line',
    data: { labels, datasets },
    options: { responsive: true }
  })

  // Bar chart: Quiz attempts distribution
  const barLabels = quizAttempts.value.map(q => q.quiz_title)
  const barData = quizAttempts.value.map(q => q.attempts)
  if (barChart) barChart.destroy()
  barChart = new Chart(barChartRef.value, {
    type: 'bar',
    data: { labels: barLabels, datasets: [{ label: 'Attempts', data: barData }] },
    options: { responsive: true }
  })
}
</script>

<style scoped>
.admin-summary-wrapper {
  max-width: 1100px;
  margin: auto;
  padding: 2rem 1.5rem;
  font-family: 'Inter', sans-serif;
}
.title {
  font-size: 1.7rem;
  font-weight: 700;
  margin-bottom: 2rem;
  color: #1e293b;
}
.leaderboard-section {
  margin-bottom: 2.5rem;
}
.leaderboard {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.leaderboard th, .leaderboard td {
  padding: 0.7rem 1rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
.leaderboard th {
  background: #f1f5f9;
}
.charts-section {
  margin-top: 2.5rem;
}
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 2rem;
}
.chart-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,.05);
}
.chart-card h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
  color: #2563eb;
  text-align: center;
}
canvas {
  width: 100%!important;
  max-height: 320px;
}
</style>
