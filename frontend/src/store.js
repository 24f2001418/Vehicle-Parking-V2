import { reactive } from 'vue'

export const authStore = reactive({
  user: null,
  role: null,
  isLoggedIn: false,

  setUser(userData) {
    this.user = userData
    this.role = userData?.role || null
    this.isLoggedIn = !!userData
  },

  logout() {
    this.user = null
    this.role = null
    this.isLoggedIn = false
    localStorage.removeItem('token')
  },

  initFromLocalStorage() {
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    if (token && userData) {
      try {
        const parsed = JSON.parse(userData)
        this.setUser(parsed)
      } catch (e) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }
})
