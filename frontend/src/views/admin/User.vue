<template>
  <div class="user-page">
    <!-- Header -->
    <header class="page-header">
      <button class="back-btn" @click="router.back()">← Back</button>
      <h1>Manage Users</h1>
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
            {{ u.is_active ? 'Deactivate' : 'Activate' }}
          </button>
          <button class="btn tiny danger" @click="openDeleteModal(u)">Delete</button>
        </div>
      </div>

      <p v-if="!filtered.length" class="empty">No users found.</p>
    </div>
    <div v-else class="loading">Loading…</div>

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

/* Layout */
.user-page {
  max-width: 1100px;
  margin: auto;
  padding: 1.5rem;
  font-family: 'Inter', sans-serif;
  background: #f3f4f6; /* Light gray background */
  min-height: 100vh;
}
.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.page-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}
.back-btn {
  border: 1px solid #d1d5db;
  padding: 7px 14px;
  border-radius: 6px;
  background: #f8fafc;
  cursor: pointer;
}

/* Controls */
.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
}
.search {
  flex: 1 1 220px;
  padding: 0.6rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}
.sort {
  padding: 0.6rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: white;
}

/* Cards */
.user-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-top: 1rem;
}
.user-card {
  background: #eff6ff; /* Light blue background */
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
}
.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.user-name {
  font-weight: 600;
  font-size: 1.1rem;
  color: #111827;
}
.user-details p {
  margin: 0.2rem 0;
  font-size: 0.9rem;
  color: #374151;
}

/* Buttons & Tags */
.actions {
  display: flex;
  gap: 8px;
  margin-top: 0.75rem;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: background 0.2s;
}
.green { background: var(--c-green); color: #fff; }
.green:hover { background: var(--c-green-hover); }
.warn { background: var(--c-warn); color: #1f2937; }
.warn:hover { background: var(--c-warn-hover); }
.danger { background: var(--c-danger); color: #fff; }
.danger:hover { background: var(--c-danger-hover); }

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #fff;
}
.tag--active {
  background: #9ca3af;
}
.tag--inactive {
  background: var(--c-green);
}

.loading, .empty {
  text-align: center;
  padding: 2.5rem 0;
  color: #6b7280;
  font-size: 0.95rem;
}

/* Modal */
.modal {
  border: none;
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 420px;
}
.modal h3 {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
}
.mb {
  margin-bottom: 1.25rem;
  color: #374151;
}
.modal-btns {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
.modal .btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  background: #e5e7eb;
}
.modal .danger {
  background: var(--c-danger);
  color: #fff;
}
.modal-backdrop::backdrop {
  background: rgba(0, 0, 0, 0.45);
}

/* Toast */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  background: #334155;
  color: #fff;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.2);
}
.toast.error {
  background: var(--c-danger);
}
.toast.success {
  background: var(--c-green);
}
</style>