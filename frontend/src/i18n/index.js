import { createI18n } from 'vue-i18n'

const localeFiles = import.meta.glob('../../../locales/!(languages).json', { eager: true })
const langFile = import.meta.glob('../../../locales/languages.json', { eager: true })
const languages = langFile['../../../locales/languages.json']?.default || {}

const messages = {}
for (const path in localeFiles) {
  const key = path.match(/\/([^/]+)\.json$/)[1]
  if (languages[key]) {
    messages[key] = localeFiles[path].default
  }
}

const savedLocale = localStorage.getItem('locale') || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'zh',
  messages
})

export default i18n
