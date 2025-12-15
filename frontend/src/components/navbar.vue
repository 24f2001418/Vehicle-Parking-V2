<template>
  <header class="navbar">
    <div class="nav-container">
      <router-link to="/" class="logo">🚗 ParkEase</router-link>
      <nav :class="{ open: isOpen }" class="nav-links">
        <!-- Guest (not logged in) -->
        <template v-if="!auth.isLoggedIn">
          <router-link to="/login" exact-active-class="active">Login</router-link>
          <router-link to="/register" exact-active-class="active">Register</router-link>
        </template>

        <!-- Admin -->
        <template v-else-if="auth.role === 'admin'">
          <router-link to="/admin" exact-active-class="active">Home</router-link>
          <router-link to="/admin/lots" exact-active-class="active">Lots</router-link>
          <router-link to="/admin/spots" exact-active-class="active">Spots</router-link>
          <router-link to="/admin/users" exact-active-class="active">Users</router-link>
          <router-link to="/admin/summary" exact-active-class="active">Summary</router-link>
          <span class="user-info">{{ auth.user?.name }}</span>
          <button class="logout-btn" @click="handleLogout">Logout</button>
        </template>

        <!-- User (regular user) -->
        <template v-else-if="auth.role === 'user'">
          <router-link to="/user" exact-active-class="active">Home</router-link>
          <router-link to="/user/parking" exact-active-class="active">Book Parking</router-link>
          <router-link to="/user/history" exact-active-class="active">History</router-link>
          <span class="user-info">{{ auth.user?.name }}</span>
          <button class="logout-btn" @click="handleLogout">Logout</button>
        </template>
      </nav>
      <button class="menu-toggle" @click="isOpen = !isOpen">☰</button>
    </div>
  </header>
</template>

<script>
import { authStore } from '@/store'

export default {
  name: 'Navbar',
  data() {
    return {
      isOpen: false,
      auth: authStore
    };
  },
  methods: {
    handleLogout() {
      authStore.logout()
      this.$router.push('/login')
      this.isOpen = false
    }
  },
  mounted() {
    authStore.initFromLocalStorage()
  }
};
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  padding: 1rem 0;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.logo {
  font-size: 1.6rem;
  font-weight: 800;
  color: white;
  text-decoration: none;
  letter-spacing: 0.5px;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-links a,
.nav-links .logout-btn {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  position: relative;
  padding: 0.5rem 0;
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: white;
  transition: width 0.3s ease;
}

.nav-links a:hover::after,
.nav-links a.active::after {
  width: 100%;
}

.nav-links a:hover,
.nav-links a.active {
  color: white;
}

.nav-links .logout-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  cursor: pointer;
  font-size: 0.95rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-links .logout-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: white;
}

.nav-links .user-info {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.9rem;
  padding: 0 1rem;
  border-left: 2px solid rgba(255, 255, 255, 0.3);
  font-weight: 500;
}

.menu-toggle {
  background: transparent;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  display: none;
  transition: transform 0.3s ease;
}

.menu-toggle:hover {
  transform: rotate(90deg);
}

@media (max-width: 768px) {
  .nav-links {
    flex-direction: column;
    width: 100%;
    display: none;
    margin-top: 1rem;
    gap: 0.8rem;
  }

  .nav-links.open {
    display: flex;
  }

  .menu-toggle {
    display: block;
  }

  .nav-links .user-info {
    border-left: none;
    padding: 0;
  }
}
</style>
