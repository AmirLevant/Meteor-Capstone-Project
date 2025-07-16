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
              <p class="text-2xl font-bold text-gray-800">{{ activePlowsCount }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <p class="text-sm text-gray-600">Routes in Progress</p>
              <p class="text-2xl font-bold text-gray-800">0</p>
            </div>
          </div>

          <!-- Coverage Area Controls -->
          <div v-if="coveragePin" class="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 class="text-md font-semibold mb-3 text-blue-800">Coverage Area</h3>
            <div class="space-y-3">
              <div>
                <p class="text-sm text-gray-600">Location</p>
                <p class="text-sm font-mono">{{ coveragePin.lat.toFixed(5) }}, {{ coveragePin.lng.toFixed(5) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-600">Radius: {{ radiusKm.toFixed(1) }} km</p>
                <p class="text-xs text-gray-500">Area: {{ coverageAreaKm2.toFixed(1) }} km²</p>
              </div>
              <button 
                @click="clearCoverageArea"
                class="w-full bg-red-500 text-white rounded px-3 py-2 text-sm hover:bg-red-600 transition-colors"
              >
                Clear Area
              </button>
            </div>
          </div>
         
          <h3 class="text-md font-semibold mt-6 mb-3">Actions</h3>
          <div class="space-y-2">
            <button 
              @click="togglePinMode"
              :class="[
                'w-full rounded-lg px-4 py-2 transition-colors',
                pinModeActive 
                  ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              ]"
            >
              {{ pinModeActive ? 'Cancel Pin Mode' : 'Set Coverage Area' }}
            </button>
            <button 
              @click="createNewRoute"
              :disabled="!coveragePin"
              :class="[
                'w-full rounded-lg px-4 py-2 transition-colors',
                coveragePin 
                  ? 'bg-green-600 hover:bg-green-700 text-white' 
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              ]"
            >
              {{ routeLoading ? 'Creating Route...' : 'Create New Route' }}
            </button>
          </div>

          <!-- Instructions -->
          <div v-if="pinModeActive" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p class="text-sm text-yellow-800">
              <strong>Pin Mode Active:</strong> Click anywhere on the map to set a coverage area center.
            </p>
          </div>
        </div>
      </div>
     
      <!-- Map Container -->
      <div class="flex-1 relative">
        <MapDisplay
          :user-type="'manager'"
          :show-all-plows="true"
          map-id="manager-map"
          @mapClick="handleMapClick"
          @mapReady="onMapReady"
        />

        <!-- Radius Control Slider -->
        <div 
          v-if="coveragePin" 
          class="absolute bottom-6 right-6 bg-white rounded-lg shadow-lg p-4 z-[700] min-w-[250px]"
        >
          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <h4 class="font-semibold text-gray-800">Coverage Radius</h4>
              <button 
                @click="showRadiusControl = !showRadiusControl"
                class="text-gray-500 hover:text-gray-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        :d="showRadiusControl ? 'M19 9l-7 7-7-7' : 'M9 5l7 7-7 7'"></path>
                </svg>
              </button>
            </div>
            
            <div v-show="showRadiusControl" class="space-y-3">
              <!-- Radius Slider -->
              <div>
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>{{ minRadius }}km</span>
                  <span class="font-semibold">{{ radiusKm.toFixed(1) }}km</span>
                  <span>{{ maxRadius }}km</span>
                </div>
                <input
                  type="range"
                  v-model.number="radiusKm"
                  :min="minRadius"
                  :max="maxRadius"
                  :step="0.1"
                  class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  @input="updateRadius"
                />
              </div>

              <!-- Quick Presets -->
              <div class="grid grid-cols-3 gap-2">
                <button
                  v-for="preset in radiusPresets"
                  :key="preset.value"
                  @click="setRadiusPreset(preset.value)"
                  :class="[
                    'px-2 py-1 text-xs rounded border transition-colors',
                    Math.abs(radiusKm - preset.value) < 0.1 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
                  ]"
                >
                  {{ preset.label }}
                </button>
              </div>

              <!-- Area Info -->
              <div class="text-xs text-gray-500 border-t pt-2">
                <p>Coverage area: {{ coverageAreaKm2.toFixed(1) }} km²</p>
                <p>Circumference: {{ (2 * Math.PI * radiusKm).toFixed(1) }} km</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePlowStore } from '@/stores/plow'
import MapDisplay from '@/components/MapDisplay.vue'
import leaflet from 'leaflet'
import { api } from '@/services/api'

const router = useRouter()
const appStore = useAppStore()
const plowStore = usePlowStore()

// Reactive state
const coveragePin = ref(null)
const radiusKm = ref(2.0)
const pinModeActive = ref(false)
const showRadiusControl = ref(true)
const mapInstance = ref(null)
const currentMarker = ref(null)
const currentCircle = ref(null)
const routeLoading = ref(false)
const routeData = ref(null)

// Configuration
const minRadius = 0.5
const maxRadius = 10.0
const radiusPresets = [
  { label: '1km', value: 1.0 },
  { label: '2km', value: 2.0 },
  { label: '5km', value: 5.0 }
]

// Computed properties
const activePlowsCount = computed(() => {
  return 0 
})

const coverageAreaKm2 = computed(() => {
  return Math.PI * Math.pow(radiusKm.value, 2)
})

