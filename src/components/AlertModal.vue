<template>
  <Transition name="fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 transform transition-all animate-scale-in">
        <div class="flex flex-col items-center text-center">
          <!-- 图标区域 -->
          <div 
            class="w-16 h-16 rounded-full flex items-center justify-center mb-4"
            :class="typeStyles[type].bg"
          >
            <component :is="typeStyles[type].icon" class="w-8 h-8" :class="typeStyles[type].text" />
          </div>

          <!-- 标题和内容 -->
          <h3 class="text-xl font-bold text-slate-800 mb-2">{{ title }}</h3>
          <p class="text-slate-500 mb-8 leading-relaxed">{{ message }}</p>

          <!-- 按钮 -->
          <button 
            @click="$emit('close')"
            class="w-full py-3 px-6 rounded-xl font-bold text-white transition-colors shadow-lg hover:shadow-xl"
            :class="typeStyles[type].btn"
          >
            我知道了
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { AlertTriangle, XCircle, Info, AlertCircle } from 'lucide-vue-next'

const props = defineProps<{
  show: boolean
  title: string
  message: string
  type: 'error' | 'warning' | 'info'
}>()

defineEmits(['close'])

const typeStyles = {
  error: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    btn: 'bg-red-600 hover:bg-red-700 shadow-red-500/30',
    icon: XCircle
  },
  warning: {
    bg: 'bg-amber-100',
    text: 'text-amber-600',
    btn: 'bg-amber-500 hover:bg-amber-600 shadow-amber-500/30',
    icon: AlertTriangle
  },
  info: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    btn: 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/30',
    icon: Info
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-scale-in {
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
