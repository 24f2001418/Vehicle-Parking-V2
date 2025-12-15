<template>
  <main class="lots-wrapper">
    <section class="lots-card">
      <h2 class="title">Manage Parking Lots</h2>

      <!-- Create or Update Lot Form -->
      <form @submit.prevent="saveLot" class="lot-form">
        <input v-model="newLot.name" placeholder="Lot Name" required />
        <input v-model.number="newLot.price" type="number" placeholder="Price/hour" required />
        <input v-model="newLot.address" placeholder="Address" />
        <input v-model="newLot.pin_code" placeholder="Pin Code" />
        <input v-model.number="newLot.number_of_spots" type="number" placeholder="Number of Spots" required />
        <button :disabled="loading">
          {{ loading ? (lotIdBeingEdited ? 'Updating...' : 'Creating...') : (lotIdBeingEdited ? 'Save Changes' : 'Create Lot') }}
        </button>
      </form>

      <!-- Show Lots -->
      <ul v-if="lots.length">
        <li v-for="lot in lots" :key="lot.id" class="lot-item">
          <div class="lot-info">
            <strong>{{ lot.name }}</strong> — ₹{{ lot.price }}/hr <br />
            {{ lot.address }}| Pin: {{ lot.pin_code }} <br/>
            Spots: {{ lot.number_of_spots }}
          </div>
          <div class="lot-actions">
            <button @click="editLot(lot)">Edit</button>
            <button @click="deleteLot(lot.id)">Delete</button>
          </div>
        </li>
      </ul>

      <p v-if="!lots.length">No parking lots available.</p>
    </section>
  </main>
</template>

<script>
export default {
  name: 'LotsAdminView',
  data() {
    return {
      lots: [],
      newLot: {
        name: '',
        price: '',
        address: '',
        pin_code: '',
        number_of_spots: ''
      },
      lotIdBeingEdited: null,
      loading: false
    };
  },
  methods: {
    async fetchLots() {
      const token = localStorage.getItem('token');
      const res = await fetch('http://127.0.0.1:5000/api/lots', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      this.lots = data.lots || [];
    },
    async saveLot() {
      const token = localStorage.getItem('token');
      this.loading = true;
      try {
        const method = this.lotIdBeingEdited ? 'PUT' : 'POST';
        const url = this.lotIdBeingEdited
          ? `/api/lots/${this.lotIdBeingEdited}`
          : 'http://127.0.0.1:5000/api/lots';

        const res = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify(this.newLot)
        });

        const result = await res.json();
        if (res.ok) {
          alert(this.lotIdBeingEdited ? 'Lot updated!' : 'Lot created!');
          this.fetchLots();
          this.resetForm();
        } else {
          alert(result.msg || 'Failed to save lot');
        }
      } catch (e) {
        alert('Error saving lot');
      } finally {
        this.loading = false;
      }
    },
    async deleteLot(id) {
      if (!confirm('Delete this lot?')) return;
      const token = localStorage.getItem('token');
      const res = await fetch(`http://127.0.0.1:5000/api/lots/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      alert(data.msg || 'Lot deleted');
      this.fetchLots();
    },
    editLot(lot) {
      this.newLot = {
        name: lot.name,
        price: lot.price,
        address: lot.address,
        pin_code: lot.pin_code,
        number_of_spots: lot.number_of_spots
      };
      this.lotIdBeingEdited = lot.id;
    },
    resetForm() {
      this.newLot = {
        name: '',
        price: '',
        address: '',
        pin_code: '',
        number_of_spots: ''
      };
      this.lotIdBeingEdited = null;
    }
  },
  mounted() {
    this.fetchLots();
  }
};
</script>

<style scoped>
.lots-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f3f6fb;
  padding: 2rem;
}

.lots-card {
  width: 100%;
  max-width: 720px;
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.lot-form {
  display: grid;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.lot-form input {
  padding: 0.7rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.lot-form button {
  padding: 0.75rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.lot-form button:hover {
  background: #0056b3;
}

.lot-item {
  padding: 1rem;
  border: 1px solid #ddd;
  margin-bottom: 1rem;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lot-actions button {
  margin-left: 0.5rem;
  background: #ff6b6b;
  color: white;
  padding: 0.5rem 0.8rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.lot-actions button:first-child {
  background: #28a745;
}
</style>
