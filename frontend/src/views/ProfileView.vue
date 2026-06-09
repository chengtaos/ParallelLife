<template>
  <div class="profile-view">
    <header class="app-header">
      <div class="brand" @click="router.push('/')">PARALLEL LIFE</div>
      <LanguageSwitcher />
    </header>

    <div v-if="loading" class="loading-state">{{ $t('common.loading') }}</div>
    <div v-else-if="profile" class="content">
      <div class="back-row">
        <button class="back-btn" @click="router.push('/')">← {{ $t('profile.backBtn') }}</button>
        <button class="delete-btn" @click="confirmDelete">{{ $t('profile.deleteBtn') }}</button>
      </div>

      <h1 class="profile-name">{{ profile.name }}</h1>
      <div class="status-row">
        <span class="status-badge" :class="profile.status">{{ profile.status }}</span>
        <span v-if="profile.graph_id" class="graph-id">Graph: {{ profile.graph_id }}</span>
      </div>

      <section v-if="profile.basic_info && Object.keys(profile.basic_info).length" class="info-section">
        <h2>{{ $t('profile.basicInfo') }}</h2>
        <div class="info-grid">
          <div v-if="profile.basic_info.age" class="info-item">
            <span class="info-label">年龄</span><span class="info-value">{{ profile.basic_info.age }}岁</span>
          </div>
          <div v-if="profile.basic_info.gender" class="info-item">
            <span class="info-label">性别</span><span class="info-value">{{ profile.basic_info.gender }}</span>
          </div>
          <div v-if="profile.basic_info.location?.current" class="info-item">
            <span class="info-label">现居</span><span class="info-value">{{ profile.basic_info.location.current }}</span>
          </div>
        </div>
        <div v-if="profile.basic_info.education?.length" class="info-list">
          <h3>教育经历</h3>
          <div v-for="edu in profile.basic_info.education" :key="edu.school" class="list-item">
            {{ edu.level }} · {{ edu.school }} · {{ edu.major }} · {{ edu.year }}
          </div>
        </div>
        <div v-if="profile.basic_info.career?.length" class="info-list">
          <h3>职业经历</h3>
          <div v-for="job in profile.basic_info.career" :key="job.company" class="list-item">
            {{ job.company }} · {{ job.role }} · {{ job.years }}
          </div>
        </div>
      </section>

      <section class="decisions-section">
        <div class="section-title-row">
          <h2>{{ $t('profile.decisions') }}</h2>
          <span v-if="branches.length" class="branch-count">{{ branches.filter(b => b.status === 'completed').length }} 次推演</span>
          <button v-if="branches.filter(b => b.status === 'completed').length >= 2"
                  class="compare-link" @click="router.push(`/compare/${profileId}`)">对比分支 →</button>
        </div>
        <div v-if="decisions.length === 0" class="empty">{{ $t('profile.noDecisions') }}</div>
        <DecisionCard v-for="d in decisions" :key="d.decision_id" :decision="d" @explore="openExplore(d)" />
      </section>

      <!-- 决策模式分析 -->
      <section v-if="decisions.length > 0 || branches.length > 0" class="pattern-section">
        <div class="section-title-row">
          <h2>决策模式</h2>
          <button v-if="!pattern && !patternLoading" class="pattern-btn" @click="loadPattern">分析 →</button>
          <span v-if="patternLoading" class="loading-tag">分析中...</span>
        </div>

        <div v-if="pattern" class="pattern-result">
          <div class="pattern-card primary">
            <div class="pattern-label">决策风格</div>
            <div class="pattern-value large">{{ pattern.decision_style }}</div>
          </div>

          <div class="pattern-grid">
            <div class="pattern-card">
              <div class="pattern-label">风险偏好</div>
              <div class="pattern-value">{{ pattern.risk_preference?.level }}</div>
              <p class="pattern-detail">{{ pattern.risk_preference?.analysis }}</p>
            </div>
            <div class="pattern-card">
              <div class="pattern-label">核心价值观</div>
              <div class="pattern-value">{{ pattern.value_orientation?.primary }}</div>
              <p class="pattern-detail">{{ pattern.value_orientation?.analysis }}</p>
            </div>
          </div>

          <div v-if="pattern.patterns?.length" class="pattern-list">
            <div v-for="(p, i) in pattern.patterns" :key="i" class="pattern-item">
              <span class="p-num">{{ i + 1 }}</span>
              <div>
                <span class="p-name">{{ p.pattern }}</span>
                <p class="p-evidence">{{ p.evidence }}</p>
              </div>
            </div>
          </div>

          <div class="pattern-insight">
            <p>{{ pattern.insight }}</p>
          </div>
        </div>
      </section>

      <div v-if="exploreTarget" class="overlay" @mousedown.self="exploreTarget = null">
        <div class="explore-modal">
          <h2>{{ $t('decision.exploreTitle') }}</h2>
          <p class="scenario-text">{{ exploreTarget.scenario }}</p>
          <div class="branch-options">
            <div v-for="(b, idx) in exploreTarget.branches" :key="idx"
                 class="branch-option" :class="{ selected: selectedBranch === idx, actual: b.is_actual }">
              <input v-if="!b.is_actual" v-model="b.label"
                     class="branch-input" @focus="selectedBranch = idx" />
              <span v-else>{{ b.label }}</span>
              <span v-if="b.is_actual" class="small-tag">{{ $t('decision.actualLabel') }}</span>
            </div>
          </div>
          <div class="depth-selector">
            <label>{{ $t('decision.depthLabel') }}</label>
            <div class="depth-options">
              <button v-for="d in depths" :key="d" :class="{ active: selectedDepth === d }" @click="selectedDepth = d">
                {{ $t(`decision.depth${d}`) }}
              </button>
            </div>
          </div>
          <div class="modal-actions">
            <button class="submit-btn" @click="startExplore" :disabled="exploring">
              <span v-if="exploring" class="spinner"></span>
              {{ exploring ? $t('decision.exploring') : $t('decision.startExplore') }}
            </button>
            <button class="cancel-btn" @click="exploreTarget = null">{{ $t('common.cancel') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import DecisionCard from '../components/DecisionCard.vue'
import { profileApi } from '../api/profile'
import { decisionApi } from '../api/decision'
import { toast } from '../toast'

const props = defineProps({ profileId: String })
const router = useRouter()

const profile = ref(null)
const decisions = ref([])
const loading = ref(true)

const exploreTarget = ref(null)
const selectedBranch = ref(-1)
const selectedDepth = ref('5y')
const exploring = ref(false)
const depths = ['1y', '3y', '5y', '10y']

const branches = ref([])
const pattern = ref(null)
const patternLoading = ref(false)

async function loadPattern() {
  patternLoading.value = true
  try {
    const res = await profileApi.getPattern(props.profileId)
    pattern.value = res.data
  } catch (e) {
    console.error('模式分析失败:', e)
  } finally {
    patternLoading.value = false
  }
}

async function loadProfile() {
  loading.value = true
  try {
    const [pRes, dRes, bRes] = await Promise.all([
      profileApi.get(props.profileId),
      decisionApi.list(props.profileId),
      decisionApi.listBranches(props.profileId)
    ])
    profile.value = pRes.data
    decisions.value = dRes.data || []
    branches.value = bRes.data || []
  } catch (e) {
    console.error('加载画像失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)

// 从推演页返回时自动刷新
const route = useRoute()
watch(() => route.fullPath, () => {
  if (route.name === 'Profile') loadProfile()
})

function openExplore(decision) {
  exploreTarget.value = decision
  selectedBranch.value = -1
  selectedDepth.value = '5y'
}

async function startExplore() {
  if (selectedBranch.value < 0) return
  exploring.value = true
  try {
    const branchLabel = exploreTarget.value.branches[selectedBranch.value].label
    const res = await decisionApi.explore(props.profileId, exploreTarget.value.decision_id, branchLabel, selectedDepth.value)
    const taskId = res.data.task_id
    const branchId = res.data.branch_id
    const startedAt = Date.now()
    const poll = setInterval(async () => {
      if (Date.now() - startedAt > 180000) {
        clearInterval(poll)
        exploring.value = false
        toast('推演超时，请重试', 'error')
        return
      }
      const statusRes = await decisionApi.getTaskStatus(taskId)
      if (statusRes.data.status === 'completed') {
        clearInterval(poll)
        router.push(`/branch/${props.profileId}/${branchId}`)
      } else if (statusRes.data.status === 'failed') {
        clearInterval(poll)
        exploring.value = false
        toast('推演失败: ' + (statusRes.data.error || '未知错误'), 'error')
      }
    }, 2000)
  } catch (e) {
    exploring.value = false
    toast('推演失败: ' + e.message, 'error')
  }
}

async function confirmDelete() {
  if (!confirm('确定要删除这个画像吗？所有关联的决策和推演结果将被永久删除。')) return
  try {
    await profileApi.delete(props.profileId)
    router.push('/')
  } catch (e) {
    toast('删除失败: ' + e.message, 'error')
  }
}
</script>

<style scoped>
.profile-view { min-height: 100vh; max-width: 900px; margin: 0 auto; padding: 0 32px; }
.app-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; border-bottom: 1px solid #eee; }
.brand { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: 2px; cursor: pointer; }
.loading-state { padding: 80px 0; text-align: center; color: #999; }
.content { padding: 32px 0 80px; }
.back-row { margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
.back-btn { background: none; border: none; font-size: 13px; color: #999; font-family: 'JetBrains Mono', monospace; cursor: pointer; }
.delete-btn { background: none; border: 1px solid #ff0000; color: #ff0000; padding: 6px 14px; font-size: 12px; font-family: 'JetBrains Mono', monospace; cursor: pointer; transition: all 0.2s; }
.delete-btn:hover { background: #ff0000; color: #fff; }
.profile-name { font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; font-size: 36px; font-weight: 300; margin-bottom: 12px; }
.status-row { display: flex; gap: 12px; align-items: center; margin-bottom: 32px; }
.status-badge { font-size: 11px; padding: 3px 10px; font-family: 'JetBrains Mono', monospace; }
.status-badge.ready { background: #000; color: #fff; }
.status-badge.failed { background: #ff0000; color: #fff; }
.status-badge.created, .status-badge.graph_built { background: #eee; color: #999; }
.graph-id { font-size: 11px; color: #999; font-family: 'JetBrains Mono', monospace; }

.info-section { margin-bottom: 40px; padding: 24px; border: 1px solid #eee; }
.info-section h2 { font-family: 'Space Grotesk', sans-serif; font-size: 18px; margin-bottom: 16px; }
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-label { font-size: 11px; color: #999; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
.info-value { font-size: 16px; font-weight: 500; }
.info-list { margin-bottom: 16px; }
.info-list h3 { font-size: 12px; color: #999; text-transform: uppercase; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace; }
.list-item { font-size: 14px; padding: 6px 0; border-bottom: 1px solid #f5f5f5; }
.decisions-section h2 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; }
.section-title-row { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; }
.branch-count { font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }
.compare-link { background: none; border: 1px solid #000; padding: 4px 12px; font-size: 12px; font-family: 'JetBrains Mono', monospace; cursor: pointer; transition: all 0.2s; margin-left: auto; }
.compare-link:hover { background: #000; color: #fff; }

.overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 100; }
.explore-modal { background: #fff; border: 1px solid #000; padding: 40px; max-width: 560px; width: 90%; max-height: 80vh; overflow-y: auto; }
.explore-modal h2 { font-family: 'Space Grotesk', sans-serif; font-size: 22px; margin-bottom: 16px; }
.scenario-text { font-size: 14px; color: #555; margin-bottom: 20px; line-height: 1.6; }
.branch-options { margin-bottom: 20px; }
.branch-option { padding: 12px; border: 1px solid #eee; margin-bottom: 8px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-size: 14px; transition: border-color 0.2s; }
.branch-option.selected { border-color: #000; background: #fafafa; }
.branch-option.actual { font-weight: 600; }
.branch-input { width: 100%; border: none; border-bottom: 1px dashed #ccc; outline: none; font-size: 14px; font-family: 'JetBrains Mono', 'Noto Sans SC', monospace; background: transparent; padding: 2px 0; }
.branch-input:focus { border-bottom-color: #000; }
.small-tag { font-size: 10px; background: #000; color: #fff; padding: 2px 6px; font-family: 'JetBrains Mono', monospace; }
.depth-selector { margin-bottom: 24px; }
.depth-selector label { display: block; font-size: 12px; color: #999; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
.depth-options { display: flex; gap: 8px; }
.depth-options button { flex: 1; padding: 8px; background: none; border: 1px solid #ddd; font-size: 13px; font-family: 'JetBrains Mono', monospace; transition: all 0.2s; }
.depth-options button.active { background: #000; color: #fff; border-color: #000; }
.modal-actions { display: flex; gap: 12px; }
.submit-btn { padding: 12px 24px; background: #000; color: #fff; border: none; font-size: 14px; font-family: 'Space Grotesk', sans-serif; display: inline-flex; align-items: center; gap: 8px; }
.submit-btn:disabled { background: #999; cursor: not-allowed; }
.cancel-btn { padding: 12px 24px; background: none; border: 1px solid #000; font-size: 14px; font-family: 'Space Grotesk', sans-serif; }
.spinner { width: 14px; height: 14px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty { color: #999; padding: 24px 0; }

.pattern-section { margin-top: 40px; padding-top: 32px; border-top: 1px solid #eee; }
.pattern-btn { background: none; border: 1px solid #000; padding: 4px 12px; font-size: 12px; font-family: 'JetBrains Mono', monospace; cursor: pointer; transition: all 0.2s; }
.pattern-btn:hover { background: #000; color: #fff; }
.loading-tag { font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }

.pattern-result { margin-top: 20px; }
.pattern-card { padding: 16px; border: 1px solid #f5f5f5; margin-bottom: 12px; }
.pattern-card.primary { background: #000; color: #fff; border-color: #000; }
.pattern-card.primary .pattern-label { color: rgba(255,255,255,0.6); }
.pattern-card.primary .pattern-value { color: #fff; }
.pattern-label { font-size: 11px; color: #999; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; margin-bottom: 4px; }
.pattern-value { font-size: 16px; font-weight: 600; }
.pattern-value.large { font-size: 22px; font-family: 'Space Grotesk', sans-serif; }
.pattern-detail { font-size: 13px; color: #666; line-height: 1.6; margin-top: 8px; }
.pattern-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.pattern-list { margin-bottom: 20px; }
.pattern-item { display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid #f5f5f5; }
.p-num { font-size: 12px; font-weight: 700; color: #999; font-family: 'JetBrains Mono', monospace; flex-shrink: 0; }
.p-name { font-size: 14px; font-weight: 500; }
.p-evidence { font-size: 12px; color: #999; margin-top: 4px; }

.pattern-insight { background: #fafafa; padding: 20px; border: 1px solid #eee; }
.pattern-insight p { font-size: 14px; line-height: 1.8; color: #333; }
</style>
