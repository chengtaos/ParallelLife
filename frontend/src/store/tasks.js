/**
 * 全局任务状态管理
 * 跨页面共享异步任务进度，用于导航间保持任务追踪
 */
import { reactive } from 'vue'

const state = reactive({
  /** @type {{ id: string, type: string, profileId: string, progress: number, message: string }[]} */
  activeTasks: []
})

export function addTask(task) {
  const existing = state.activeTasks.find(t => t.id === task.id)
  if (existing) {
    Object.assign(existing, task)
  } else {
    state.activeTasks.push(task)
  }
}

export function updateTask(taskId, updates) {
  const task = state.activeTasks.find(t => t.id === taskId)
  if (task) Object.assign(task, updates)
}

export function removeTask(taskId) {
  const idx = state.activeTasks.findIndex(t => t.id === taskId)
  if (idx >= 0) state.activeTasks.splice(idx, 1)
}

export function getTasksForProfile(profileId) {
  return state.activeTasks.filter(t => t.profileId === profileId)
}

export function getActiveTaskCount(profileId) {
  return getTasksForProfile(profileId).length
}

export default state
