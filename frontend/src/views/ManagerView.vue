<template>
  <div class="h-screen bg-gray-100">
    <div class="bg-white shadow-sm px-6 py-4">
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
    
    <div class="p-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold mb-4">Fleet Overview</h2>
        <p class="text-gray-600">Manager view is under construction. Map and controls will appear here.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>