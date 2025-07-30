<template>
  <div class="user-page">
    <header class="page-header">
      <button class="back-btn" @click="router.back()">← Back</button>
    </header>

    <!-- Controls -->
    <section class="controls">
      <input v-model="search" class="search" placeholder="Search by name or email…" />
      <select v-model="sortBy" class="sort">
        <option value="name">Name</option>
        <option value="role">Role</option>
        <option value="status">Status</option>
      </select>
    </section>

    <!-- User Cards -->
    <div class="user-cards" v-if="!loading">
      <div v-for="u in filtered" :key="u.id" class="user-card">
        <div class="user-header">
          <div class="user-name">{{ u.full_name }}</div>
          <span :class="['tag', u.is_active ? 'tag--inactive' : 'tag--active']">
            {{ u.is_active ? 'Inactive' : 'Active' }}
          </span>
        </div>

        <div class="user-details">
          <p><strong>Email:</strong> {{ u.email }}</p>
          <p><strong>Role:</strong> {{ u.role }}</p>
        </div>

        <div class="actions">
          <button
            class="btn tiny"
            :class="u.is_active ? 'warn' : 'green'"
            @click="openToggleModal(u)"
          >
          Deactivate
          </button>
          <button class="btn tiny danger" @click="openDeleteModal(u)">Delete</button>
        </div>
      </div>

      <p v-if="!filtered.length" class="empty">No users found.</p>
    </div>
    <div v-else class="loading">Loading…</div>

    <!-- Download CSV Button -->
    <div class="export-csv-bar">
      <button class="btn export" @click="exportAdminCSV" :disabled="exporting">
        {{ exporting ? 'Exporting...' : 'Download All User Performance (CSV)' }}
      </button>
    </div>

    <!-- Confirmation Modal -->
    <dialog ref="modalRef" class="modal">
      <form method="dialog" class="modal-box">
        <h3>{{ modal.title }}</h3>
        <p class="mb">{{ modal.message }}</p>
        <div class="modal-btns">
          <button class="btn" @click="modal.resolve(false)">Cancel</button>
          <button class="btn danger" :disabled="modal.busy" @click="modal.resolve(true)">
            {{ modal.busy ? 'Please wait…' : modal.okText }}
          </button>
        </div>
      </form>
    </dialog>

    <!-- Toast -->
    <transition name="fade">
      <div v-if="toast.msg" class="toast" :class="toast.type">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup>
const exporting = ref(false)

async function exportAdminCSV() {
  exporting.value = true
  try {
    await axios.post(`${API}/export/admin-csv`, {}, { headers: hdr() })
    showToast('Export started! Check your email soon.', 'success')
  } catch (e) {
    showToast('Failed to start export', 'error')
  } finally {
    exporting.value = false
  }
}
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:5000/api'
const router = useRouter()

const users   = ref([])
const loading = ref(true)
const search  = ref('')
const sortBy  = ref('name')

/* Toast */
const toast = ref({ msg: '', type: '' })
function showToast (msg, type = 'info', ms = 2500) {
  toast.value = { msg, type }
  setTimeout(() => (toast.value = { msg: '', type: '' }), ms)
}

/* Modal */
const modalRef = ref(null)
const modal = ref({ title:'', message:'', okText:'', resolve:()=>{}, busy:false })
function confirm (title, message, okText = 'OK') {
  return new Promise(resolve => {
    modal.value = {
      title, message, okText, busy:false,
      resolve: v => { modalRef.value.close(); resolve(v) }
    }
    modalRef.value.showModal()
  })
}

/* Fetch users */
const hdr = () => ({ Authorization:`Bearer ${localStorage.token}` })

onMounted(loadUsers)
async function loadUsers () {
  loading.value = true
  try {
    const { data } = await axios.get(`${API}/users`, { headers: hdr() })
    users.value = data.users || []
  } catch (e) {
    showToast('Failed to load users', 'error', 4000)
  } finally {
    loading.value = false
  }
}

