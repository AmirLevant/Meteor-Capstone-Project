<template>
  <div class="h-screen flex flex-col">
    <!-- Header -->
    <div class="bg-white shadow-sm px-6 py-4 relative z-[800]">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800">Driver Navigation</h1>
        <button 
          @click="goHome"
          class="text-blue-600 hover:text-blue-800 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Back to Home
        </button>
      </div>
    </div>
    
    <!-- Map Container -->
    <div class="flex-1 relative">
      <MapDisplay 
        :user-type="'driver'"
        :zoom="16"
        map-id="driver-map"
        @map-ready="onMapReady"
      />
      
      <!-- Driver Controls Overlay -->
      <div class="absolute bottom-6 left-6 right-6 z-[800]">
        <div class="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
          <div v-if="!driverName">
            <h3 class="text-lg font-semibold mb-3">Enter Your Information</h3>
            <input 
              v-model="tempName"
              type="text"
              placeholder="Your name"
              class="w-full px-4 py-2 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
            <input 
              v-model="tempEmail"
              type="email"
              placeholder="Your email"
              class="w-full px-4 py-2 border rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
            <button 
              @click="saveDriverInfo"
              :disabled="!tempName || !tempEmail"
              class="w-full bg-blue-600 text-white rounded-lg px-4 py-3 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Start Driving
            </button>
          </div>
          
          <div v-else>
            <p class="text-sm text-gray-600 mb-2">Driver: {{ driverName }}</p>
            <button 
              @click="toggleTracking"
              :class="[
                'w-full rounded-lg px-4 py-3 font-semibold transition-colors',
                isTracking 
                  ? 'bg-red-600 text-white hover:bg-red-700' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              ]"
            >
              {{ isTracking ? 'Stop Tracking' : 'Start Route' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import MapDisplay from '@/components/MapDisplay.vue'

const router = useRouter()
const appStore = useAppStore()

// Local state
const tempName = ref('')
const tempEmail = ref('')
const isTracking = ref(false)

// Computed
const driverName = computed(() => appStore.driverInfo.name)
const driverEmail = computed(() => appStore.driverInfo.email)

// Methods
const goHome = () => {
  appStore.resetUser()
  router.push('/')
}

const saveDriverInfo = () => {
  if (tempName.value && tempEmail.value) {
    appStore.setDriverInfo(tempName.value, tempEmail.value)
  }
}

const toggleTracking = () => {
  isTracking.value = !isTracking.value
  console.log('Tracking:', isTracking.value)
  // Will implement actual tracking later
}

const onMapReady = (mapInstance) => {
  console.log('Driver map is ready')
  // Will be used later to show driver location
}
</script>

<style>
/* Fix for Vue DevTools */
:deep(#__nuxt-devtools__),
:deep(#__vue-devtools__) {
  z-index: 9999 !important;
}
</style>