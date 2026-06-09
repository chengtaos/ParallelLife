<template>
  <div class="lang-switcher">
    <button
      v-for="loc in locales"
      :key="loc"
      :class="{ active: currentLocale === loc }"
      @click="switchLocale(loc)"
    >
      {{ loc.toUpperCase() }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = ref(locale.value)
const locales = ['zh', 'en']

function switchLocale(loc) {
  currentLocale.value = loc
  locale.value = loc
  localStorage.setItem('locale', loc)
}
</script>

<style scoped>
.lang-switcher { display: flex; gap: 4px; }
.lang-switcher button {
  background: none; border: 1px solid #000;
  padding: 2px 8px; font-size: 11px; font-family: 'JetBrains Mono', monospace;
  color: #999; transition: all 0.2s;
}
.lang-switcher button.active { background: #000; color: #fff; }
.lang-switcher button:hover:not(.active) { color: #666; }
</style>
