<template>
  <main class="admin-wrapper">
    <section class="header">
      <h2 class="title">ParkEase Admin Dashboard</h2>
      <p class="subtitle">Welcome, Admin! Choose an action below.</p>
    </section>

    <!-- Quick‑access grid -->
    <section class="grid">
      <!-- Lots CRUD -->
      <RouterLink to="/admin/lots" class="card">
        <span class="icon">🏗️</span>
        <h3>Manage Lots</h3>
        <p>Create, edit, or delete parking lots.<br />Spots auto‑generated.</p>
      </RouterLink>

      <!-- Spot status -->
      <RouterLink to="/admin/spots" class="card">
        <span class="icon">🚗</span>
        <h3>Spot Status</h3>
        <p>Live view of every spot &amp; parked vehicle.</p>
      </RouterLink>

      <!-- Users -->
      <RouterLink to="/admin/users" class="card">
        <span class="icon">👥</span>
        <h3>Users</h3>
        <p>See all registered users &amp; roles.</p>
      </RouterLink>

      <!-- Summary charts -->
      <RouterLink to="/admin/summary" class="card">
        <span class="icon">📊</span>
        <h3>Summary Charts</h3>
        <p>Occupancy, revenue, and performance charts.</p>
      </RouterLink>
    </section>
  </main>
</template>

<script>
export default {
  name: 'AdminHomeView'
};
</script>

<style scoped>
/* wrapper */
.admin-wrapper {
  min-height: 100vh;
  background: #eef4ff;
  padding: 2rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* header */
.header {
  text-align: center;
  margin-bottom: 2rem;
}
.title {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
}
.subtitle {
  font-size: 1.1rem;
  color: #555;
}

/* grid of cards */
.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}

/* card */
.card {
  background: #fff;
  border-radius: 14px;
  padding: 2rem 1.5rem;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
  text-align: center;
  text-decoration: none;
  color: inherit;
  transition: transform 0.25s, box-shadow 0.25s;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}
.icon {
  font-size: 2.2rem;
  margin-bottom: 0.8rem;
}
.card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}
.card p {
  font-size: 0.95rem;
  color: #666;
}
</style>
