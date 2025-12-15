<template>
  <main class="parking-container premium-ui">
    <!-- STEP 1: Choose Lot -->
    <section v-if="stage === 'lots'" class="stage-chooser">
      <h2 class="heading animate-fade">Select Parking Lot</h2>

      <!-- Location Search Input -->
      <div class="search-location">
        <label for="userLocation">Enter Your Location</label>
        <input
          id="userLocation"
          v-model="userLocation"
          type="text"
          placeholder="e.g., MG Road, Bangalore"
        />
        <button class="btn-search" @click="fetchNearbyLots">🔍 Search</button>
      </div>

      <!-- Nearby Parking Lots -->
      <ul class="lot-list animate-slide">
        <li
          v-for="lot in lots"
          :key="lot.id"
          class="lot-card"
          @click="chooseLot(lot)"
        >
          <div class="lot-card-inner">
            <h3>{{ lot.name }}</h3>
            <p class="price">₹{{ lot.price }}/hr</p>
            <p class="address">📍 {{ lot.address || '—' }}</p>
          </div>
        </li>
      </ul>
    </section>

    <!-- STEP 2: Spot Selection -->
    <!-- STEP 2: Confirm booking (no spot grid shown) -->
    <section v-else-if="stage === 'confirm'" class="confirm-book animate-fade">
      <header class="seat-map-header">
        <button class="back-btn" @click="resetLot">← Back</button>
        <div>
          <h2 class="heading">{{ currentLot.name }}</h2>
          <p class="sub">Enter your details and confirm booking — we'll assign the first available slot</p>
        </div>
      </header>

      <div class="confirm-form">
        <label>Name: <input v-model="userName" placeholder="Your Name" /></label>
        <label>Vehicle No: <input v-model="vehicleNumber" placeholder="KA01AB1234" /></label>
        <p class="cost">Estimated cost: ₹{{ currentLot.price }}/hr</p>
        <button class="confirm-btn" @click="confirmBooking" :disabled="booking || !userName || !vehicleNumber">
          {{ booking ? 'Booking…' : '✅ Book Spot' }}
        </button>
      </div>

      <!-- Toast notification -->
      <div v-if="toastVisible" class="toast">
        {{ toastMessage }}
      </div>

    </section>

    <section v-else-if="stage === 'spots'" class="seat-map animate-fade">
      <header class="seat-map-header">
        <button class="back-btn" @click="resetLot">← Back</button>
        <div>
          <h2 class="heading">{{ currentLot.name }}</h2>
          <p class="sub">Select a spot below</p>
        </div>
      </header>

      <div class="legend">
        <span><i class="box available"></i> Available</span>
        <span><i class="box selected"></i> Selected</span>
        <span><i class="box occupied"></i> Occupied</span>
        <span><i class="box reserved"></i> Reserved</span>
      </div>

      <div class="grid spot-grid animate-slide">
        <button
          v-for="spot in spots"
          :key="spot.id"
          class="spot-btn"
          :class="statusClass(spot)"
          :disabled="spot.status !== 'A' && !isSelected(spot)"
          @click="toggleSelect(spot)"
        >
          {{ spot.number }}
        </button>
      </div>

      <!-- Bottom Bar for booking -->
      <transition name="slide-up">
        <footer v-if="selectedSpot" class="ticket-bar animate-pop">
          <div class="ticket-info">
            <p>You selected <strong>Spot #{{ selectedSpot.number }}</strong></p>
            <label>Name: <input v-model="userName" placeholder="Your Name" /></label>
            <label>Vehicle No: <input v-model="vehicleNumber" placeholder="KA01AB1234" /></label>
            <p><strong>Time:</strong> {{ bookingTime }}</p>
            <p class="cost">Estimated cost: ₹{{ currentLot.price }}/hr</p>
          </div>
          <button class="confirm-btn" @click="bookSpot" :disabled="booking || !userName || !vehicleNumber">
            {{ booking ? 'Booking…' : '✅ Confirm Booking' }}
          </button>
        </footer>
      </transition>
    </section>

    <!-- STEP 3: Active Reservation -->
    <section v-else-if="stage === 'active'" class="active-reservation animate-fade">
      <h2 class="heading">🅿️ Active Parking</h2>
      <div class="summary">
        <p><strong>Lot:</strong> {{ currentLot.name }}</p>
        <p><strong>Spot:</strong> {{ selectedSpot.number }}</p>
        <p><strong>Started:</strong> {{ bookingTime }}</p>
        <p><strong>Elapsed:</strong> {{ elapsedText }}</p>
        <p class="cost">Current cost ({{ currentLot.price }}/hr): <strong>₹{{ runningCost }}</strong></p>
      </div>
      <button class="confirm-btn finish-btn" :disabled="releaseLoading" @click="endBooking">
        {{ releaseLoading ? 'Releasing…' : '💳 Release & Pay' }}
      </button>
    </section>

    <!-- STEP 4: Payment -->
    <section v-else-if="stage === 'pay'" class="payment-screen animate-pop">
      <h2 class="heading">Payment</h2>
      <p class="pay-amount">Amount due: <strong>₹{{ paymentAmount }}</strong></p>
      <p class="pay-note">Please choose a payment method:</p>

      <div class="pay-options">
        <button class="pay-btn" @click="completePayment('UPI')">UPI</button>
        <button class="pay-btn" @click="completePayment('Credit Card')">Credit&nbsp;Card</button>
        <button class="pay-btn" @click="completePayment('Cash')">Cash</button>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: 'ParkingView',
  data() {
    return {
      stage: 'lots',
      toastMessage: '',
      toastVisible: false,
      userLocation: '',
      lots: [],
      currentLot: null,
      selectedLotId: null,
      spots: [],
      selectedSpot: null,
      userName: '',
      vehicleNumber: '',
      bookingTime: '',
      reservationId: null,
      timer: null,
      startTimestamp: null,
      elapsedMs: 0,
      booking: false,
      releaseLoading: false,
      paymentAmount: '0.00', // NEW
    };
  },
  computed: {
    token() {
      return localStorage.getItem('token');
    },
    elapsedText() {
      const sec = Math.floor(this.elapsedMs / 1000);
      const h = Math.floor(sec / 3600);
      const m = Math.floor((sec % 3600) / 60);
      const s = sec % 60;
      return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    },
    runningCost() {
      if (!this.currentLot) return '0.00';
      const hours = this.elapsedMs / 3600000;
      return (hours * this.currentLot.price).toFixed(2);
    },
  },
  watch: {
    token(newVal) {
      if (newVal) this.fetchLots();
    },
  },
  methods: {
    async fetchNearbyLots() {
      if (!this.token) return;
      const q = this.userLocation.trim();
      const url = q ? `http://127.0.0.1:5000/api/lots?near=${encodeURIComponent(q)}` : 'http://127.0.0.1:5000/api/lots';
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${this.token}` },
      });
      const data = await res.json();
      this.lots = data.lots || [];
    },
    async fetchLots() {
      if (!this.token) return;
      const res = await fetch('http://127.0.0.1:5000/api/lots', {
        headers: { Authorization: `Bearer ${this.token}` },
      });
      const data = await res.json();
      this.lots = data.lots || [];
    },
    async chooseLot(lot) {
      // When a lot is chosen, go to a confirmation form (no spot grid shown)
      this.currentLot = lot;
      this.selectedLotId = lot.id;
      this.selectedSpot = null;
      this.bookingTime = '';
      this.userName = '';
      this.vehicleNumber = '';
      this.stage = 'confirm';
    },
    async fetchSpots(lotId) {
      const res = await fetch(`/api/spots/${lotId}`, {
        headers: { Authorization: `Bearer ${this.token}` },
      });
      const data = await res.json();
      this.spots = data.spots || [];
    },
    statusClass(spot) {
      if (this.isSelected(spot)) return 'selected';
      return { A: 'available', R: 'reserved', O: 'occupied' }[spot.status] || 'available';
    },
    toggleSelect(spot) {
      if (spot.status !== 'A' && !this.isSelected(spot)) return;
      this.selectedSpot = this.isSelected(spot) ? null : spot;
      this.bookingTime = new Date().toISOString();
    },
    isSelected(spot) {
      return this.selectedSpot && this.selectedSpot.id === spot.id;
    },
    async bookSpot() {
      if (!this.selectedSpot) return;
      this.booking = true;
      try {
        const res = await fetch('http://127.0.0.1:5000/api/reservations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          },
          body: JSON.stringify({
            lot_id: this.selectedLotId,
            spot_id: this.selectedSpot.id,
            name: this.userName,
            vehicle_plate: this.vehicleNumber,
            start_time: this.bookingTime,
          }),
        });
        const data = await res.json();
        if (!res.ok) throw data;
        this.selectedSpot.status = 'O';
        this.reservationId = data.reservation.id;
        this.stage = 'active';
        this.startTimer();
      } catch (e) {
        this.showToast(e.msg || 'Booking failed');
      } finally {
        this.booking = false;
      }
    },
    
    async confirmBooking() {
      // Book without selecting a spot; backend will assign the first available
      this.booking = true;
      this.bookingTime = new Date().toISOString();
      try {
        const res = await fetch('http://127.0.0.1:5000/api/reservations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          },
          body: JSON.stringify({
            lot_id: this.selectedLotId,
            // omit spot_id so server assigns one
            name: this.userName || null,
            vehicle_plate: this.vehicleNumber || null,
            start_time: this.bookingTime,
          }),
        });
        const data = await res.json();
        if (!res.ok) throw data;
        // response includes assigned spot
        this.selectedSpot = data.spot || null;
        this.reservationId = data.reservation.id;
        this.stage = 'active';
        this.startTimer();
        this.showToast('Booking successful — spot assigned')
      } catch (e) {
        this.showToast(e.msg || 'Booking failed');
      } finally {
        this.booking = false;
      }
    },

    showToast(msg, ms = 3500) {
      this.toastMessage = msg;
      this.toastVisible = true;
      setTimeout(() => {
        this.toastVisible = false;
        this.toastMessage = '';
      }, ms);
    },
    startTimer() {
      this.startTimestamp = Date.now();
      this.elapsedMs = 0;
      this.timer && clearInterval(this.timer);
      this.timer = setInterval(() => {
        this.elapsedMs = Date.now() - this.startTimestamp;
      }, 1000);
    },
    async endBooking() {
      if (!this.reservationId) return;
      this.releaseLoading = true;
      try {
        const res = await fetch(`/api/reservations/${this.reservationId}/end`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const data = await res.json();
        if (!res.ok) throw data;
        clearInterval(this.timer);
        this.paymentAmount = data.reservation.cost || '0.00'; // NEW
        this.stage = 'pay'; // NEW
      } catch (e) {
        this.showToast(e.msg || 'Could not release spot');
      } finally {
        this.releaseLoading = false;
      }
    },
    completePayment(method) {
      this.showToast(`Payment of ₹${this.paymentAmount} received via ${method}. Thank you!`);
      this.resetLot();
      this.stage = 'lots';
      this.fetchLots();
    },
    resetLot() {
      this.selectedLotId = null;
      this.currentLot = null;
      this.spots = [];
      this.selectedSpot = null;
      this.userName = '';
      this.vehicleNumber = '';
      this.bookingTime = '';
      this.reservationId = null;
      this.timer && clearInterval(this.timer);
      this.elapsedMs = 0;
      this.paymentAmount = '0.00';
    },
  },
  mounted() {
    if (this.token) this.fetchLots();
  },
  beforeUnmount() {
    this.timer && clearInterval(this.timer);
  },
};
</script>

<style scoped>
.premium-ui {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(to right, #f7f9fc, #eef1f7);
  color: #333;
  padding: 2rem;
}
.heading {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
.lot-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  margin-bottom: 1rem;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.lot-card:hover {
  transform: scale(1.02);
}
.spot-btn {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  font-weight: bold;
}
.spot-btn.available { background: #d3f9d8; }
.spot-btn.selected { background: #82cfff; }
.spot-btn.occupied { background: #ff6b6b; cursor: not-allowed; }
.spot-btn.reserved { background: #ffd166; cursor: not-allowed; }
.ticket-bar, .active-reservation {
  margin-top: 2rem;
  background: #ffffff;
  padding: 1rem;
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.confirm-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 480px;
  margin-top: 1.25rem;
}
.confirm-form input {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 100%;
}
.toast {
  position: fixed;
  right: 20px;
  top: 20px;
  background: rgba(0,0,0,0.8);
  color: #fff;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.2);
}
.confirm-btn {
  background: #007bff;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}
.confirm-btn:hover {
  background: #0056b3;
}
.animate-fade { animation: fadeIn 0.6s ease-in; }
.animate-slide { animation: slideInUp 0.6s ease; }
.animate-pop { animation: popIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideInUp { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
@keyframes popIn { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
</style>
