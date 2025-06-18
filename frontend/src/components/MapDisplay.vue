<template>
  <div class="relative h-full w-full">
    <div :id="mapId" class="h-full w-full"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import leaflet from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Props
const props = defineProps({
  // Unique ID for this map instance
  mapId: {
    type: String,
    default: 'map'
  },
  // Center coordinates [lat, lng]
  center: {
    type: Array,
    default: () => [43.479509, -80.518162]
  },
  // Initial zoom level
  zoom: {
    type: Number,
    default: 13
  },
  // Show all plows (for manager view)
  showAllPlows: {
    type: Boolean,
    default: false
  },
  // User type to customize behavior
  userType: {
    type: String,
    default: 'driver',
    validator: (value) => ['manager', 'driver'].includes(value)
  }
})

// Emit events
const emit = defineEmits(['mapClick', 'mapReady'])

let map = null
let markers = []

// Initialize map
const initMap = () => {
  // Create map instance
  map = leaflet.map(props.mapId).setView(props.center, props.zoom)
  
  // Add Mapbox tile layer
  leaflet
    .tileLayer(
      `https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{tileSize}/{z}/{x}/{y}?access_token=${import.meta.env.VITE_API_KEY}`,
      {
        attribution:
          'Map data &copy; © <a href="https://www.mapbox.com/about/maps">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18,
        id: "streets-v12",
        tileSize: 512,
        zoomOffset: -1,
        accessToken: import.meta.env.VITE_API_KEY
      }
    )
    .addTo(map)
  
  // Add click handler for manager view
  if (props.userType === 'manager') {
    map.on('click', (e) => {
      emit('mapClick', { lat: e.latlng.lat, lng: e.latlng.lng })
    })
  }
  
  // Emit that map is ready
  emit('mapReady', map)
}

// Add a marker to the map
const addMarker = (lat, lng, options = {}) => {
  const marker = leaflet.marker([lat, lng], options).addTo(map)
  markers.push(marker)
  return marker
}

// Clear all markers
const clearMarkers = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

// Update map center
const setCenter = (lat, lng, zoom = null) => {
  if (map) {
    if (zoom) {
      map.setView([lat, lng], zoom)
    } else {
      map.setView([lat, lng])
    }
  }
}

// Lifecycle
onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

// Watch for center changes
watch(() => props.center, (newCenter) => {
  if (map && newCenter) {
    setCenter(newCenter[0], newCenter[1])
  }
})

// Expose methods for parent components to use
defineExpose({
  addMarker,
  clearMarkers,
  setCenter,
  map: () => map
})
</script>

<style>
/* Fix for Leaflet marker icons */
.leaflet-default-icon-path {
  background-image: url(https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png);
}

/* Ensure leaflet controls are accessible but below our UI */
.leaflet-control-container {
  z-index: 400 !important;
}

/* Ensure map tiles and overlays work properly */
.leaflet-pane {
  z-index: 200 !important;
}

.leaflet-tile-pane {
  z-index: 200 !important;
}

.leaflet-overlay-pane {
  z-index: 400 !important;
}

.leaflet-shadow-pane {
  z-index: 500 !important;
}

.leaflet-marker-pane {
  z-index: 600 !important;
}

.leaflet-tooltip-pane {
  z-index: 650 !important;
}

.leaflet-popup-pane {
  z-index: 700 !important;
}
</style>