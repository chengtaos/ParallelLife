<template>
  <div class="decision-card">
    <div class="decision-header">
      <div class="timeline-dot"></div>
      <div class="decision-meta">
        <span class="stage-badge">{{ stageLabel }}</span>
        <span class="decision-time">{{ decision.timestamp }}</span>
      </div>
    </div>
    <p class="scenario">{{ decision.scenario }}</p>
    <div class="branches-list">
      <div v-for="(b, idx) in decision.branches" :key="idx" class="branch-item" :class="{ actual: b.is_actual }">
        <span class="branch-marker">{{ b.is_actual ? '✓' : '○' }}</span>
        <span class="branch-label">{{ b.label }}</span>
        <span v-if="b.is_actual" class="actual-tag">{{ $t('decision.actualLabel') }}</span>
      </div>
    </div>
    <button v-if="!hideExplore" class="explore-btn" @click="$emit('explore', decision)">
      {{ $t('profile.exploreBtn') }} →
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  decision: Object,
  hideExplore: Boolean
})

defineEmits(['explore'])

const stageLabels = {
  high_school: '高中', college: '大学', early_career: '初入职场',
  mid_career: '职业中期', late_career: '职业后期'
}
const stageLabel = computed(() => stageLabels[props.decision.life_stage] || props.decision.life_stage || '人生阶段')
</script>

<style scoped>
.decision-card { border: 1px solid #eee; padding: 24px; margin-bottom: 16px; position: relative; transition: border-color 0.2s; }
.decision-card:hover { border-color: #000; }
.decision-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.timeline-dot { width: 10px; height: 10px; background: #000; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.decision-meta { display: flex; gap: 10px; align-items: center; }
.stage-badge { font-size: 11px; background: #000; color: #fff; padding: 2px 8px; font-family: 'JetBrains Mono', monospace; }
.decision-time { font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }
.scenario { font-size: 14px; line-height: 1.6; color: #333; margin-bottom: 16px; }
.branches-list { margin-bottom: 16px; }
.branch-item { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; font-size: 14px; }
.branch-item.actual { font-weight: 600; }
.branch-marker { font-size: 14px; width: 20px; }
.branch-label { flex: 1; }
.actual-tag { font-size: 10px; background: #000; color: #fff; padding: 2px 6px; font-family: 'JetBrains Mono', monospace; }
.explore-btn { background: none; border: 1px solid #000; padding: 8px 16px; font-size: 13px; font-family: 'JetBrains Mono', monospace; transition: all 0.2s; }
.explore-btn:hover { background: #000; color: #fff; }
</style>
