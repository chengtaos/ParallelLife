<template>
  <div class="branch-result">
    <section class="narrative-section">
      <h2>{{ $t('branch.narrative') }}</h2>
      <div class="narrative-text">{{ branch.narrative || '推演中...' }}</div>
    </section>

    <section v-if="branch.causal_chain?.length" class="causal-section">
      <h2>{{ $t('branch.causalChain') }}</h2>
      <div class="causal-list">
        <div v-for="step in branch.causal_chain" :key="step.step_no" class="causal-step">
          <div class="step-header">
            <span class="step-num">{{ $t('branch.stepLabel', { step: step.step_no }) }}</span>
            <span class="step-time">{{ $t('branch.timeOffset', { offset: step.time_offset }) }}</span>
          </div>
          <p class="step-event">{{ step.event }}</p>
          <p class="step-consequence">{{ step.consequence }}</p>
          <div v-if="step.affected_dimensions?.length" class="step-dims">
            <span class="dim-label">{{ $t('branch.affectedDims') }}:</span>
            <span v-for="dim in step.affected_dimensions" :key="dim" class="dim-tag">
              {{ $t(`branch.dimension.${dim}`) }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <section v-if="branch.dimensional_trajectory && Object.keys(branch.dimensional_trajectory).length" class="dims-section">
      <h2>{{ $t('branch.dimensions') }}</h2>

      <div class="timepoint-tabs">
        <button v-for="tp in availableTimePoints" :key="tp"
                :class="{ active: currentTimePoint === tp }" @click="currentTimePoint = tp">
          {{ tp === 'baseline' ? $t('branch.baseline') : $t('branch.timePoint', { time: tp }) }}
        </button>
      </div>

      <DimRadar :trajectory="branch.dimensional_trajectory" :currentTimePoint="currentTimePoint" />

      <div v-if="currentScores" class="score-list">
        <div v-for="dim in dims" :key="dim" class="score-item">
          <div class="score-header">
            <span class="score-name">{{ $t(`branch.dimension.${dim}`) }}</span>
            <span class="score-value">{{ currentScores[dim]?.score || 0 }}</span>
          </div>
          <div class="score-bar">
            <div class="score-fill" :style="{ width: (currentScores[dim]?.score || 0) + '%' }"></div>
          </div>
          <p class="score-reason">{{ currentScores[dim]?.reasoning || '' }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import DimRadar from './DimRadar.vue'

const props = defineProps({ branch: Object })

const dims = ['career_achievement', 'wealth', 'social_density', 'happiness', 'location_stability', 'health', 'self_fulfillment']

const availableTimePoints = computed(() => {
  if (!props.branch.dimensional_trajectory) return []
  return Object.keys(props.branch.dimensional_trajectory)
})

const currentTimePoint = ref('baseline')

watch(() => props.branch, () => {
  if (availableTimePoints.value.length) {
    currentTimePoint.value = availableTimePoints.value[availableTimePoints.value.length - 1]
  }
}, { immediate: true })

const currentScores = computed(() => {
  if (!props.branch.dimensional_trajectory) return null
  return props.branch.dimensional_trajectory[currentTimePoint.value]
})
</script>

<style scoped>
.branch-result { max-width: 800px; }
section { margin-bottom: 40px; }
h2 { font-family: 'Space Grotesk', sans-serif; font-size: 20px; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #eee; }
.narrative-text { font-size: 15px; line-height: 1.8; color: #333; }

.causal-list { position: relative; padding-left: 20px; }
.causal-list::before { content: ''; position: absolute; left: 8px; top: 0; bottom: 0; width: 1px; background: #ddd; }
.causal-step { margin-bottom: 20px; position: relative; }
.causal-step::before { content: ''; position: absolute; left: -16px; top: 8px; width: 8px; height: 8px; background: #fff; border: 1.5px solid #000; border-radius: 50%; }
.step-header { display: flex; gap: 12px; align-items: baseline; margin-bottom: 6px; }
.step-num { font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.step-time { font-size: 11px; color: #999; font-family: 'JetBrains Mono', monospace; }
.step-event { font-size: 14px; color: #333; margin-bottom: 4px; }
.step-consequence { font-size: 13px; color: #666; font-style: italic; }
.step-dims { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
.dim-label { font-size: 11px; color: #999; }
.dim-tag { font-size: 10px; background: #f0f0f0; padding: 2px 6px; font-family: 'JetBrains Mono', monospace; }

.timepoint-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
.timepoint-tabs button { padding: 6px 12px; background: none; border: 1px solid #ddd; font-size: 12px; font-family: 'JetBrains Mono', monospace; transition: all 0.2s; }
.timepoint-tabs button.active { background: #000; color: #fff; border-color: #000; }

.score-list { margin-top: 24px; }
.score-item { margin-bottom: 16px; padding: 12px; border: 1px solid #f5f5f5; }
.score-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.score-name { font-size: 13px; font-weight: 500; }
.score-value { font-size: 20px; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }
.score-bar { height: 4px; background: #eee; margin-bottom: 6px; }
.score-fill { height: 100%; background: #000; transition: width 0.5s ease; }
.score-reason { font-size: 12px; color: #999; line-height: 1.5; }
</style>
