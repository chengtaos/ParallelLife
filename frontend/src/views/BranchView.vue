<template>
  <div class="branch-view">
    <header class="app-header">
      <div class="brand" @click="router.push('/')">PARALLEL LIFE</div>
      <LanguageSwitcher />
    </header>

    <!-- 推演进行中 -->
    <div v-if="generating" class="generating-state">
      <div class="gen-icon">◉</div>
      <h2>正在推演平行人生...</h2>
      <p class="gen-detail">{{ generateMessage }}</p>
      <div class="gen-bar"><div class="gen-fill" :style="{ width: genProgress + '%' }"></div></div>
      <p class="gen-hint">AI 正在推理因果链，这可能需要 30-60 秒</p>
    </div>

    <!-- 加载中 -->
    <div v-else-if="loading" class="loading-state">
      <div class="spinner-lg"></div>
      <p>{{ $t('branch.loading') }}</p>
    </div>

    <!-- 结果 -->
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
        <button class="back-btn" @click="router.push(`/profile/${profileId}`)" style="margin-top:16px">← 返回画像</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import BranchResult from '../components/BranchResult.vue'
import { decisionApi } from '../api/decision'

const props = defineProps({ profileId: String, branchId: String })
const router = useRouter()

const branch = ref(null)
const loading = ref(true)
const generating = ref(false)
const genProgress = ref(0)
const generateMessage = ref('正在检索上下文...')
let pollTimer = null

async function fetchBranch() {
  try {
    const res = await decisionApi.getBranch(props.profileId, props.branchId)
    branch.value = res.data

    if (res.data.status === 'pending' || res.data.status === 'generating') {
      // 还在生成中，进入轮询模式
      loading.value = false
      generating.value = true
      startPolling()
    } else {
      // 已完成或失败
      generating.value = false
      loading.value = false
    }
  } catch (e) {
    console.error('加载分支失败:', e)
    // 可能是刚创建还没保存，进入轮询
    loading.value = false
    generating.value = true
    startPolling()
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const res = await decisionApi.getBranch(props.profileId, props.branchId)
      branch.value = res.data
      genProgress.value = Math.min(genProgress.value + 3, 90)
      generateMessage.value = 'AI 正在推理人生演变...'

      if (res.data.status === 'completed') {
        clearInterval(pollTimer)
        genProgress.value = 100
        generating.value = false
        branch.value = res.data
      } else if (res.data.status === 'failed') {
        clearInterval(pollTimer)
        generating.value = false
        branch.value = res.data
      }
    } catch (e) {
      genProgress.value = Math.min(genProgress.value + 1, 85)
    }
  }, 2000)
}

onMounted(fetchBranch)
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.branch-view { min-height: 100vh; max-width: 900px; margin: 0 auto; padding: 0 32px; }
.app-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; border-bottom: 1px solid #eee; }
.brand { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: 2px; cursor: pointer; }
.loading-state { padding: 120px 0; text-align: center; }
.spinner-lg { width: 32px; height: 32px; border: 3px solid #eee; border-top-color: #000; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

.generating-state { padding: 120px 0; text-align: center; max-width: 480px; margin: 0 auto; }
.gen-icon { font-size: 40px; animation: pulse 2s ease-in-out infinite; margin-bottom: 20px; }
@keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
.generating-state h2 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; margin-bottom: 12px; }
.gen-detail { font-size: 14px; color: #666; margin-bottom: 20px; }
.gen-bar { height: 3px; background: #eee; margin-bottom: 12px; }
.gen-fill { height: 100%; background: #000; transition: width 0.8s ease; }
.gen-hint { font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }

.content { padding: 32px 0 80px; }
.back-row { margin-bottom: 24px; }
.back-btn { background: none; border: none; font-size: 13px; color: #999; font-family: 'JetBrains Mono', monospace; cursor: pointer; }
.branch-title { font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; font-size: 32px; font-weight: 300; margin-bottom: 12px; }
.branch-meta { display: flex; gap: 12px; margin-bottom: 32px; }
.meta-tag { font-size: 11px; background: #000; color: #fff; padding: 3px 10px; font-family: 'JetBrains Mono', monospace; }
.error-state { padding: 40px; border: 1px solid #ff0000; color: #ff0000; }
</style>
