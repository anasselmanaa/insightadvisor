import axios from 'axios'

const api = axios.create({
  baseURL: 'https://insightadvisor-api.onrender.com',
  timeout: 60000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
