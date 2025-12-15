<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1 class="title">Welcome to ParkEase</h1>
      <p class="subtitle">
        Effortlessly find and reserve parking spots near you.
      </p>
    </div>

    <!-- Active Bookings Dashboard -->
    <div v-if="activeBooking && !paymentModal" class="active-booking-section">
      <h2 class="section-title">🎯 Your Active Booking</h2>
      <div class="active-card">
        <div class="booking-info">
          <div class="info-row">
            <span class="label">Lot:</span>
            <span class="value">{{ activeBooking.lot_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Spot #:</span>
            <span class="value">{{ activeBooking.spot_number }}</span>
          </div>
          <div class="info-row">
            <span class="label">Started:</span>
            <span class="value">{{ formatDate(activeBooking.parked_at || activeBooking.created_at) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Duration:</span>
            <span class="value">{{ elapsed(activeBooking) }}</span>
          </div>
          <div class="info-row" v-if="activeBooking.cost != null">
            <span class="label">Current Cost:</span>
            <span class="value price">₹{{ activeBooking.cost.toFixed(2) }}</span>
          </div>
        </div>
        <div class="booking-actions">
          <button class="btn btn-primary" @click="endBooking(activeBooking)">
            {{ endingBooking ? 'Ending...' : '🛑 End Booking' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="paymentModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal-content" @click.stop>
        <h2 class="modal-title">💳 Payment Required</h2>
        
        <div class="payment-details">
          <div class="detail-row">
            <span class="label">Lot Name:</span>
            <span class="value">{{ paymentData.lot_name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Spot #:</span>
            <span class="value">{{ paymentData.spot_number }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Duration:</span>
            <span class="value">{{ paymentData.duration }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Start Time:</span>
            <span class="value">{{ paymentData.started }}</span>
          </div>
          <div class="detail-row">
            <span class="label">End Time:</span>
            <span class="value">{{ paymentData.ended }}</span>
          </div>
          <div class="divider"></div>
          <div class="detail-row total">
            <span class="label">Total Amount:</span>
            <span class="value amount">₹{{ paymentData.cost.toFixed(2) }}</span>
          </div>
        </div>

        <div class="payment-methods">
          <button class="payment-btn cash" @click="processPayment('cash')">
            💵 Pay Cash
          </button>
          <button class="payment-btn card" @click="processPayment('card')">
            💳 Pay Card
          </button>
          <button class="payment-btn upi" @click="processPayment('upi')">
            📱 Pay UPI
          </button>
        </div>

        <button class="btn-cancel" @click="closePaymentModal">Cancel</button>
      </div>
    </div>

    <div v-if="!paymentModal" class="action-cards">
      <router-link to="/parking" class="card">
        <h2>🚘 Book Parking</h2>
        <p>Select a lot, reserve a spot, and park stress-free.</p>
        <span class="cta">Start Booking →</span>
      </router-link>

      <router-link to="/history" class="card">
        <h2>📜 View History</h2>
        <p>Check your past reservations and total spent.</p>
        <span class="cta">View History →</span>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data() {
    return {
      activeBooking: null,
      endingBooking: false,
      refreshInterval: null,
      paymentModal: false,
      paymentData: null,
      processing: false
    };
  },
  computed: {
    token() {
      return localStorage.getItem('token');
    }
  },
  methods: {
    async fetchActiveBooking() {
      if (!this.token) return;
      try {
        const res = await fetch('http://127.0.0.1:5000/api/reservations', {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const data = await res.json();
        const reservations = data.reservations || [];
        
        // Find the active booking (parked but not left)
        const active = reservations.find(r => r.parked_at && !r.left_at);
        if (active) {
          this.activeBooking = {
            ...active,
            lot_name: active.lot_name || active.spot?.lot?.name || '—',
            spot_number: active.spot_number || active.spot?.number || '—'
          };
        } else {
          this.activeBooking = null;
        }
      } catch (e) {
        console.error('Failed to fetch active booking:', e);
      }
    },
    async endBooking(booking) {
      if (!confirm('End this booking and proceed to payment?')) return;
      this.endingBooking = true;
      try {
        const res = await fetch(`http://127.0.0.1:5000/api/reservations/${booking.id}/end`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
          }
        });
        const data = await res.json();
        if (!res.ok) throw data;
        
        // Show payment modal with booking details
        this.paymentData = {
          id: booking.id,
          lot_name: booking.lot_name,
          spot_number: booking.spot_number,
          cost: data.cost || 0,
          started: this.formatDate(booking.parked_at || booking.created_at),
          ended: new Date().toLocaleString(),
          duration: this.elapsed(booking)
        };
        this.paymentModal = true;
      } catch (e) {
        alert(e.msg || 'Failed to end booking');
      } finally {
        this.endingBooking = false;
      }
    },
    closePaymentModal() {
      this.paymentModal = false;
      this.paymentData = null;
      this.activeBooking = null;
      this.fetchActiveBooking();
    },
    async processPayment(method) {
      if (this.processing) return;
      this.processing = true;
      
      try {
        alert(`Processing ${method.toUpperCase()} payment of ₹${this.paymentData.cost.toFixed(2)}...`);
        
        // Here you would integrate with a real payment gateway
        // For now, we'll just simulate success
        setTimeout(() => {
          alert(`✅ Payment via ${method.toUpperCase()} successful!`);
          this.closePaymentModal();
        }, 1000);
      } catch (e) {
        alert('Payment processing failed: ' + (e.msg || 'Unknown error'));
      } finally {
        this.processing = false;
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
    }
  },
  mounted() {
    this.fetchActiveBooking();
    // Refresh active booking every 30 seconds
    this.refreshInterval = setInterval(() => {
      this.fetchActiveBooking();
    }, 30000);
  },
  beforeUnmount() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
  }
};
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #222;
}

.welcome-section {
  text-align: center;
  margin-bottom: 3rem;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.2rem;
  color: #666;
  margin-top: 0.75rem;
  font-weight: 500;
}

.active-booking-section {
  margin-bottom: 4rem;
}

.section-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
}

.active-card {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
  border-radius: 16px;
  padding: 2rem;
  color: white;
  box-shadow: 0 12px 30px rgba(255, 152, 0, 0.3);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2.5rem;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.booking-info {
  display: grid;
  gap: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.05rem;
  background: rgba(255, 255, 255, 0.15);
  padding: 0.8rem 1rem;
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

.label {
  font-weight: 700;
  opacity: 0.95;
}

.value {
  font-weight: 600;
  text-align: right;
}

.value.price {
  font-size: 1.4rem;
  font-weight: 800;
}

.booking-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  padding: 0.9rem 1.8rem;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 1rem;
}

.btn-primary {
  background: #dc3545;
  color: white;
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.3);
}

.btn-primary:hover {
  background: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(220, 53, 69, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: translateY(-2px);
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  text-decoration: none;
  color: #000;
  border: 2px solid #e0e7ff;
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 123, 255, 0.15);
  border-color: #007bff;
}

.card h2 {
  margin-bottom: 0.75rem;
  font-size: 1.5rem;
  color: #0c4a6e;
  font-weight: 700;
}

.card p {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.cta {
  display: inline-block;
  margin-top: 1rem;
  font-weight: 700;
  color: #007bff;
  transition: all 0.3s ease;
}

.card:hover .cta {
  transform: translateX(4px);
}

/* Payment Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 2.5rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.payment-details {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 0;
  font-size: 0.95rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row.total {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 1rem;
  margin: 1rem -1.5rem -1.5rem -1.5rem;
  border-radius: 0 0 12px 12px;
}

.detail-row .label {
  font-weight: 700;
  color: #666;
}

.detail-row.total .label {
  color: white;
}

.detail-row .value {
  font-weight: 600;
  color: #333;
  text-align: right;
}

.detail-row.total .value {
  color: white;
}

.detail-row .value.amount {
  font-size: 1.4rem;
  font-weight: 800;
}

.divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
  margin: 0.8rem 0;
}

.payment-methods {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.payment-btn {
  padding: 1rem;
  border: 2px solid #e0e7ff;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.payment-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.payment-btn.cash {
  border-color: #28a745;
  color: #28a745;
}

.payment-btn.cash:hover {
  background: #e6f5ea;
}

.payment-btn.card {
  border-color: #007bff;
  color: #007bff;
}

.payment-btn.card:hover {
  background: #e7f1ff;
}

.payment-btn.upi {
  border-color: #ff9800;
  color: #ff9800;
}

.payment-btn.upi:hover {
  background: #fff3e0;
}

.btn-cancel {
  width: 100%;
  padding: 0.9rem;
  background: #f0f0f0;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  color: #666;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: 2rem 1rem;
  }

  .title {
    font-size: 2.2rem;
  }

  .active-card {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .booking-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .action-cards {
    grid-template-columns: 1fr;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .payment-methods {
    grid-template-columns: 1fr;
  }
}
</style>