// Methods
const goHome = () => {
  appStore.resetUser()
  router.push('/')
}

const togglePinMode = () => {
  pinModeActive.value = !pinModeActive.value
  if (!pinModeActive.value && !coveragePin.value) {
    // If canceling pin mode without setting a pin, hide the radius control
    showRadiusControl.value = false
  }
}

const handleMapClick = (coords) => {
  console.log('Map clicked:', coords, 'Pin mode:', pinModeActive.value)
  if (pinModeActive.value) {
    setCoveragePin(coords)
    pinModeActive.value = false
  }
}

const setCoveragePin = (coords) => {
  console.log('Setting coverage pin:', coords)
  coveragePin.value = { lat: coords.lat, lng: coords.lng }
  showRadiusControl.value = true
  updateMapDisplay()
}

const clearCoverageArea = () => {
  coveragePin.value = null
  showRadiusControl.value = false
  routeData.value = null
  clearMapDisplay()
}

const createNewRoute = async () => {
  if (!coveragePin.value) {
    alert('Please set a coverage area first')
    return
  }

  routeLoading.value = true
  
  try {
    const data = await api.createRoute(
      {
        lat: coveragePin.value.lat,
        lng: coveragePin.value.lng
      },
      radiusKm.value
    )
    
    console.log('Route created:', data)
    routeData.value = data
    
    // Display the route on the map
    displayRouteOnMap(data.roads)
    
    alert(`Route created successfully! Found ${data.roads?.length || 0} road segments.`)
    
  } catch (error) {
    console.error('Error creating route:', error)
    alert('Failed to create route. Please try again.')
  } finally {
    routeLoading.value = false
  }
}

const setRadiusPreset = (value) => {
  radiusKm.value = value
  updateRadius()
}

const updateRadius = () => {
  if (coveragePin.value && mapInstance.value) {
    updateMapDisplay()
  }
}

const updateMapDisplay = () => {
  console.log('updateMapDisplay called', mapInstance.value, coveragePin.value)
  if (!mapInstance.value || !coveragePin.value) return

  // Clear existing marker and circle
  clearMapDisplay()

  // Use leaflet directly since we imported it
  const L = window.L || leaflet
  
  if (!L) {
    console.error('Leaflet not available')
    return
  }

  // Add marker
  currentMarker.value = L.marker([coveragePin.value.lat, coveragePin.value.lng], {
    icon: L.divIcon({
      className: 'coverage-pin',
      html: '<div class="w-4 h-4 bg-blue-600 border-2 border-white rounded-full shadow-lg"></div>',
      iconSize: [16, 16],
      iconAnchor: [8, 8]
    })
  }).addTo(mapInstance.value)

  console.log('Marker added:', currentMarker.value)

  // Add circle
  currentCircle.value = L.circle([coveragePin.value.lat, coveragePin.value.lng], {
    radius: radiusKm.value * 1000, // Convert km to meters
    fillColor: '#3b82f6',
    fillOpacity: 0.1,
    color: '#3b82f6',
    weight: 2,
    opacity: 0.6
  }).addTo(mapInstance.value)

  console.log('Circle added:', currentCircle.value)

  // Fit map to show the entire circle
  const bounds = currentCircle.value.getBounds()
  mapInstance.value.fitBounds(bounds, { padding: [20, 20] })
}

const clearMapDisplay = () => {
  if (currentMarker.value) {
    mapInstance.value.removeLayer(currentMarker.value)
    currentMarker.value = null
  }
  if (currentCircle.value) {
    mapInstance.value.removeLayer(currentCircle.value)
    currentCircle.value = null
  }
  // Clear any route overlays
  clearRouteDisplay()
}

const displayRouteOnMap = (roads) => {
  if (!roads || !mapInstance.value) return
  
  const L = window.L || leaflet
  
  roads.forEach(road => {
    if (road.geometry && road.geometry.coordinates) {
      // Convert coordinates to Leaflet format [lat, lng]
      const latlngs = road.geometry.coordinates.map(coord => [coord[1], coord[0]])
      
      // Add road as a polyline
      const polyline = L.polyline(latlngs, {
        color: '#ff6b35',
        weight: 3,
        opacity: 0.8
      }).addTo(mapInstance.value)
      
      // Store reference for cleanup
      if (!routeData.value.mapLayers) {
        routeData.value.mapLayers = []
      }
      routeData.value.mapLayers.push(polyline)
    }
  })
}

const clearRouteDisplay = () => {
  if (routeData.value?.mapLayers) {
    routeData.value.mapLayers.forEach(layer => {
      mapInstance.value.removeLayer(layer)
    })
    routeData.value.mapLayers = []
  }
}

const onMapReady = (map) => {
  console.log('Manager map is ready', map)
  mapInstance.value = map
  
  // Load initial plow data
  plowStore.fetchPlows()
}

// Watch for radius changes
watch(radiusKm, () => {
  updateRadius()
})
</script>

<style scoped>
/* Custom slider styling */
.slider::-webkit-slider-thumb {
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 2px solid white;
}

.slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 2px solid white;
}

/* Fix for Vue DevTools */
:deep(#__nuxt-devtools__),
:deep(#__vue-devtools__) {
  z-index: 9999 !important;
}

/* Custom pin styling */
:deep(.coverage-pin) {
  background: transparent !important;
  border: none !important;
}
</style>