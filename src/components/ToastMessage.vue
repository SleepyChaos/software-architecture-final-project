<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="visible"
        class="fixed top-6 left-1/2 -translate-x-1/2 z-[9999] flex items-center gap-3 px-5 py-3 rounded-xl shadow-2xl text-sm font-medium max-w-sm"
        :class="styles[computedType].bg"
      >
        <component :is="styles[computedType].icon" class="w-5 h-5 shrink-0" />
        <span>{{ message }}</span>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ShieldAlert, CheckCircle2, AlertTriangle, Info } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  message: string
  type?: 'error' | 'success' | 'warning' | 'info'
  duration?: number
}>(), {
  type: 'error',
  duration: 3000,
})

const visible = ref(false)

const styles = {
  error:   { bg: 'bg-red-600 text-white',    icon: ShieldAlert },
  success: { bg: 'bg-green-600 text-white',  icon: CheckCircle2 },
  warning: { bg: 'bg-amber-500 text-white',  icon: AlertTriangle },
  info:    { bg: 'bg-blue-600 text-white',   icon: Info },
}

const computedType = computed(() => props.type)

let timer: ReturnType<typeof setTimeout> | null = null

function show() {
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    visible.value = false
  }, props.duration)
}

watch(() => props.message, (val) => {
  if (val) show()
}, { immediate: true })

defineExpose({ show })
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-leave-active {
  transition: all 0.2s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, -20px);
}
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
