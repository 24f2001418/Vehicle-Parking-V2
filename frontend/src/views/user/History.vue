<template>
  <main class="history-container premium-ui">
    <h2 class="heading animate-fade">🗂️ Reservation History</h2>
    <div class="export-row">
      <button class="link-btn" @click="startExport" :disabled="exportLoading">
        {{ exportLoading ? 'Exporting…' : 'Export My Bookings (CSV)' }}
      </button>
      <span v-if="exportStatus" class="export-status">{{ exportStatus }}</span>
    </div>

    <!-- Loading spinner -->
    <div v-if="loading" class="loader animate-fade">Loading…</div>

    <!-- Empty state -->
    <div v-else-if="reservations.length === 0" class="empty-state animate-pop">
      <p>No reservations yet. Go book your first spot! 🚗</p>
      <router-link to="/parking" class="link-btn">Book Now</router-link>
    </div>

    <!-- History list -->
    <ul v-else class="history-list animate-slide">
      <li
        v-for="res in reservations"
        :key="res.id"
        class="history-card"
        :class="statusClass(res)"
      >
        <div class="card-header">
          <h3 class="lot-name">{{ res.lot_name }}</h3>
          <span class="status-badge">{{ humanStatus(res) }}</span>
        </div>
        <p><strong>Spot:</strong> #{{ res.spot_number }}</p>
        <p>
          <strong>Start:</strong>
          {{ formatDate(res.parked_at || res.created_at) }}
        </p>
        <p>
          <strong>
            {{ res.left_at ? 'End:' : 'Elapsed:' }}
          </strong>
          {{ res.left_at ? formatDate(res.left_at) : elapsed(res) }}
        </p>
        <p v-if="res.cost != null" class="cost">
          Paid: ₹{{ res.cost.toFixed(2) }}
        </p>
      </li>
    </ul>
  </main>
</template>

<script>
export default {
  name: 'HistoryView',
  data() {
    return {
      loading: true,
      reservations: [],
      exportLoading: false,
      exportTaskId: null,
      exportStatus: '',
    };
  },
  computed: {
    token() {
      return localStorage.getItem('token');
    },
  },
  methods: {
    async fetchHistory() {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/reservations', {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const data = await res.json();
        this.reservations = (data.reservations || []).map((r) => ({
          ...r,
          // for convenience: flatten nested objects if backend already provides
          lot_name: r.lot_name || r.spot?.lot?.name || '—',
          spot_number: r.spot_number || r.spot?.number || '—',
          created_at: r.created_at || r.reserved_at || r.parked_at,
        }));
      } catch (e) {
        console.error(e);
        alert('Failed to load history');
      } finally {
        this.loading = false;
      }
    },
    formatDate(dt) {
      if (!dt) return '—';
      return new Date(dt).toLocaleString();
    },
    elapsed(res) {
      if (!res.parked_at) return '—';
      const ms = Date.now() - new Date(res.parked_at).getTime();
      const h = Math.floor(ms / 3600000);
      const m = Math.floor((ms % 3600000) / 60000);
      return `${h}h ${m}m`;
    },
    humanStatus(res) {
      if (res.left_at) return 'Completed';
      if (res.parked_at) return 'Active';
      return 'Reserved';
    },
    statusClass(res) {
      return {
        completed: !!res.left_at,
        active: !res.left_at && !!res.parked_at,
        reserved: !res.parked_at,
      };
    },
    async startExport() {
      if (!this.token) return alert('Please login');
      this.exportLoading = true;
      this.exportStatus = 'Starting export...';
      try {
        const res = await fetch('http://127.0.0.1:5000/api/reports/export', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token}` },
          body: JSON.stringify({ format: 'csv' })
        });
        const data = await res.json();
        if (!res.ok) throw data;
        this.exportTaskId = data.task_id;
        this.exportStatus = 'Export queued';
      } catch (e) {
        console.error(e);
        this.exportStatus = 'Failed to start export';
        this.exportLoading = false;
      }
    },
    async pollExportStatus(taskId) {
      const interval = 3000;
      const maxTries = 40; // ~2 minutes
      let tries = 0;
      const id = setInterval(async () => {
        tries++;
        try {
          const res = await fetch(`/api/reports/status/${taskId}`, {
            headers: { Authorization: `Bearer ${this.token}` }
          });
          const data = await res.json();
          if (data.state === 'SUCCESS') {
            clearInterval(id);
            this.exportLoading = false;
            this.exportStatus = 'Export ready';
            if (data.download_urls && data.download_urls.length) {
              // open first url
              window.open(data.download_urls[0], '_blank');
            }
          } else if (data.state === 'FAILURE') {
            clearInterval(id);
            this.exportLoading = false;
            this.exportStatus = 'Export failed';
          } else {
            this.exportStatus = `Export ${data.state}`;
          }
          if (tries > maxTries) {
            clearInterval(id);
            this.exportLoading = false;
            this.exportStatus = 'Export timed out';
          }
        } catch (e) {
          console.error(e);
        }
      }, interval);
    }
  },
  mounted() {
    if (this.token) this.fetchHistory();
  },
  watch: {
    exportTaskId(newId) {
      if (newId) this.pollExportStatus(newId);
    }
  }
};
</script>

<style scoped>
.history-container {
  padding: 2rem;
}
.loader {
  text-align: center;
  font-size: 1.1rem;
}
.empty-state {
  text-align: center;
  margin-top: 3rem;
}
.link-btn {
  display: inline-block;
  margin-top: 1rem;
  background: #007bff;
  color: #fff;
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
}
.history-list {
  display: grid;
  gap: 1rem;
}
.history-card {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  padding: 1rem 1.2rem;
  position: relative;
}
.history-card.completed { border-left: 6px solid #28a745; }
.history-card.active    { border-left: 6px solid #ffc107; }
.history-card.reserved  { border-left: 6px solid #17a2b8; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.status-badge {
  font-size: 0.8rem;
  background: #e9ecef;
  padding: 0.2rem 0.6rem;
  border-radius: 0.4rem;
}
.cost {
  margin-top: 0.4rem;
  font-weight: 600;
}
/* Animations (re‑use from premium UI) */
.animate-fade { animation: fadeIn 0.6s ease-in; }
.animate-slide { animation: slideInUp 0.6s ease; }
.animate-pop { animation: popIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideInUp { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes popIn { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
</style>
