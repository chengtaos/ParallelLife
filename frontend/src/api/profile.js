import service from './index'

export const profileApi = {
  create(text, name) {
    return service.post('/api/profile/create', { text, name })
  },
  get(profileId) {
    return service.get(`/api/profile/${profileId}`)
  },
  list() {
    return service.get('/api/profile/list')
  },
  delete(profileId) {
    return service.delete(`/api/profile/${profileId}`)
  },
  getTaskStatus(taskId) {
    return service.get(`/api/profile/task/${taskId}/status`)
  },
  getPattern(profileId) {
    return service.get(`/api/profile/${profileId}/pattern`)
  },
  getNetwork(profileId) {
    return service.get(`/api/profile/${profileId}/network`)
  }
}
