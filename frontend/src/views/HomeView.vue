<template>
  <div class="h-screen relative">
    <div id="map" class="h-full z-[1]"></div>
  </div>
</template>

<script>
import leaflet from 'leaflet';
import { onMounted } from 'vue';
import 'leaflet/dist/leaflet.css';

export default {
  name: "HomeView",
  components: {},
  setup() {
    let map;
    onMounted(() => {
      //init map
      map = leaflet.map('map').setView([43.479509, -80.518162], 17);
      console.log("hello")
      console.log(import.meta.env.VITE_API_KEY)
      
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
        
      // Add snow plow marker at the specified coordinates - using basic implementation that doesn't require extra plugins
      const snowPlowCoords = [43.47856, -80.51842]; // Converted from 43°28'42.8"N 80°31'06.3"W
      const snowPlowMarker = leaflet.marker(snowPlowCoords).addTo(map);
      snowPlowMarker.bindPopup('Snow Plow #1<br>Status: Active');
      
      // Add a simple geolocation button without requiring the plugin
      const locationButton = leaflet.control({position: 'topright'});
      
      locationButton.onAdd = function() {
        const button = leaflet.DomUtil.create('button', 'location-button');
        button.innerHTML = '📍';
        button.title = "Show my location";
        button.style.fontSize = '20px';
        button.style.padding = '5px 10px';
        button.style.backgroundColor = 'white';
        button.style.border = '2px solid rgba(0,0,0,0.2)';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';
        
        button.onclick = function() {
          map.locate({setView: true, maxZoom: 16});
        };
        
        return button;
      };
      
      locationButton.addTo(map);
      
      // Handle location found event
      map.on('locationfound', function(e) {
        const radius = e.accuracy / 2;
        
        // Create a marker at the location
        const locationMarker = leaflet.marker(e.latlng).addTo(map)
            .bindPopup(`You are within ${radius} meters from this point`).openPopup();
        
        // Draw a circle showing the accuracy radius
        leaflet.circle(e.latlng, radius).addTo(map);
      });
      
      // Handle location error
      map.on('locationerror', function(e) {
        alert(e.message);
      });
    });
  }
};
</script>