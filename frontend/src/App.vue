<template>
  <router-view />
  <div v-if="ts.visible.value" class="toast" :class="ts.type.value" @click="ts.visible.value = false">
    {{ ts.message.value }}
  </div>
</template>

<script setup>
import { toastState as ts } from './toast'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f1f1; }
::-webkit-scrollbar-thumb { background: #000000; }
::-webkit-scrollbar-thumb:hover { background: #333333; }

button { font-family: inherit; cursor: pointer; }

.toast {
  position: fixed; bottom: 32px; left: 50%; transform: translateX(-50%);
  padding: 12px 28px; font-size: 14px; font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
  color: #fff; cursor: pointer; z-index: 9999; animation: toastUp 0.3s ease;
  max-width: 90vw; text-align: center;
}
.toast.info { background: #000; }
.toast.error { background: #d00; }
@keyframes toastUp { from { opacity: 0; transform: translateX(-50%) translateY(16px); } to { opacity: 1; transform: translateX(-50%) translateY(0); } }
</style>
