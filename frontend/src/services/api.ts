import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const api = {
  async getPlows() {
    const response = await axios.get(`${API_BASE_URL}/api/plows`)
    return response.data
  }
}