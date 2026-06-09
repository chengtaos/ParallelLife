<template>
  <Teleport to="body">
    <div v-if="visible" class="toast" :class="type" @click="hide">
      {{ message }}
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('info') // info | error
let timer = null

function show(msg, t = 'info') {
  if (timer) clearTimeout(timer)
  message.value = msg
  type.value = t
  visible.value = true
  timer = setTimeout(hide, 4000)
}

function hide() {
  visible.value = false
  if (timer) clearTimeout(timer)
}

defineExpose({ show, hide })
</script>

<style scoped>
.toast {
  position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%);
  padding: 12px 28px; font-size: 14px; font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  color: #fff; cursor: pointer; z-index: 9999; animation: slideUp 0.3s ease;
  max-width: 90vw; text-align: center;
}
.toast.info { background: #000; }
.toast.error { background: #d00; }
@keyframes slideUp { from { opacity: 0; transform: translateX(-50%) translateY(16px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
</style>
