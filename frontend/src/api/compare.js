import service from './index'

export const compareApi = {
  compare(profileId, branchIds) {
    return service.post(`/api/compare/${profileId}`, { branch_ids: branchIds })
  },
  getTaskStatus(taskId) {
    return service.get(`/api/compare/task/${taskId}/status`)
  }
}
