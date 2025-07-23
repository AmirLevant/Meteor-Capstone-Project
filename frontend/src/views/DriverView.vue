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

      <!-- Find My Location Button -->
      <div class="absolute top-4 right-4 z-[800]">
        <button
          @click="findMyLocation"
          :disabled="locationLoading"
          class="bg-white rounded-lg shadow-lg p-3 hover:bg-gray-50 transition-colors disabled:bg-gray-100"
          title="Find my location"
        >
          <svg v-if="!locationLoading" class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          <svg v-else class="w-6 h-6 text-gray-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
     
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
            <div class="mb-4">
              <p class="text-sm text-gray-600 mb-2">Driver: {{ driverName }}</p>
              
              <!-- Route Selection -->
              <div v-if="availableRoutes.length > 0" class="mb-3">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Select Route:
                </label>
                <select 
                  v-model="selectedRouteId"
                  @change="selectRoute"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Choose a route...</option>
                  <option 
                    v-for="route in availableRoutes" 
                    :key="route.id" 
                    :value="route.id"
                  >
                    Route {{ route.id.split('_')[1] }} ({{ route.road_count || 0 }} roads)
                  </option>
                </select>
              </div>

              <!-- Route Info -->
              <div v-if="selectedRoute" class="mb-3 p-3 bg-blue-50 rounded-lg">
                <p class="text-sm text-blue-800">
                  <strong>Active Route:</strong> {{ selectedRoute.road_count || 0 }} road segments
                </p>
                <p class="text-xs text-blue-600">
                  Coverage: {{ selectedRoute.radius }}km radius
                </p>
              </div>
            </div>
            
            <div class="space-y-2">
              <button
                @click="loadRoutes"
                :disabled="routesLoading"
                class="w-full bg-gray-600 text-white rounded-lg px-4 py-2 hover:bg-gray-700 disabled:bg-gray-400 transition-colors"
              >
                {{ routesLoading ? 'Loading...' : 'Refresh Routes' }}
              </button>
              
              <button
                @click="toggleTracking"
                :disabled="!selectedRoute"
                :class="[
                  'w-full rounded-lg px-4 py-3 font-semibold transition-colors',
                  !selectedRoute 
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : isTracking
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import MapDisplay from '@/components/MapDisplay.vue'
import { api } from '@/services/api'
import leaflet from 'leaflet'

const router = useRouter()
const appStore = useAppStore()

// Local state
const tempName = ref('')
const tempEmail = ref('')
const isTracking = ref(false)
const availableRoutes = ref([])
const selectedRouteId = ref('')
const selectedRoute = ref(null)
const routesLoading = ref(false)
const mapInstance = ref(null)
const routeMapLayers = ref([])
const locationLoading = ref(false)

// Computed
const driverName = computed(() => appStore.driverInfo.name)
const driverEmail = computed(() => appStore.driverInfo.email)

// Methods
const goHome = () => {
  appStore.resetUser()
  router.push('/')
}

const findMyLocation = () => {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by your browser')
    return
  }

  locationLoading.value = true

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      console.log('Current location:', latitude, longitude)
      
      if (mapInstance.value) {
        // Center map on current location with higher zoom for driver
        mapInstance.value.setView([latitude, longitude], 17)
      }
      
      locationLoading.value = false
    },
    (error) => {
      console.error('Error getting location:', error)
      let errorMessage = 'Unable to get your location. '
      
      switch(error.code) {
        case error.PERMISSION_DENIED:
          errorMessage += 'Please allow location access.'
          break
        case error.POSITION_UNAVAILABLE:
          errorMessage += 'Location information unavailable.'
          break
        case error.TIMEOUT:
          errorMessage += 'Location request timed out.'
          break
        default:
          errorMessage += 'An unknown error occurred.'
      }
      
      alert(errorMessage)
      locationLoading.value = false
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  )
}

const saveDriverInfo = () => {
  if (tempName.value && tempEmail.value) {
    appStore.setDriverInfo(tempName.value, tempEmail.value)
    // Load routes after driver info is saved
    loadRoutes()
  }
}

const loadRoutes = async () => {
  routesLoading.value = true
  try {
    const response = await api.getRoutes()
    availableRoutes.value = response.routes || []
    console.log(`Loaded ${availableRoutes.value.length} routes`)
  } catch (error) {
    console.error('Error loading routes:', error)
    alert('Failed to load routes')
  } finally {
    routesLoading.value = false
  }
}

const selectRoute = async () => {
  if (!selectedRouteId.value) {
    selectedRoute.value = null
    clearRouteDisplay()
    return
  }

  try {
    const response = await api.getRouteById(selectedRouteId.value)
    selectedRoute.value = response.route
    console.log('Selected route:', selectedRoute.value)
    
    // Display the route on the map
    displayRouteOnMap(selectedRoute.value.roads)
    
    // Center map on the route
    if (selectedRoute.value.center && mapInstance.value) {
      mapInstance.value.setView([selectedRoute.value.center.lat, selectedRoute.value.center.lng], 14)
    }
    
  } catch (error) {
    console.error('Error fetching route:', error)
    alert('Failed to load route details')
  }
}

const displayRouteOnMap = (roads) => {
  if (!roads || !mapInstance.value) return
  
  // Clear existing route display
  clearRouteDisplay()
  
  const L = window.L || leaflet
  
  roads.forEach((road, index) => {
    if (road.coordinates && road.coordinates.length >= 2) {
      // Convert coordinates to Leaflet format [lat, lng] - using simplified format
      const latlngs = road.coordinates.map(coord => [coord[1], coord[0]])
      
      // Use same red color as ManagerView for all roads
      const polyline = L.polyline(latlngs, {
        color: '#ff6b35',  // Same red as ManagerView
        weight: 4,
        opacity: 0.8
      }).addTo(mapInstance.value)
      
      // Add popup with road info (simplified)
      polyline.bindPopup(`
        <div>
          <strong>${road.name}</strong><br>
          Type: ${road.type}<br>
          ID: ${road.id}
        </div>
      `)
      
      // Store reference for cleanup
      routeMapLayers.value.push(polyline)
    }
  })
  
  console.log(`Displayed ${routeMapLayers.value.length} road segments on map`)
}

const clearRouteDisplay = () => {
  if (routeMapLayers.value.length > 0 && mapInstance.value) {
    routeMapLayers.value.forEach(layer => {
      mapInstance.value.removeLayer(layer)
    })
    routeMapLayers.value = []
  }
}

const toggleTracking = () => {
  if (!selectedRoute.value) return
  
  isTracking.value = !isTracking.value
  console.log('Tracking:', isTracking.value, 'Route:', selectedRoute.value.id)
  
  if (isTracking.value) {
    // Start tracking - this is where you'd implement GPS tracking
    console.log('Started tracking route with', selectedRoute.value.road_count, 'roads')
  } else {
    // Stop tracking
    console.log('Stopped tracking')
  }
}

const onMapReady = (mapInstanceParam) => {
  console.log('Driver map is ready')
  mapInstance.value = mapInstanceParam
  
  // If we're already logged in, load routes
  if (driverName.value) {
    loadRoutes()
  }
}

// Load routes when component mounts if driver is already logged in
onMounted(() => {
  if (driverName.value) {
    loadRoutes()
  }
})
</script>

<style>
/* Fix for Vue DevTools */
:deep(#__nuxt-devtools__),
:deep(#__vue-devtools__) {
  z-index: 9999 !important;
}
</style>