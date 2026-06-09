<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">{{ $t('nav.brand') }}</div>
      <div class="nav-links">
        <LanguageSwitcher />
      </div>
    </nav>

    <div class="main-content">
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">{{ $t('home.tagline') }}</span>
            <span class="version-text">{{ $t('home.version') }}</span>
          </div>
          <h1 class="main-title">
            {{ $t('home.heroTitle1') }}<br>
            <span class="gradient-text">{{ $t('home.heroTitle2') }}</span>
          </h1>
          <p class="hero-desc">{{ $t('home.heroDesc') }}</p>
          <p class="slogan-text">{{ $t('home.slogan') }}<span class="blinking-cursor">_</span></p>
        </div>
        <div class="hero-right">
          <button class="create-btn" @click="showCreate = true">{{ $t('home.startBtn') }} →</button>
        </div>
      </section>

      <section v-if="showCreate" class="create-section">
        <div class="create-card">
          <h2>{{ $t('profile.createTitle') }}</h2>
          <div class="form-group">
            <label>{{ $t('profile.nameLabel') }}</label>
            <input v-model="profileName" :placeholder="$t('profile.namePlaceholder')" class="input" />
          </div>
          <div class="form-group">
            <label>{{ $t('profile.textLabel') }}</label>
            <textarea v-model="profileText" :placeholder="$t('profile.textPlaceholder')" class="textarea" rows="12"></textarea>
            <p class="hint">{{ $t('profile.textHint') }}</p>
          </div>
          <button class="submit-btn" @click="createProfile" :disabled="creating">
            <span v-if="creating" class="spinner"></span>
            {{ creating ? $t('profile.creating') : $t('profile.submitBtn') }}
          </button>
          <button class="cancel-btn" @click="showCreate = false">{{ $t('common.cancel') }}</button>
        </div>
      </section>

      <section class="profiles-section">
        <div class="section-header">
          <span class="status-dot">■</span> {{ $t('home.systemStatus') }}
        </div>
        <h2>{{ $t('home.recentProfiles') }}</h2>
        <div v-if="profiles.length === 0" class="empty-state">{{ $t('home.noProfiles') }}</div>
        <div v-else class="profile-grid">
          <div v-for="p in profiles" :key="p.profile_id" class="profile-card" @click="router.push(`/profile/${p.profile_id}`)">
            <div class="card-header">
              <span class="card-name">{{ p.name }}</span>
              <span class="card-status" :class="p.status">{{ p.status }}</span>
            </div>
            <div class="card-meta">
              <span>{{ p.basic_info?.age ? p.basic_info.age + '岁' : '' }}</span>
              <span v-if="p.basic_info?.location?.current">{{ p.basic_info.location.current }}</span>
            </div>
            <div class="card-footer">
              <span>{{ p.decision_ids?.length || 0 }} 个决策点</span>
              <span class="arrow">→</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'
import { profileApi } from '../api/profile'

const router = useRouter()
const profiles = ref([])
const showCreate = ref(false)
const creating = ref(false)
const profileName = ref('')
const profileText = ref('')

onMounted(async () => {
  try {
    const res = await profileApi.list()
    profiles.value = res.data || []
  } catch (e) {
    console.error('加载画像列表失败:', e)
  }
})

async function createProfile() {
  if (!profileText.value.trim()) return
  creating.value = true
  try {
    const res = await profileApi.create(profileText.value, profileName.value || 'Unnamed')
    const taskId = res.data.task_id
    const poll = setInterval(async () => {
      const statusRes = await profileApi.getTaskStatus(taskId)
      if (statusRes.data.status === 'completed') {
        clearInterval(poll)
        router.push(`/profile/${statusRes.data.result.profile_id}`)
      } else if (statusRes.data.status === 'failed') {
        clearInterval(poll)
        creating.value = false
        alert('创建失败: ' + (statusRes.data.error || '未知错误'))
      }
    }, 2000)
  } catch (e) {
    creating.value = false
    alert('创建失败: ' + e.message)
  }
}
</script>

<style scoped>
.home-container { min-height: 100vh; max-width: 1200px; margin: 0 auto; padding: 0 32px; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; border-bottom: 1px solid #eee; }
.nav-brand { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: 2px; }
.nav-links { display: flex; align-items: center; gap: 16px; }
.hero-section { display: flex; justify-content: space-between; align-items: center; padding: 80px 0 60px; }
.hero-left { flex: 1; }
.tag-row { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.orange-tag { background: #000; color: #fff; padding: 4px 12px; font-size: 12px; font-family: 'JetBrains Mono', monospace; }
.version-text { font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }
.main-title { font-size: 64px; font-weight: 300; line-height: 1.15; font-family: 'Space Grotesk', 'Noto Sans SC', sans-serif; }
.gradient-text { font-weight: 700; }
.hero-desc { margin-top: 24px; font-size: 16px; line-height: 1.6; color: #555; max-width: 560px; }
.slogan-text { margin-top: 12px; font-size: 14px; color: #999; font-family: 'JetBrains Mono', monospace; }
.blinking-cursor { animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }
.create-btn { padding: 14px 32px; background: #000; color: #fff; border: none; font-size: 15px; font-family: 'Space Grotesk', sans-serif; letter-spacing: 1px; transition: all 0.2s; }
.create-btn:hover { background: #333; }

.create-section { margin-bottom: 60px; }
.create-card { border: 1px solid #000; padding: 40px; max-width: 720px; }
.create-card h2 { font-family: 'Space Grotesk', sans-serif; font-size: 24px; margin-bottom: 24px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 12px; color: #999; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }
.input, .textarea { width: 100%; border: 1px solid #ddd; padding: 12px 16px; font-size: 14px; font-family: 'JetBrains Mono', 'Noto Sans SC', monospace; transition: border-color 0.2s; resize: vertical; }
.input:focus, .textarea:focus { outline: none; border-color: #000; }
.hint { font-size: 11px; color: #999; margin-top: 8px; }
.submit-btn { padding: 12px 28px; background: #000; color: #fff; border: none; font-size: 14px; font-family: 'Space Grotesk', sans-serif; margin-right: 12px; display: inline-flex; align-items: center; gap: 8px; }
.submit-btn:disabled { background: #999; cursor: not-allowed; }
.cancel-btn { padding: 12px 28px; background: none; border: 1px solid #000; font-size: 14px; font-family: 'Space Grotesk', sans-serif; }
.spinner { width: 14px; height: 14px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.profiles-section { padding: 40px 0 80px; border-top: 1px solid #eee; }
.section-header { font-size: 13px; color: #999; font-family: 'JetBrains Mono', monospace; margin-bottom: 12px; }
.status-dot { color: #000; }
.profiles-section h2 { font-family: 'Space Grotesk', sans-serif; font-size: 20px; margin-bottom: 24px; }
.empty-state { color: #999; font-size: 14px; padding: 40px 0; }
.profile-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.profile-card { border: 1px solid #eee; padding: 20px; cursor: pointer; transition: all 0.2s; }
.profile-card:hover { border-color: #000; transform: translateY(-2px); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-name { font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 16px; }
.card-status { font-size: 10px; padding: 2px 6px; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
.card-status.ready { background: #000; color: #fff; }
.card-status.failed { background: #ff0000; color: #fff; }
.card-status.created, .card-status.graph_built { background: #eee; color: #999; }
.card-meta { display: flex; gap: 12px; font-size: 13px; color: #666; margin-bottom: 12px; }
.card-footer { display: flex; justify-content: space-between; font-size: 12px; color: #999; font-family: 'JetBrains Mono', monospace; }
</style>
