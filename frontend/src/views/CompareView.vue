<template>
  <div class="compare-view">
    <header class="app-header">
      <div class="brand" @click="router.push('/')">PARALLEL LIFE</div>
      <LanguageSwitcher />
    </header>

    <div class="content">
      <div class="back-row">
        <button class="back-btn" @click="router.push(`/profile/${profileId}`)">← 返回画像</button>
      </div>

      <h1>分支对比</h1>
      <p class="subtitle">选择 2-3 条已推演的分支，AI 将分析它们的关键差异</p>

      <!-- 选择分支 -->
      <section v-if="!comparing && !result" class="select-section">
        <div v-if="branches.length === 0" class="empty">还没有推演结果，先去探索几条平行人生吧</div>
        <div v-else class="branch-grid">
          <div v-for="b in branches" :key="b.branch_id"
               class="branch-card" :class="{ selected: selectedIds.includes(b.branch_id) }"
               @click="toggleSelect(b.branch_id, b.status)">
            <div class="card-top">
              <span class="check">{{ selectedIds.includes(b.branch_id) ? '●' : '○' }}</span>
              <span class="card-label">{{ b.branch_label }}</span>
            </div>
            <div class="card-meta">深度 {{ b.depth }} · {{ b.status === 'completed' ? '已完成' : '推演中' }}</div>
            <p class="card-preview">{{ b.narrative ? b.narrative.slice(0, 80) + '...' : '暂无叙事' }}</p>
          </div>
        </div>

        <button v-if="branches.length >= 2" class="compare-btn"
                :disabled="selectedIds.length < 2 || selectedIds.length > 3"
                @click="startCompare">
          {{ selectedIds.length < 2 ? '请选择至少 2 条分支' : `对比 ${selectedIds.length} 条分支 →` }}
        </button>
      </section>

      <!-- 对比进行中 -->
      <section v-if="comparing" class="generating">
        <div class="gen-icon">◉</div>
        <p>AI 正在分析各路径差异...</p>
        <div class="gen-bar"><div class="gen-fill" :style="{ width: genProgress + '%' }"></div></div>
      </section>

      <!-- 对比结果 -->
      <section v-if="result" class="result-section">
        <button class="redo-btn" @click="reset">← 重新对比</button>

        <!-- 摘要 -->
        <div class="result-block">
          <h2>整体对比</h2>
          <p class="summary-text">{{ result.diff_summary }}</p>
        </div>

        <!-- 维度对比 -->
        <div class="result-block">
          <h2>维度差异</h2>
          <div v-for="(analysis, dim) in result.dimension_diff" :key="dim" class="dim-row">
            <div class="dim-header">
              <span class="dim-name">{{ $t(`branch.dimension.${dim}`) }}</span>
              <span class="dim-best">最佳路径：{{ analysis.best_path }}</span>
            </div>
            <p class="dim-analysis">{{ analysis.analysis }}</p>
          </div>
        </div>

        <!-- 关键转折点 -->
        <div v-if="result.key_turning_points?.length" class="result-block">
          <h2>关键转折点</h2>
          <div v-for="(tp, i) in result.key_turning_points" :key="i" class="turning-point">
            <div class="tp-header">
              <span class="tp-num">{{ i + 1 }}</span>
              <span class="tp-time">{{ tp.time }}</span>
            </div>
            <p class="tp-event">{{ tp.event }}</p>
            <p class="tp-impact">{{ tp.impact }}</p>
          </div>
        </div>

        <!-- 深度洞察 -->
        <div class="result-block insight">
          <h2>深度洞察</h2>
          <p class="insight-text">{{ result.insight }}</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import { decisionApi } from '../api/decision'
import { compareApi } from '../api/compare'

const props = defineProps({ profileId: String })
const router = useRouter()

const branches = ref([])
const selectedIds = ref([])
const comparing = ref(false)
const genProgress = ref(0)
const result = ref(null)

onMounted(async () => {
  try {
    const res = await decisionApi.listBranches(props.profileId)
    branches.value = (res.data || []).filter(b => b.status === 'completed')
  } catch (e) {
    console.error('加载分支失败:', e)
  }
})

function toggleSelect(id, status) {
  if (status !== 'completed') return
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) {
    selectedIds.value.splice(idx, 1)
  } else if (selectedIds.value.length < 3) {
    selectedIds.value.push(id)
  }
}

