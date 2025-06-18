<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-4xl w-full px-6">
      <!-- App Title -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-gray-800 mb-4">Snow Plow Management System</h1>
        <p class="text-xl text-gray-600">Select your role to continue</p>
      </div>

      <!-- Selection Cards -->
      <div class="grid md:grid-cols-2 gap-8">
        <!-- Manager Card -->
        <div 
          @click="selectManager"
          class="bg-white rounded-lg shadow-lg p-8 cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <div class="text-center">
            <div class="mb-6">
              <svg class="w-24 h-24 mx-auto text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800 mb-3">Manager View</h2>
            <p class="text-gray-600">Monitor fleet, create routes, and manage coverage areas</p>
          </div>
        </div>

        <!-- Driver Card -->
        <div 
          @click="selectDriver"
          class="bg-white rounded-lg shadow-lg p-8 cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <div class="text-center">
            <div class="mb-6">
              <svg class="w-24 h-24 mx-auto text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6l2 5-2 5H9l2-5-2-5z"></path>
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800 mb-3">Driver View</h2>
            <p class="text-gray-600">Navigate routes and update your location</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const selectManager = () => {
  router.push('/manager')
}

const selectDriver = () => {
  router.push('/driver')
}
</script>