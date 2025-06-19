import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const api = {
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

  async createRoute(center: { lat: number, lng: number }, radius: number) {
    const response = await axios.post(`${API_BASE_URL}/api/routes/create`, {
      center,
      radius
    })
    return response.data
  },

  async getRoutes() {
    const response = await axios.get(`${API_BASE_URL}/api/routes`)
    return response.data
  },

  async getRouteById(routeId: string) {
    const response = await axios.get(`${API_BASE_URL}/api/routes/${routeId}`)
    return response.data
  }
}