import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ProfileView from '../views/ProfileView.vue'
import BranchView from '../views/BranchView.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/profile/:profileId', name: 'Profile', component: ProfileView, props: true },
  { path: '/branch/:profileId/:branchId', name: 'Branch', component: BranchView, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
