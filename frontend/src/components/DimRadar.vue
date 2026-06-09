<template>
  <div class="dim-radar">
    <div class="chart-container" ref="chartRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  trajectory: Object,
  currentTimePoint: String
})
const chartRef = ref(null)

const DIMS = ['career_achievement', 'wealth', 'social_density', 'happiness', 'location_stability', 'health', 'self_fulfillment']
const DIM_LABELS = {
  career_achievement: '职业', wealth: '财富', social_density: '人际',
  happiness: '幸福', location_stability: '地理', health: '健康', self_fulfillment: '自我实现'
}

function drawChart() {
  if (!chartRef.value || !props.trajectory) return
  const container = chartRef.value
  container.innerHTML = ''

  const data = props.trajectory[props.currentTimePoint]
  if (!data) return

  const width = 320, height = 320, margin = 40
  const radius = Math.min(width, height) / 2 - margin

  const svg = d3.select(container)
    .append('svg').attr('width', width).attr('height', height)
    .append('g').attr('transform', `translate(${width / 2},${height / 2})`)

  const angleSlice = (Math.PI * 2) / DIMS.length
  const rScale = d3.scaleLinear().range([0, radius]).domain([0, 100])

  const levels = [20, 40, 60, 80]
  levels.forEach(level => {
    svg.append('circle').attr('r', rScale(level))
      .attr('fill', 'none').attr('stroke', '#eee').attr('stroke-width', 0.5)
    svg.append('text').attr('y', -rScale(level)).attr('dy', '-0.35em')
      .attr('text-anchor', 'middle').attr('font-size', '8px').attr('fill', '#ccc')
      .text(level)
  })

  DIMS.forEach((dim, i) => {
    const angle = angleSlice * i - Math.PI / 2
    const x = rScale(105) * Math.cos(angle)
    const y = rScale(105) * Math.sin(angle)
    svg.append('text').attr('x', x).attr('y', y)
      .attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
      .attr('font-size', '11px').attr('font-family', 'JetBrains Mono, Noto Sans SC, monospace')
      .attr('fill', '#666').text(DIM_LABELS[dim])
    svg.append('line').attr('x1', 0).attr('y1', 0)
      .attr('x2', rScale(100) * Math.cos(angle)).attr('y2', rScale(100) * Math.sin(angle))
      .attr('stroke', '#eee').attr('stroke-width', 0.5)
  })

  const points = DIMS.map((dim, i) => {
    const score = data[dim]?.score || 50
    const angle = angleSlice * i - Math.PI / 2
    return [rScale(score) * Math.cos(angle), rScale(score) * Math.sin(angle)]
  })

  svg.append('polygon')
    .attr('points', points.map(p => p.join(',')).join(' '))
    .attr('fill', 'rgba(0,0,0,0.08)').attr('stroke', '#000').attr('stroke-width', 1.5)

  points.forEach(([x, y]) => {
    svg.append('circle').attr('cx', x).attr('cy', y).attr('r', 3).attr('fill', '#000')
  })
}

onMounted(() => { nextTick(drawChart) })
watch(() => [props.trajectory, props.currentTimePoint], () => { nextTick(drawChart) }, { deep: true })
</script>

<style scoped>
.dim-radar { display: flex; justify-content: center; }
.chart-container { width: 320px; height: 320px; }
</style>
