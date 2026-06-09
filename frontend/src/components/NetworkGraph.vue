<template>
  <div class="network-graph">
    <div v-if="!data || data.nodes.length === 0" class="empty">暂无关系数据</div>
    <svg ref="svgRef" v-else></svg>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'

const props = defineProps({ data: Object })
const svgRef = ref(null)

function render() {
  if (!svgRef.value || !props.data?.nodes?.length) return

  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const width = 700, height = 420
  svg.attr('viewBox', `0 0 ${width} ${height}`)

  const nodes = props.data.nodes.map(d => ({ ...d }))
  const edges = props.data.edges.map(d => ({ ...d }))

  const sim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(30))

  const link = svg.append('g')
    .selectAll('line').data(edges).join('line')
    .attr('stroke', '#ddd').attr('stroke-width', 1)

  const nodeSize = d => d.importance === 'high' ? 12 : d.importance === 'low' ? 6 : 9
  const nodeColor = d => d.type === 'Organization' ? '#000' : d.type === 'Location' ? '#999' : '#555'

  const node = svg.append('g')
    .selectAll('g').data(nodes).join('g')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y })
      .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null })
    )

  node.append('circle')
    .attr('r', nodeSize)
    .attr('fill', nodeColor)
    .attr('stroke', '#fff').attr('stroke-width', 2)

  node.append('text')
    .text(d => d.id)
    .attr('x', d => nodeSize(d) + 6).attr('y', 4)
    .attr('font-size', '11px').attr('font-family', 'JetBrains Mono, Noto Sans SC, monospace')
    .attr('fill', '#333')

  node.append('title').text(d => `${d.id}${d.role ? ' · ' + d.role : ''}\n${d.description}`)

  sim.on('tick', () => {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    node.attr('transform', d => `translate(${d.x},${d.y})`)
  })
}

onMounted(() => { nextTick(render) })
watch(() => props.data, () => { nextTick(render) }, { deep: true })
</script>

<style scoped>
.network-graph { width: 100%; overflow: hidden; }
.network-graph svg { width: 100%; height: auto; }
.empty { color: #999; padding: 40px; text-align: center; font-size: 13px; }
</style>
