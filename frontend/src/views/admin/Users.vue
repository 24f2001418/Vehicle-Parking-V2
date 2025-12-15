<template>
  <main class="users-wrapper">
    <section class="users-card">
      <h2 class="title">Registered Users</h2>

      <!-- Search -->
      <div class="search-row">
        <input
          v-model.trim="search"
          placeholder="Search by name or email"
        />
        <button @click="fetchUsers" :disabled="loading">
          {{ loading ? 'Refreshing…' : 'Refresh' }}
        </button>
      </div>

      <!-- Table -->
      <table class="users-table" v-if="filtered.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filtered" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.role }}</td>
            <td>{{ u.is_active ? 'Active' : 'Inactive' }}</td>
            <td class="actions-cell">
              <button
                v-if="!u.is_active"
                @click="activateUser(u.id)"
                :disabled="loading"
                class="activate-btn"
              >
                Activate
              </button>
              <button
                @click="deleteUser(u.id)"
                :disabled="loading"
                class="delete-btn"
              >
                Delete
              </button>
              <button
                v-if="u.is_active"
                @click="deactivateUser(u.id)"
                :disabled="loading"
                class="deactivate-btn"
              >
                Deactivate
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-if="!filtered.length && !loading" class="no-data">
        No users found.
      </p>
    </section>
  </main>
</template>

<script>
export default {
  name: 'UsersAdminView',
  data() {
    return {
      users: [],
      search: '',
      loading: false
    }
  },
  computed: {
    filtered() {
      const term = this.search.toLowerCase()
      return this.users.filter(
        u =>
          u.name.toLowerCase().includes(term) ||
          u.email.toLowerCase().includes(term)
      )
    }
  },
  methods: {
    async fetchUsers() {
      const token = localStorage.getItem('token')
      this.loading = true
      try {
        const res = await fetch('http://127.0.0.1:5000/api/users', {
          headers: { Authorization: `Bearer ${token}` }
        })
        const data = await res.json()
        this.users = (data.users || []).filter(u => u.role !== 'admin')
      } catch (e) {
        alert('Failed to fetch users')
      } finally {
        this.loading = false
      }
    },
    async activateUser(userId) {
      const token = localStorage.getItem('token')
      this.loading = true
      try {
        const res = await fetch(`/api/users/${userId}/activate`, {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        if (res.ok) {
          alert('User activated successfully')
          await this.fetchUsers()
        } else {
          const data = await res.json()
          alert(data.msg || 'Failed to activate user')
        }
      } catch (e) {
        alert('Error activating user')
      } finally {
        this.loading = false
      }
    },
    async deactivateUser(userId) {
      const token = localStorage.getItem('token')
      this.loading = true
      try {
        const res = await fetch(`/api/users/${userId}/deactivate`, {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        if (res.ok) {
          alert('User deactivated successfully')
          await this.fetchUsers()
        } else {
          const data = await res.json()
          alert(data.msg || 'Failed to deactivate user')
        }
      } catch (e) {
        alert('Error deactivating user')
      } finally {
        this.loading = false
      }
    },
    async deleteUser(userId) {
      if (!confirm('Are you sure you want to delete this user?')) {
        return
      }
      const token = localStorage.getItem('token')
      this.loading = true
      try {
        const res = await fetch(`/api/users/${userId}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        if (res.ok) {
          alert('User deleted successfully')
          await this.fetchUsers()
        } else {
          const data = await res.json()
          alert(data.msg || 'Failed to delete user')
        }
      } catch (e) {
        alert('Error deleting user')
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchUsers()
  }
}
</script>

<style scoped>
.users-wrapper {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f3f6fb;
  padding: 2rem;
}

.users-card {
  width: 100%;
  max-width: 900px;
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

.search-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.search-row input {
  flex: 1;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.search-row button {
  padding: 0.6rem 1rem;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.search-row button:hover {
  background: #0056b3;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}
.users-table th,
.users-table td {
  padding: 0.65rem 0.8rem;
  border: 1px solid #e0e0e0;
  text-align: left;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.activate-btn {
  padding: 0.4rem 0.75rem;
  background: #28a745;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.activate-btn:hover {
  background: #218838;
}

.delete-btn {
  padding: 0.4rem 0.75rem;
  background: #dc3545;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.delete-btn:hover {
  background: #c82333;
}

.deactivate-btn {
  padding: 0.4rem 0.75rem;
  background: #ffc107;
  color: #000;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.deactivate-btn:hover {
  background: #e0a800;
}

.no-data {
  text-align: center;
  margin-top: 1rem;
  color: #666;
}
</style>
