<template>
  <router-view />
  <ToastMessage
    :message="toastMessage"
    :type="toastType"
    :duration="3000"
  />
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

  onToast(showToast)
})
</script>
