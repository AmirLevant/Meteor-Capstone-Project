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
        .addTo(map)
    });

  }
};
</script>
