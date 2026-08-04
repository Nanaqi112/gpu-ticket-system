import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_staff || false)

  async function login(username, password) {
    const response = await authApi.login(username, password)
    user.value = response
    return response
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // 忽略错误
    }
    user.value = null
  }

  async function fetchUserInfo() {
    try {
      const response = await authApi.getUserInfo()
      user.value = response
    } catch {
      user.value = null
    }
  }

  return {
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUserInfo
  }
})