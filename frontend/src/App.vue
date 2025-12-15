<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Navbar from './components/navbar.vue'
import { authStore } from './store'

// Initialize auth state on app mount
authStore.initFromLocalStorage()
</script>

<template>
  <Navbar />
  <RouterView />
</template>

<style scoped>
</style>