/* Filtered + Sorted List */
const filtered = computed(() => {
  const q = search.value.toLowerCase()
  let list = users.value
    .filter(u => u.role !== 'admin')
    .filter(u => u.full_name.toLowerCase().includes(q) || u.email.includes(q))

  if (sortBy.value === 'role') {
    list.sort((a, b) => a.role.localeCompare(b.role))
  } else if (sortBy.value === 'status') {
    list.sort((a, b) => (a.is_active === b.is_active) ? 0 : (a.is_active ? -1 : 1))
  } else {
    list.sort((a, b) => a.full_name.localeCompare(b.full_name))
  }
  return list
})

/* Toggle Active/Inactive */
async function toggleActive (user) {
  const action = user.is_active ? 'deactivate' : 'activate'
  user.is_active = !user.is_active
  try {
    await axios.put(`${API}/users/${user.id}/${action}`, {}, { headers: hdr() })
    showToast(`User ${action}d`, 'success')
  } catch (e) {
    user.is_active = !user.is_active
    showToast('Operation failed', 'error')
  }
}
function openToggleModal (u) {
  confirm(
    `${u.is_active ? 'Deactivate' : 'Activate'} user`,
    `Are you sure to ${u.is_active ? 'deactivate' : 'activate'} “${u.full_name}”?`,
    u.is_active ? 'Deactivate' : 'Activate'
  ).then(v => v && toggleActive(u))
}

/* Delete User */
async function removeUser (user) {
  try {
    await axios.delete(`${API}/users/${user.id}`, { headers: hdr() })
    users.value = users.value.filter(u => u.id !== user.id)
    showToast('User deleted', 'success')
  } catch (e) {
    showToast('Could not delete user', 'error')
  }
}
function openDeleteModal (u) {
  confirm('Delete user', `Permanently delete “${u.full_name}”?`, 'Delete')
    .then(v => v && removeUser(u))
}
</script>

<style scoped>
:root {
  --c-green: #22c55e;
  --c-green-hover: #16a34a;
  --c-warn: #facc15;
  --c-warn-hover: #eab308;
  --c-danger: #dc2626;
  --c-danger-hover: #b91c1c;
}

.user-page {
  max-width: 1200px;
  margin: auto;
  padding: 2rem;
  font-family: 'Inter', sans-serif;
  background: #f9fafb;
  min-height: 100vh;
}
.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}
.back-btn {
  background: white;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}
.search {
  flex: 1 1 250px;
  padding: 0.7rem 1rem;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #fff;
}
.sort {
  padding: 0.7rem 1rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background: #fff;
}

.user-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
.user-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s;
}
.user-card:hover {
  transform: translateY(-4px);
}
.user-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.user-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #111827;
}
.user-details p {
  margin: 0.3rem 0;
  font-size: 0.9rem;
  color: #374151;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
.btn.tiny {
  padding: 0.45rem 0.8rem;
  font-size: 0.8rem;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}
.green {
  background: var(--c-green);
  color: #fff;
}
.green:hover {
  background: var(--c-green-hover);
}
.warn {
  background: var(--c-warn);
  color: #1f2937;
}
.warn:hover {
  background: var(--c-warn-hover);
}
.danger {
  background: var(--c-danger);
  color: #fff;
}
.danger:hover {
  background: var(--c-danger-hover);
}

.tag {
  padding: 0.3rem 0.6rem;
  font-size: 0.75rem;
  border-radius: 4px;
  color: #fff;
  font-weight: 500;
}
.tag--active {
  background: #10b981;
}
.tag--inactive {
  background: #9ca3af;
}

.export-csv-bar {
  text-align: right;
  margin-top: 2rem;
}
.btn.export {
  background: #2563eb;
  color: #fff;
  border-radius: 6px;
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  border: none;
  cursor: pointer;
}
.btn.export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  font-size: 1rem;
  color: #6b7280;
}

.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  background: #334155;
  color: #fff;
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.15);
  font-size: 0.9rem;
  z-index: 1000;
}
.toast.success {
  background: var(--c-green);
}
.toast.error {
  background: var(--c-danger);
}
.actions {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  gap: 0.8rem;
}

.btn.tiny {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn.tiny.green {
  background-color: #4caf50;
  color: white;
}

.btn.tiny.warn {
  background-color: #ff9800;
  color: white;
}

.btn.tiny.danger {
  background-color: #f44336;
  color: white;
}
</style>
