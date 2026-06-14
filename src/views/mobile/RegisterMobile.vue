<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <router-link to="/mobile/profile" class="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors">
          <ArrowLeft class="w-5 h-5" />
          <span class="text-sm font-medium">返回</span>
        </router-link>
        <h1 class="text-lg font-semibold text-gray-900">注册账号</h1>
        <div class="w-16"></div>
      </div>
    </div>

    <!-- 注册表单区域 -->
    <div class="max-w-md mx-auto px-4 py-10">
      <div class="bg-white rounded-xl shadow-sm p-8">
        <!-- 注册头部：图标和标题 -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900">读者注册</h2>
          <p class="text-gray-500 mt-2">创建您的图书馆读者账号</p>
        </div>

        <!-- 注册表单 -->
        <form @submit.prevent="handleRegister" class="space-y-5">
          <!-- 读者证号输入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">读者证号</label>
            <input
              v-model="registerForm.readerId"
              type="text"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="请输入读者证号（如：20240001）"
              required
            >
            <p class="text-xs text-gray-400 mt-1">读者证号将作为您的登录凭证</p>
          </div>

          <!-- 密码输入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">设置密码</label>
            <div class="relative">
              <input
                v-model="registerForm.password"
                :type="showPassword ? 'text' : 'password'"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all pr-12"
                placeholder="请设置密码（至少6位）"
                required
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <EyeOff v-if="showPassword" class="w-5 h-5" />
                <Eye v-else class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- 确认密码输入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">确认密码</label>
            <input
              v-model="registerForm.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="请再次输入密码"
              required
            >
            <!-- 密码不一致提示 -->
            <p
              v-if="registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword"
              class="text-xs text-red-500 mt-1"
            >
              两次输入的密码不一致
            </p>
          </div>

          <!-- 错误提示 -->
          <div v-if="auth.error" class="text-red-500 text-sm text-center bg-red-50 py-2 rounded-lg">
            {{ auth.error }}
          </div>

          <!-- 成功提示 -->
          <div v-if="registerSuccess" class="text-green-600 text-sm text-center bg-green-50 py-3 rounded-lg">
            <CheckCircle2 class="w-5 h-5 inline-block mr-1 -mt-0.5" />
            注册成功！即将跳转到登录页...
          </div>

          <!-- 注册按钮 -->
          <button
            type="submit"
            :disabled="auth.isLoading || !isFormValid || registerSuccess"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Loader2 v-if="auth.isLoading" class="w-5 h-5 animate-spin mr-2" />
            {{ auth.isLoading ? '注册中...' : '立即注册' }}
          </button>
        </form>

        <!-- 底部链接 -->
        <div class="mt-6 text-center text-sm text-gray-500">
          已有账号？
          <router-link to="/mobile/profile" class="text-blue-600 font-medium hover:underline">
            立即登录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ArrowLeft, UserPlus, Loader2, Eye, EyeOff, CheckCircle2 } from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()

// 表单数据
const registerForm = ref({
  readerId: '',
  password: '',
  confirmPassword: '',
})

// 密码可见性
const showPassword = ref(false)

// 注册成功标记
const registerSuccess = ref(false)

// 表单有效性校验
const isFormValid = computed(() => {
  return (
    registerForm.value.readerId.trim() !== '' &&
    registerForm.value.password.length >= 6 &&
    registerForm.value.password === registerForm.value.confirmPassword
  )
})

/**
 * 处理注册提交
 * 校验表单后调用注册接口，成功后跳转登录页
 */
async function handleRegister() {
  if (!isFormValid.value) return

  const success = await auth.register(
    registerForm.value.readerId.trim(),
    registerForm.value.password,
  )

  if (success) {
    registerSuccess.value = true
    // 延迟跳转到个人页面（登录状态）
    setTimeout(() => {
      router.push('/mobile/profile')
    }, 1200)
  }
}
</script>
