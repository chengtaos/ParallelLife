import service from './index'

export const decisionApi = {
  list(profileId) {
    return service.get(`/api/decision/${profileId}/list`)
  },
  explore(profileId, decisionId, branchLabel, depth) {
    return service.post(`/api/decision/${profileId}/explore`, {
      decision_id: decisionId,
      branch_label: branchLabel,
      depth
    })
  },
  getTaskStatus(taskId) {
    return service.get(`/api/decision/task/${taskId}/status`)
  },
  getBranch(profileId, branchId) {
    return service.get(`/api/decision/branch/${profileId}/${branchId}`)
  },
  listBranches(profileId) {
    return service.get(`/api/decision/branches/${profileId}`)
  }
}
