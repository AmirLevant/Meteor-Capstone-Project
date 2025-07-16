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
let circles = []

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

  // Make Leaflet globally accessible for radius functionality
  window.L = leaflet
 
  // Emit that map is ready
  emit('mapReady', map)
}

// Add a marker to the map
const addMarker = (lat, lng, options = {}) => {
  const marker = leaflet.marker([lat, lng], options).addTo(map)
  markers.push(marker)
  return marker
}

// Add a custom marker (for coverage pins)
const addCustomMarker = (lat, lng, customIcon) => {
  const marker = leaflet.marker([lat, lng], { icon: customIcon }).addTo(map)
  markers.push(marker)
  return marker
}

// Add a circle to the map
const addCircle = (lat, lng, radius, options = {}) => {
  const defaultOptions = {
    fillColor: '#3b82f6',
    fillOpacity: 0.1,
    color: '#3b82f6',
    weight: 2,
    opacity: 0.6
  }
  
  const circle = leaflet.circle([lat, lng], {
    radius: radius, // radius in meters
    ...defaultOptions,
    ...options
  }).addTo(map)
  
  circles.push(circle)
  return circle
}

// Clear all markers
const clearMarkers = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

// Clear all circles
const clearCircles = () => {
  circles.forEach(circle => circle.remove())
  circles = []
}

// Clear all overlays (markers and circles)
const clearAllOverlays = () => {
  clearMarkers()
  clearCircles()
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

// Fit map to show bounds
const fitBounds = (bounds, options = {}) => {
  if (map && bounds) {
    map.fitBounds(bounds, options)
  }
}

// Create a custom div icon
const createDivIcon = (html, className = '', iconSize = [16, 16]) => {
  return leaflet.divIcon({
    className: className,
    html: html,
    iconSize: iconSize,
    iconAnchor: [iconSize[0] / 2, iconSize[1] / 2]
  })
}

// Get map instance (for external manipulation)
const getMapInstance = () => map

// Remove specific marker or circle
const removeLayer = (layer) => {
  if (map && layer) {
    map.removeLayer(layer)
    
    // Remove from tracking arrays
    const markerIndex = markers.indexOf(layer)
    if (markerIndex > -1) {
      markers.splice(markerIndex, 1)
    }
    
    const circleIndex = circles.indexOf(layer)
    if (circleIndex > -1) {
      circles.splice(circleIndex, 1)
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
  addCustomMarker,
  addCircle,
  clearMarkers,
  clearCircles,
  clearAllOverlays,
  setCenter,
  fitBounds,
  createDivIcon,
  removeLayer,
  getMapInstance,
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

/* Custom pin styling */
.coverage-pin {
  background: transparent !important;
  border: none !important;
}
</style>