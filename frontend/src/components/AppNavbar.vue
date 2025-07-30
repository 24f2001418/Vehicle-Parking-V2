<template>
  <nav class="navbar">
    <div class="nav-brand" @click="$router.push('/')">
      <span class="logo">QuizMaster</span>
    </div>
    <ul class="nav-links">
      <template v-if="role === 'admin'">
        <li><router-link to="/admin">Dashboard</router-link></li>
        <li><router-link to="/admin/users">Users</router-link></li>
        <li><router-link to="/admin/subject">Subjects</router-link></li>
        <li><router-link to="/admin/summary">Analytics</router-link></li>
      </template>
      <template v-else-if="role === 'user'">
        <li><router-link to="/user">Home</router-link></li>
        <li><router-link to="/user/subject">Subjects</router-link></li>
        <li><router-link to="/score">Scores</router-link></li>
        <li><router-link to="/summary">Summary</router-link></li>
      </template>
      <template v-else>
        <li><router-link to="/login">Login</router-link></li>
        <li><router-link to="/register">Register</router-link></li>
      </template>
    </ul>
    <div class="nav-actions" v-if="role">
      <button class="logout-btn" @click="logout">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'


const router = useRouter()
const role = ref('')
let lastToken = localStorage.getItem('token')

function logout() {
  localStorage.removeItem('token');
  role.value = '';
  lastToken = null;
  router.push('/login');
}

function getRole() {
  const token = localStorage.getItem('token')
  if (!token) return ''
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.role || ''
  } catch {
    return ''
  }
}

function updateRoleIfChanged() {
  const token = localStorage.getItem('token')
  if (token !== lastToken) {
    lastToken = token
    role.value = getRole()
  }
}

let poller = null
onMounted(() => {
  role.value = getRole()
  // Poll for token changes every 500ms
  poller = setInterval(updateRoleIfChanged, 500)
  // Listen for storage changes (other tabs)
  window.addEventListener('storage', updateRoleIfChanged)
})
onUnmounted(() => {
  if (poller) clearInterval(poller)
  window.removeEventListener('storage', updateRoleIfChanged)
})
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #2563eb 60%, #1e40af 100%);
  color: #fff;
  padding: 0.7rem 2rem;
  box-shadow: 0 2px 12px rgba(37,99,235,0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-brand {
  font-size: 1.5rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 1px;
}
.logo {
  color: #fff;
  text-shadow: 0 2px 8px #1e40af44;
}
.nav-links {
  display: flex;
  gap: 1.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
}
.nav-links a {
  color: #fff;
  text-decoration: none;
  font-weight: 500;
  font-size: 1.05rem;
  padding: 0.2rem 0.5rem;
  border-radius: 5px;
  transition: background 0.18s;
}
.nav-links a.router-link-exact-active,
.nav-links a:hover {
  background: #1e40af;
}
.nav-actions {
  margin-left: 1.5rem;
}
.logout-btn {
  background: #fff;
  color: #2563eb;
  border: none;
  border-radius: 6px;
  padding: 0.4rem 1.1rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 4px #1e40af22;
  transition: background 0.18s, color 0.18s;
}
.logout-btn:hover {
  background: #2563eb;
  color: #fff;
}
@media (max-width: 700px) {
  .navbar {
    flex-direction: column;
    align-items: flex-start;
    padding: 0.7rem 0.7rem;
  }
  .nav-links {
    gap: 0.7rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
  }
  .nav-actions {
    margin-left: 0;
    margin-top: 0.7rem;
  }
}
</style>
