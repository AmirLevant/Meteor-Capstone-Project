import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // State
  const userType = ref<'manager' | 'driver' | null>(null)
  const driverInfo = ref({
    name: '',
    email: ''
  })

  // Actions
  const setUserType = (type: 'manager' | 'driver') => {
    userType.value = type
  }

  const setDriverInfo = (name: string, email: string) => {
    driverInfo.value = { name, email }
  }

  const resetUser = () => {
    userType.value = null
    driverInfo.value = { name: '', email: '' }
  }

  return {
    // State
    userType,
    driverInfo,
    
    // Actions
    setUserType,
    setDriverInfo,
    resetUser
  }
})