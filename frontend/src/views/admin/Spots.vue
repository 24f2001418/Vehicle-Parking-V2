<template>
  <main class="spots-wrapper premium-ui">
    <section class="spots-card animate-fade">
      <h2 class="title">🛠️ Admin: Parking Spot Monitor</h2>

      <!-- Filter and refresh -->
      <div class="filter-row">
        <label>
          Lot:
          <select v-model="selectedLot" @change="fetchSpots">
            <option value="">All Lots</option>
            <option v-for="lot in lots" :key="lot.id" :value="lot.id">{{ lot.name }}</option>
          </select>
        </label>
        <button @click="fetchSpots" :disabled="loading">
          {{ loading ? 'Refreshing…' : '🔄 Refresh' }}
        </button>
        <span class="summary">
          Showing {{ spots.length }} spot{{ spots.length !== 1 ? 's' : '' }}
        </span>
      </div>

      <!-- Spot Table -->
      <table class="spot-table animate-slide">
        <thead>
          <tr>
            <th>#</th>
            <th>Lot</th>
            <th>Status</th>
            <th>Vehicle</th>
            <th>User</th>
            <th>Parked At</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="spot in spots" :key="spot.id" :class="{ occupied: spot.status === 'O' }">
            <td><strong>{{ spot.number }}</strong></td>
            <td>{{ getLotName(spot.lot_id) }}</td>
            <td>
              <span :class="['badge', badgeClass(spot.status)]">
                {{ statusLabel(spot.status) }}
              </span>
            </td>
            <td class="dim-text">
  {{ spot.status !== 'A' ? spot.vehicle_plate || '—' : '—' }}
</td>
<td class="dim-text">
  {{ spot.status !== 'A' ? spot.user_email || '—' : '—' }}
</td>
<td>
  {{ spot.status !== 'A' && spot.parked_at ? formatDate(spot.parked_at) : '—' }}
</td>
          </tr>
        </tbody>
      </table>

      <p v-if="!spots.length && !loading" class="no-data animate-pop">
        🚫 No spot data to show for this lot.
      </p>
    </section>
  </main>
</template>

<script>
export default {
  name: 'SpotsAdminView',
  data() {
    return {
      lots: [],
      spots: [],
      selectedLot: '',
      loading: false
    };
  },
  methods: {
    formatDate(ts) {
      return new Date(ts).toLocaleString();
    },
    getLotName(id) {
      const lot = this.lots.find(l => l.id === id);
      return lot ? lot.name : `Lot ${id}`;
    },
    badgeClass(status) {
      return { A: 'free', R: 'reserved', O: 'occupied' }[status] || 'unknown';
    },
    statusLabel(status) {
      return { A: 'Available', R: 'Reserved', O: 'Occupied' }[status] || 'Unknown';
    },
    async fetchLots() {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:5000/api/lots', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      this.lots = data.lots || [];
    },
    async fetchSpots() {
      const token = localStorage.getItem('token');
      this.loading = true;
      try {
        const url = this.selectedLot ? `http://127.0.0.1:5000/api/spots/${this.selectedLot}` : 'http://127.0.0.1:5000/api/spots';
        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        this.spots = data.spots || [];
      } catch (e) {
        alert('Failed to fetch spot data.');
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchLots();
    this.fetchSpots();
  }
};
</script>

<style scoped>
.premium-ui {
  min-height: 100vh;
  background: linear-gradient(135deg, #e6f0ff, #f8fbff);
  font-family: 'Poppins', sans-serif;
  padding: 2rem;
  color: #333;
}
.spots-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 1100px;
  margin: auto;
}
.title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
}
.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.filter-row select,
.filter-row button {
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  font-size: 1rem;
}
.filter-row button {
  background: #007bff;
  border: none;
  color: #fff;
  cursor: pointer;
}
.filter-row button:hover {
  background: #0056b3;
}
.summary {
  margin-left: auto;
  font-size: 0.9rem;
  font-weight: 500;
  color: #666;
}
.spot-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.spot-table th,
.spot-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
.spot-table tr.occupied {
  background: #fff6f6;
}
.dim-text {
  color: #555;
}
.badge {
  padding: 0.3rem 0.7rem;
  font-size: 0.85rem;
  border-radius: 5px;
  color: #fff;
  font-weight: 600;
}
.badge.free { background: #28a745; }
.badge.occupied { background: #dc3545; }
.badge.reserved { background: #ffc107; color: #333; }
.no-data {
  margin-top: 2rem;
  font-style: italic;
  text-align: center;
  color: #666;
}

/* Premium Animations */
.animate-fade { animation: fadeIn 0.6s ease-in; }
.animate-slide { animation: slideUp 0.5s ease-in-out; }
.animate-pop { animation: popIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes popIn { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
</style>
