import { createApp } from 'vue'
import { createPinia } from 'pinia'
import AppMobile from './AppMobile.vue'
import '@/index.css'
import router from './router'

const app = createApp(AppMobile)
app.use(createPinia())
app.use(router)
app.mount('#app')
