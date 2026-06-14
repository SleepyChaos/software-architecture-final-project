<template>
  <!-- 主应用容器：设置最小高度和背景色，确保页面占满视口 -->
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 路由视图：根据当前路由动态渲染对应的页面组件 -->
    <router-view />

    <!-- 全局 Toast 提示：用于 401 未授权等全局消息 -->
    <ToastMessage
      :message="toastMessage"
      :type="toastType"
      :duration="3000"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ToastMessage from '@/components/ToastMessage.vue'
import { onToast } from '@/utils/toast'
import { useAuthStore } from '@/stores/auth'

const toastMessage = ref('')
const toastType = ref<'error' | 'success' | 'warning' | 'info'>('error')

function showToast(msg: string, type: 'error' | 'success' | 'warning' | 'info' = 'error') {
  toastMessage.value = ''
  toastType.value = type
  setTimeout(() => { toastMessage.value = msg }, 0)
}

onMounted(() => {
  const authStore = useAuthStore()
  authStore.initializeUser()

  // 注册全局 Toast 处理器，供路由守卫和 HTTP 工具调用
  onToast(showToast)
})
</script>

<style scoped>
/* 应用根元素样式：设置现代系统字体族 */
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style>