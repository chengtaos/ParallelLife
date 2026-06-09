import axios from 'axios'
import i18n from '../i18n'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' }
})

service.interceptors.request.use(config => {
  config.headers['Accept-Language'] = i18n.global.locale.value
  return config
}, error => Promise.reject(error))

service.interceptors.response.use(response => {
  const res = response.data
  if (!res.success && res.success !== undefined) {
    return Promise.reject(new Error(res.error || 'Unknown error'))
  }
  return res
}, error => {
  console.error('Response error:', error)
  return Promise.reject(error)
})

export default service
