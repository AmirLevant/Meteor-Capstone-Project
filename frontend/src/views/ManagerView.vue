<template>
  <div class="h-screen flex flex-col">
    <!-- Header -->
    <div class="bg-white shadow-sm px-6 py-4 relative z-[800]">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-800">Manager Dashboard</h1>
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
    
    <!-- Main Content -->
    <div class="flex-1 flex relative">
      <!-- Sidebar -->
      <div class="w-96 bg-white shadow-lg overflow-y-auto relative z-[800]">
        <div class="p-6">
          <h2 class="text-lg font-semibold mb-4">Fleet Overview</h2>
          <div class="space-y-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600">Active Plows</p>
              <p class="text-2xl font-bold text-gray-800">0</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600">Routes in Progress</p>
              <p class="text-2xl font-bold text-gray-800">0</p>
            </div>
          </div>
          
          <h3 class="text-md font-semibold mt-6 mb-3">Actions</h3>
          <div class="space-y-2">
            <button class="w-full bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition-colors">
              Create New Route
            </button>
            <button class="w-full bg-green-600 text-white rounded-lg px-4 py-2 hover:bg-green-700 transition-colors">
              Set Coverage Area
            </button>
          </div>
        </div>
      </div>
      
      <!-- Map Container -->
      <div class="flex-1 relative">
        <MapDisplay 
          :user-type="'manager'"
          :show-all-plows="true"
          map-id="manager-map"
          @map-click="handleMapClick"
          @map-ready="onMapReady"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import MapDisplay from '@/components/MapDisplay.vue'

const router = useRouter()
const appStore = useAppStore()

const goHome = () => {
  appStore.resetUser()
  router.push('/')
}

const handleMapClick = (coords) => {
  console.log('Map clicked at:', coords)
  // Will be used later for route creation
}

const onMapReady = (mapInstance) => {
  console.log('Manager map is ready')
  // Will be used later to add initial markers
}
</script>

<style>
/* Fix for Vue DevTools */
:deep(#__nuxt-devtools__),
:deep(#__vue-devtools__) {
  z-index: 9999 !important;
}
</style>