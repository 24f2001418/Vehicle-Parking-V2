<template>
  <main class="summary-wrapper">
    <section class="summary-card">
      <h2 class="title">Occupancy Summary</h2>

      <div class="charts-grid">
        <!-- Bar: per‑lot -->
        <div class="chart-box">
          <canvas ref="barEl"></canvas>
        </div>
        <!-- Doughnut: overall -->
        <div class="chart-box">
          <canvas ref="donutEl"></canvas>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  DoughnutController,
  ArcElement,
  Legend,
  Tooltip
} from 'chart.js'

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  DoughnutController,
  ArcElement,
  Legend,
  Tooltip
)

export default {
  name: 'SummaryAdminView',
  data() {
    return {
      lots: [],
      barChart: null,
      donutChart: null
    }
  },
  methods: {
    /* Fetch lots & build charts */
    async fetchLots() {
      const token = localStorage.getItem('token')
      const res = await fetch('http://127.0.0.1:5000/api/lots', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const data = await res.json()
      this.lots = data.lots || []
      this.drawCharts()
    },

    /* Draw both charts */
    drawCharts() {
      // Dispose old charts
      this.barChart && this.barChart.destroy()
      this.donutChart && this.donutChart.destroy()

      /* -------- prepare data -------- */
      const labels = this.lots.map(l => l.name)
      const occupied = this.lots.map(l => l.occupied || 0)
      const free = this.lots.map(l => l.number_of_spots - (l.occupied || 0))

      /* -------- bar chart -------- */
      this.barChart = new Chart(this.$refs.barEl, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Occupied', data: occupied, stack: 's1' },
            { label: 'Free', data: free, stack: 's1' }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } }
        }
      })

      /* -------- doughnut chart -------- */
      const totalOcc = occupied.reduce((a, b) => a + b, 0)
      const totalFree = free.reduce((a, b) => a + b, 0)

      this.donutChart = new Chart(this.$refs.donutEl, {
        type: 'doughnut',
        data: {
          labels: ['Occupied', 'Free'],
          datasets: [{ data: [totalOcc, totalFree] }]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom' } }
        }
      })
    }
  },
  mounted() {
    this.fetchLots()
  }
}
</script>

<style scoped>
.summary-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f3f6fb;
  padding: 2rem;
}

.summary-card {
  width: 100%;
  max-width: 960px;
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
}

.charts-grid {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.chart-box {
  background: #fafafa;
  border-radius: 12px;
  padding: 1rem;
}
</style>
