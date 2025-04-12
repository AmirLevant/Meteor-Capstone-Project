<template>
  <div class="h-screen relative">
    <GeoErrorModal 
      @closeGeoError="closeGeoError" 
      v-if="geoError" 
      :geoErrorMsg="geoErrorMsg"
      />
      <MapFeatures :coords="coords" :fetchCoords="fetchCoords" />
    <div id="map" class="h-full z-[1]"></div>
    
    <!-- Plow Status UI Panel on the right side -->
    <div class="absolute top-4 right-4 bg-white p-3 rounded-md shadow-md z-10">
      <h3 class="text-lg font-semibold mb-2">Snow Plow Status</h3>
      <div class="flex flex-col space-y-2 mb-3">
        <label class="flex items-center cursor-pointer">
          <input type="radio" name="plowStatus" value="active" v-model="plowStatus" class="mr-2">
          <span class="text-green-600 font-medium">Active</span>
        </label>
        <label class="flex items-center cursor-pointer">
          <input type="radio" name="plowStatus" value="idle" v-model="plowStatus" class="mr-2">
          <span class="text-yellow-500 font-medium">Idle</span>
        </label>
        <label class="flex items-center cursor-pointer">
          <input type="radio" name="plowStatus" value="inactive" v-model="plowStatus" class="mr-2">
          <span class="text-red-600 font-medium">Inactive</span>
        </label>
      </div>
      
    </div>
  </div>
</template>

<script>
import leaflet from 'leaflet';
import { onMounted, ref, watch } from 'vue';
import 'leaflet/dist/leaflet.css';
import redMarker from '../assets/map-marker-plow.svg';
import GeoErrorModal from '@/components/GeoErrorModal.vue';
import MapFeatures from '@/components/MapFeatures.vue';

export default {
  name: "HomeView",
  components: {GeoErrorModal, MapFeatures},
  setup() {
    let map;
    let snowPlowMarker;
    const plowStatus = ref('active'); // Default status
    
    // Create custom icons for different statuses
    const createCustomIcon = (color) => {
      return leaflet.divIcon({
        className: `custom-marker ${color}-marker`,
        html: `<div style="width: 24px; height: 24px; background-color: ${color}; border: 2px solid white; border-radius: 50%; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
      });
    };
    
    // Status color mapping
    const statusColors = {
      active: '#22c55e', // green-600
      idle: '#eab308',   // yellow-500
      inactive: '#dc2626' // red-600
    };
    
    // Watch for changes in the plow status
    watch(plowStatus, (newStatus) => {
      if (snowPlowMarker) {
        // Update the marker popup content
        snowPlowMarker.setPopupContent(`Snow Plow #1<br>Status: ${newStatus.charAt(0).toUpperCase() + newStatus.slice(1)}`);
        
        // Change marker icon based on status
        const color = statusColors[newStatus];
        snowPlowMarker.setIcon(createCustomIcon(color));
      }
    });
    
    // Function to find user location
    const findMyLocation = () => {
      if (map) {
        map.locate({setView: true, maxZoom: 16});
      }
    };
    
    onMounted(() => {
      //init map
      map = leaflet.map('map').setView([43.479509, -80.518162], 17);
      console.log("hello");
      console.log(import.meta.env.VITE_API_KEY);
      
      // add tile layer
      leaflet
        .tileLayer(
          `https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{tileSize}/{z}/{x}/{y}?access_token=${import.meta.env.VITE_API_KEY}`,
          {
            attribution:
              'Map data &copy; © <a href="https://www.mapbox.com/about/maps">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://apps.mapbox.com/feedback/" target="_blank">Improve this map</a></strong>',
            maxZoom: 18,
            id: "streets-v12",
            tileSize: 512,
            zoomOffset: -1,
            accessToken: import.meta.env.VITE_API_KEY
          }
        )
        .addTo(map);
        
      // Add snow plow marker at the specified coordinates with initial status color
      const snowPlowCoords = [43.47656, -80.51842]; // Converted from 43°28'42.8"N 80°31'06.3"W
      const initialColor = statusColors[plowStatus.value];
      snowPlowMarker = leaflet.marker(snowPlowCoords, {
        icon: createCustomIcon(initialColor)
      }).addTo(map);
      
      // Set popup content and open it immediately to show status
      snowPlowMarker.bindPopup(`Snow Plow #1<br>Status: ${plowStatus.value.charAt(0).toUpperCase() + plowStatus.value.slice(1)}`).openPopup();

      getGeolocation();
      
      // Ensure the map centers on the snow plow with appropriate zoom
      //map.setView(snowPlowCoords, 17);
      
      // Handle location found event
      //map.on('locationfound', function(e) {
      //  const radius = e.accuracy / 2;
        
        // Create a marker at the location
      //  const locationMarker = leaflet.marker(e.latlng).addTo(map)
      //      .bindPopup(`You are within ${radius} meters from this point`).openPopup();
        
        // Draw a circle showing the accuracy radius
      //  leaflet.circle(e.latlng, radius).addTo(map);
      //});
      
      // Handle location error
      //map.on('locationerror', function(e) {
        alert(e.message);
      //});
    });

    const coords = ref(null);
    const fetchCoords = ref(null);
    const geoMarker = ref(null);
    const geoError = ref(null);
    geoError.value = false;
    const geoErrorMsg = ref("Testing v-bind on Modal");

    const getGeolocation = () => {
      // check session storage for coords
      if (sessionStorage.getItem('coords'))
      {
        coords.value = JSON.parse(sessionStorage.getItem("coords"));
        plotGeolocation(coords.value);
        return;
      }
      fetchCoords.value = true;
      navigator.geolocation.getCurrentPosition(setCoords, getLocError);
    }

    const setCoords = (pos) => {
      // stop fetching coords
      fetchCoords.value = null;

      // set coords in session storage
      const setSessionCoords = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      };

      sessionStorage.setItem('coords', JSON.stringify(setSessionCoords));

      // set ref coords value
      coords.value = setSessionCoords;

      plotGeolocation(coords.value);
    }

    const getLocError = (err) => {
      fetchCoords.value = null;
      geoError.value = true;
      geoErrorMsg.value = err.message;
    }

    const plotGeolocation = (coords) => {
      // create custom marker
      const customMarker = leaflet.icon({
        iconUrl: redMarker,
        iconSize: [35, 35],
      });

      // create new marker with coords and custom icon
      geoMarker.value = leaflet.marker([coords.lat, coords.lng], {icon: customMarker })
      .addTo(map);

      // set map view to current location
      map.setView([coords.lat, coords.lng], 16);
    };

    const closeGeoError = () =>
      {
        console.log("Closing modal...");
        geoError.value = false;
        geoErrorMsg.value = null;
        console.log(geoError.value)
      };
    
    return {
      plowStatus,
      coords, fetchCoords, geoMarker, closeGeoError, geoError, geoErrorMsg
    };
  }
};
</script>

<style>
/* Custom marker styling */
.custom-marker {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>