<template>
  <div class="p-4 bg-gray-100 rounded">
    <h2>Plow Data Test</h2>
    
    <!-- Existing button -->
    <button @click="loadPlows" :disabled="loading" class="mr-2 mb-2 p-2 bg-blue-500 text-white rounded">
      {{ loading ? 'Loading...' : 'Load All Plows' }}
    </button>
    
    <!-- New test buttons -->
    <button @click="loadSinglePlow" class="mr-2 mb-2 p-2 bg-green-500 text-white rounded">
      Get Plow #1
    </button>
    
    <button @click="createNewPlow" class="mr-2 mb-2 p-2 bg-purple-500 text-white rounded">
      Create Plow
    </button>
    
    <button @click="updatePlowStatus" class="mr-2 mb-2 p-2 bg-orange-500 text-white rounded">
      Update Plow #1 Status
    </button>
    
    <!-- Display results -->
    <div v-if="plows.length > 0" class="mt-4">
      <h3>All Plows:</h3>
      <ul>
        <li v-for="plow in plows" :key="plow.id">
          {{ plow.name }} - Lat: {{ plow.lat }}, Lng: {{ plow.lng }}
        </li>
      </ul>
    </div>
    
    <!-- Display single plow result -->
    <div v-if="singlePlow" class="mt-4">
      <h3>Single Plow Result:</h3>
      <p>{{ JSON.stringify(singlePlow) }}</p>
    </div>
    
    <!-- Display API responses -->
    <div v-if="apiResponse" class="mt-4">
      <h3>API Response:</h3>
      <p>{{ apiResponse }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePlowStore } from '@/stores/plow'
import { api } from '@/services/api'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const plowStore = usePlowStore()
const { plows, loading } = storeToRefs(plowStore)

// New reactive variables for testing
const singlePlow = ref(null)
const apiResponse = ref('')

const loadPlows = () => {
  plowStore.fetchPlows()
}

const loadSinglePlow = async () => {
  try {
    singlePlow.value = await api.getPlowById(1)
  } catch (error) {
    console.error('Error loading single plow:', error)
  }
}

const createNewPlow = async () => {
  try {
    const result = await api.createPlow({ name: 'Test Plow', lat: 45.5, lng: -73.6 })
    apiResponse.value = `Created: ${JSON.stringify(result)}`
  } catch (error) {
    console.error('Error creating plow:', error)
  }
}

const updatePlowStatus = async () => {
  try {
    const result = await api.updatePlowStatus(1, { status: 'active' })
    apiResponse.value = `Updated: ${JSON.stringify(result)}`
  } catch (error) {
    console.error('Error updating plow status:', error)
  }
}
</script>