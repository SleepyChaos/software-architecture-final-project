import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 系统状态组合式函数：在线状态与当前时间
 */
export function useSystemStatus() {
  const online = ref<boolean>(navigator.onLine)
  const now = ref<string>(new Date().toLocaleString('zh-CN'))

  function updateTime() {
    now.value = new Date().toLocaleString('zh-CN')
  }

  function handleOnline() { online.value = true }
  function handleOffline() { online.value = false }

  onMounted(() => {
    const timer = setInterval(updateTime, 1000)
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    ;(window as any).__status_timer = timer
  })

  onUnmounted(() => {
    if ((window as any).__status_timer) clearInterval((window as any).__status_timer)
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  })

  return { online, now }
}

