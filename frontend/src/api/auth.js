import service from './index'

export const authApi = {
  login(password) {
    return service.post('/api/auth/login', { password })
  },
  check() {
    return service.get('/api/auth/check')
  }
}
