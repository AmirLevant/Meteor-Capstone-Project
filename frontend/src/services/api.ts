import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// Type definitions for lean data format
export interface LeanRoad {
  id: string
  name: string
  type: string
  coordinates: [number, number][] // Array of [lng, lat] pairs
}

export interface RouteCenter {
  lat: number
  lng: number
}

export interface LeanRoute {
  id: string
  center: RouteCenter
  radius: number
  roads: LeanRoad[]
  road_count: number
  created_at: string
  status: string
}

export interface CreateRouteResponse {
  success: boolean
  route: LeanRoute
  roads: LeanRoad[]
  message: string
}

export interface GetRoutesResponse {
  success: boolean
  routes: LeanRoute[]
  count: number
}

export interface GetRouteByIdResponse {
  success: boolean
  route: LeanRoute
}

export const api = {
  // Plow Management
  async getPlows() {
    const response = await axios.get(`${API_BASE_URL}/api/plows`)
    return response.data
  },
 
  async getPlowById(id: number) {
    const response = await axios.get(`${API_BASE_URL}/api/plows/${id}`)
    return response.data
  },
 
  async createPlow(plowData: any) {
    const response = await axios.post(`${API_BASE_URL}/api/plows/`, plowData)
    return response.data
  },
 
  async updatePlowStatus(id: number, status: any) {
    const response = await axios.patch(`${API_BASE_URL}/api/plows/${id}/status`, status)
    return response.data
  },

  // Route Management
  async createRoute(center: RouteCenter, radius: number): Promise<CreateRouteResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/routes/create`, {
      center,
      radius
    })
    return response.data
  },

  async getRoutes(): Promise<GetRoutesResponse> {
    const response = await axios.get(`${API_BASE_URL}/api/routes`)
    return response.data
  },

  async getRouteById(routeId: string): Promise<GetRouteByIdResponse> {
    const response = await axios.get(`${API_BASE_URL}/api/routes/${routeId}`)
    return response.data
  },

  // Driver Management
  async createDriver(driverData: { name: string; email: string; password: string }) {
    const response = await axios.post(`${API_BASE_URL}/api/driver`, driverData)
    return response.data
  },

  async updateDriverLocation(locationData: {
    email: string
    location: {
      type: 'Point'
      coordinates: [number, number] // [lng, lat]
    }
    last_update: string
  }) {
    const response = await axios.put(`${API_BASE_URL}/api/driver/location`, locationData)
    return response.data
  },

  async getDriverLocation(email: string) {
    const response = await axios.get(`${API_BASE_URL}/api/driver/location?email=${encodeURIComponent(email)}`)
    return response.data
  },

  async assignDriverToRoute(driverName: string, routeId: string) {
    const response = await axios.post(`${API_BASE_URL}/api/assign_driver`, {
      driver_name: driverName,
      route_id: routeId
    })
    return response.data
  },

  // Legacy route optimization (for existing optimized route functionality)
  async getOptimizedRoute(coordinates: { lat: number; lng: number }[]) {
    const response = await axios.post(`${API_BASE_URL}/api/get_route`, {
      coordinates
    })
    return response.data
  },

  // Utility method for testing connectivity
  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/`)
    return response.data
  }
}