async function startCompare() {
  comparing.value = true
  genProgress.value = 0
  try {
    const res = await compareApi.compare(props.profileId, selectedIds.value)
    const taskId = res.data.task_id
    const poll = setInterval(async () => {
      genProgress.value = Math.min(genProgress.value + 5, 90)
      try {
        const s = await compareApi.getTaskStatus(taskId)
        if (s.data.status === 'completed') {
          clearInterval(poll)
          genProgress.value = 100
          result.value = s.data.result.comparison
          comparing.value = false
        } else if (s.data.status === 'failed') {
          clearInterval(poll)
          comparing.value = false
          alert('对比失败: ' + (s.data.error || '未知错误'))
        }
      } catch (e) { /* continue polling */ }
    }, 2000)
  } catch (e) {
    comparing.value = false
    alert('对比失败: ' + e.message)
  }
}

function reset() {
  result.value = null
  selectedIds.value = []
}
</script>

<style scoped>
.compare-view { min-height: 100vh; max-width: 900px; margin: 0 auto; padding: 0 32px; }
.app-header { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; border-bottom: 1px solid #eee; }
.brand { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: 2px; cursor: pointer; }
.content { padding: 32px 0 80px; }
.back-row { margin-bottom: 24px; }
.back-btn { background: none; border: none; font-size: 13px; color: #999; font-family: 'JetBrains Mono', monospace; cursor: pointer; }
h1 { font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; font-size: 32px; font-weight: 300; margin-bottom: 8px; }
.subtitle { font-size: 14px; color: #666; margin-bottom: 32px; }

.select-section { }
.empty { color: #999; padding: 60px 0; text-align: center; }
.branch-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; margin-bottom: 24px; }
.branch-card { border: 1px solid #eee; padding: 16px; cursor: pointer; transition: all 0.2s; }
.branch-card:hover { border-color: #999; }
.branch-card.selected { border-color: #000; background: #fafafa; }
.card-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.check { font-size: 12px; color: #000; }
.card-label { font-size: 14px; font-weight: 600; }
.card-meta { font-size: 11px; color: #999; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px; }
.card-preview { font-size: 12px; color: #666; line-height: 1.5; }
.compare-btn { margin-top: 16px; padding: 12px 28px; background: #000; color: #fff; border: none; font-size: 14px; font-family: 'Space Grotesk', sans-serif; }
.compare-btn:disabled { background: #ccc; cursor: not-allowed; }

.generating { padding: 80px 0; text-align: center; }
.gen-icon { font-size: 40px; animation: pulse 2s ease-in-out infinite; margin-bottom: 16px; }
@keyframes pulse { 0%,100%{opacity:.3} 50%{opacity:1} }
.gen-bar { height: 3px; background: #eee; max-width: 320px; margin: 16px auto 0; }
.gen-fill { height: 100%; background: #000; transition: width 0.5s ease; }

.result-section { }
.redo-btn { background: none; border: 1px solid #000; padding: 8px 16px; font-size: 12px; font-family: 'JetBrains Mono', monospace; margin-bottom: 32px; cursor: pointer; }
.result-block { margin-bottom: 40px; }
.result-block h2 { font-family: 'Space Grotesk', sans-serif; font-size: 20px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #eee; }
.summary-text { font-size: 15px; line-height: 1.8; color: #333; }

.dim-row { padding: 16px; border: 1px solid #f5f5f5; margin-bottom: 12px; }
.dim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.dim-name { font-size: 14px; font-weight: 600; }
.dim-best { font-size: 11px; background: #000; color: #fff; padding: 2px 8px; font-family: 'JetBrains Mono', monospace; }
.dim-analysis { font-size: 13px; color: #555; line-height: 1.6; }

.turning-point { padding: 16px 16px 16px 40px; border-left: 1px solid #ddd; margin-bottom: 16px; position: relative; }
.turning-point::before { content: ''; position: absolute; left: -4px; top: 20px; width: 7px; height: 7px; background: #000; border-radius: 50%; }
.tp-header { display: flex; gap: 12px; align-items: baseline; margin-bottom: 6px; }
.tp-num { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.tp-time { font-size: 11px; color: #999; font-family: 'JetBrains Mono', monospace; }
.tp-event { font-size: 14px; color: #333; margin-bottom: 4px; }
.tp-impact { font-size: 13px; color: #666; font-style: italic; }

.insight { background: #fafafa; padding: 24px; border: 1px solid #eee; }
.insight-text { font-size: 15px; line-height: 1.9; color: #333; }
</style>
