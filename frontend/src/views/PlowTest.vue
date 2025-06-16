<template>
  <div class="p-4 bg-gray-100 rounded">
    <h2>Plow Data Test</h2>
    <button @click="loadPlows" :disabled="loading">
      {{ loading ? 'Loading...' : 'Load Plows' }}
    </button>
    
    <div v-if="plows.length > 0" class="mt-4">
      <h3>Plows:</h3>
      <ul>
        <li v-for="plow in plows" :key="plow.id">
          {{ plow.name }} - Lat: {{ plow.lat }}, Lng: {{ plow.lng }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePlowStore } from '@/stores/plow'
import { storeToRefs } from 'pinia'

const plowStore = usePlowStore()
const { plows, loading } = storeToRefs(plowStore)

const loadPlows = () => {
  plowStore.fetchPlows()
}
</script>