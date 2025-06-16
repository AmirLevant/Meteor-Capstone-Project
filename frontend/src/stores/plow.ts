import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const usePlowStore = defineStore('plow', () => {
  const plows = ref([])
  const loading = ref(false)

  async function fetchPlows() {
    loading.value = true
    try {
      const data = await api.getPlows()
      plows.value = data.plows
    } catch (error) {
      console.error('Failed to fetch plows:', error)
    } finally {
      loading.value = false
    }
  }

  return { plows, loading, fetchPlows }
})