import axios from 'axios'
import i18n from '../i18n'

// 用户身份：首次访问生成随机 key，存入 localStorage 持久化
function randomId() {
  return 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0
    return (c === 'x' ? r : r & 3 | 8).toString(16)
  })
}

function getUserKey() {
  let key = localStorage.getItem('user_key')
  if (!key) {
    key = 'uk_' + randomId().slice(0, 20)
    localStorage.setItem('user_key', key)
  }
  return key
}

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:5001' : ''),
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' }
})

service.interceptors.request.use(config => {
  config.headers['Accept-Language'] = i18n.global.locale.value
  config.headers['X-User-Key'] = getUserKey()
  const token = sessionStorage.getItem('auth_token')
  if (token) config.headers['X-Auth-Token'] = token
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
