<template>
  <div class="branch-view">
    <header class="app-header">
      <div class="brand" @click="router.push('/')">PARALLEL LIFE</div>
      <LanguageSwitcher />
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner-lg"></div>
      <p>{{ $t('branch.loading') }}</p>
    </div>

    <div v-else-if="branch" class="content">
      <div class="back-row">
        <button class="back-btn" @click="router.push(`/profile/${profileId}`)">← {{ $t('decision.backToProfile') }}</button>
      </div>

      <h1 class="branch-title">{{ $t('branch.title') }}</h1>
      <div class="branch-meta">
        <span class="meta-tag">{{ $t('branch.branchLabel') }}: {{ branch.branch_label }}</span>
        <span class="meta-tag">深度: {{ branch.depth }}</span>
      </div>

      <BranchResult v-if="branch.status === 'completed'" :branch="branch" />
      <div v-else-if="branch.status === 'failed'" class="error-state">
        <p>推演失败: {{ branch.error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import BranchResult from '../components/BranchResult.vue'
import { decisionApi } from '../api/decision'

const props = defineProps({ profileId: String, branchId: String })
const router = useRouter()

const branch = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await decisionApi.getBranch(props.profileId, props.branchId)
    branch.value = res.data
  } catch (e) {
    console.error('加载分支失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.branch-view { min-height: 100vh; max-width: 900px; margin: 0 auto; padding: 0 32px; }
.app-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; border-bottom: 1px solid #eee; }
.brand { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: 2px; cursor: pointer; }
.loading-state { padding: 120px 0; text-align: center; }
.spinner-lg { width: 32px; height: 32px; border: 3px solid #eee; border-top-color: #000; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.content { padding: 32px 0 80px; }
.back-row { margin-bottom: 24px; }
.back-btn { background: none; border: none; font-size: 13px; color: #999; font-family: 'JetBrains Mono', monospace; cursor: pointer; }
.branch-title { font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; font-size: 32px; font-weight: 300; margin-bottom: 12px; }
.branch-meta { display: flex; gap: 12px; margin-bottom: 32px; }
.meta-tag { font-size: 11px; background: #000; color: #fff; padding: 3px 10px; font-family: 'JetBrains Mono', monospace; }
.error-state { padding: 40px; border: 1px solid #ff0000; color: #ff0000; }
</style>
