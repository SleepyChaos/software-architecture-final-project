<!--
  登录页面组件
  功能：提供读者证登录和注册新账号两种方式，支持用户身份验证
  特点：
  - 双重模式：读者证登录和新用户注册
  - 动态切换登录/注册，提供流畅的用户体验
  - 表单验证和错误提示
  - 响应式设计，适配不同屏幕尺寸
-->
<template>
  <!-- 登录页面容器：全屏布局，居中显示 -->
  <div class="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-6 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute -top-40 -right-40 w-96 h-96 bg-blue-100 rounded-full opacity-50 blur-3xl"></div>
    <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-100 rounded-full opacity-50 blur-3xl"></div>

    <!-- 返回按钮 -->
    <router-link to="/" class="absolute top-8 left-8 flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors z-10">
      <ArrowLeft class="w-6 h-6" />
      <span class="font-medium">返回首页</span>
    </router-link>

    <!-- 登录主容器：左右分栏布局 -->
    <div class="w-full max-w-4xl bg-white rounded-3xl shadow-2xl overflow-hidden flex">
      <!-- 左侧：引导区 -->
      <div class="w-1/3 bg-gradient-to-br from-blue-600 to-indigo-700 p-10 text-white flex flex-col justify-between relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-full bg-[url('/pattern.svg')] opacity-10"></div>
        
        <div class="relative z-10">
          <div class="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mb-6 backdrop-blur-sm">
            <BookOpen class="w-8 h-8 text-white" />
          </div>
          <h1 class="text-3xl font-bold mb-2">身份认证</h1>
          <p class="text-blue-100">Authentication</p>
        </div>

        <div class="relative z-10">
          <p class="text-sm text-blue-200 leading-relaxed mb-4">
            已有账号请使用读者证登录，新用户可点击注册创建账号。
          </p>
          <div class="text-xs text-blue-300">系统版本 v2.0.1</div>
        </div>
      </div>

      <!-- 右侧：操作区 -->
      <div class="flex-1 p-12">
        <!-- 登录方式切换 -->
        <div class="flex gap-4 mb-10">
          <!-- 读者证登录按钮 -->
          <button 
            class="flex-1 py-4 rounded-xl border-2 font-bold transition-all flex items-center justify-center gap-2"
            :class="loginMethod === 'card' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-slate-100 text-slate-400 hover:border-blue-200 hover:bg-slate-50'"
            @click="setMethod('card')"
          >
            <CreditCard class="w-5 h-5" />
            读者证登录
          </button>
          <!-- 注册账号按钮 -->
          <button 
            class="flex-1 py-4 rounded-xl border-2 font-bold transition-all flex items-center justify-center gap-2"
            :class="loginMethod === 'register' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-slate-100 text-slate-400 hover:border-blue-200 hover:bg-slate-50'"
            @click="setMethod('register')"
          >
            <UserPlus class="w-5 h-5" />
            注册账号
          </button>
        </div>

        <!-- 读者证登录表单 -->
        <div v-if="loginMethod === 'card'" class="animate-fade-in">
          <div class="space-y-6">
            <!-- 读者证号输入框 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">读者证号 / 学号</label>
              <div class="relative">
                <input 
                  v-model="studentId"
                  type="text" 
                  class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-lg font-medium"
                  placeholder="请刷卡或输入证号"
                  @keyup.enter="handleLogin"
                >
                <CreditCard class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 w-6 h-6" />
              </div>
              <p class="text-xs text-blue-500 mt-2 flex items-center gap-1">
                <Info class="w-4 h-4" />
                可在自助机刷卡区直接刷读者证登录
              </p>
            </div>

            <!-- 密码输入框 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">密码</label>
              <div class="relative">
                <input 
                  v-model="password"
                  type="password" 
                  class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-lg font-medium"
                  placeholder="请输入密码"
                  @keyup.enter="handleLogin"
                >
                <Lock class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 w-6 h-6" />
              </div>
            </div>

            <!-- 错误提示区域：显示登录错误信息 -->
            <div v-if="authStore.error" class="text-red-500 text-sm bg-red-50 px-4 py-2 rounded-lg">
              {{ authStore.error }}
            </div>

            <!-- 登录按钮：提交读者证登录表单 -->
            <button 
              class="w-full py-4 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-blue-500/30 disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              :disabled="authStore.isLoading || !studentId"
              @click="handleLogin"
            >
              <!-- 加载动画：登录过程中显示旋转图标 -->
              <Loader2 v-if="authStore.isLoading" class="w-5 h-5 animate-spin" />
              <!-- 按钮文字：根据加载状态显示不同文本 -->
              {{ authStore.isLoading ? '正在验证...' : '确认登录' }}
            </button>
          </div>
        </div>

        <!-- 注册区域：新用户注册表单 -->
        <div v-else class="animate-fade-in">
          <div class="space-y-5">
            <!-- 读者证号输入框 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">读者证号 / 学号</label>
              <div class="relative">
                <input 
                  v-model="registerId"
                  type="text" 
                  class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-lg font-medium"
                  placeholder="请输入您的读者证号"
                >
                <CreditCard class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 w-6 h-6" />
              </div>
            </div>

            <!-- 密码输入框 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">设置密码</label>
              <div class="relative">
                <input 
                  v-model="registerPassword"
                  :type="showRegisterPassword ? 'text' : 'password'"
                  class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-lg font-medium pr-14"
                  placeholder="请设置密码（至少6位）"
                >
                <button
                  type="button"
                  @click="showRegisterPassword = !showRegisterPassword"
                  class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <EyeOff v-if="showRegisterPassword" class="w-5 h-5" />
                  <Eye v-else class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- 确认密码输入框 -->
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-2">确认密码</label>
              <div class="relative">
                <input 
                  v-model="registerConfirmPassword"
                  :type="showRegisterPassword ? 'text' : 'password'"
                  class="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-lg font-medium"
                  placeholder="请再次输入密码"
                  @keyup.enter="handleRegister"
                >
                <Lock class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-400 w-6 h-6" />
              </div>
              <!-- 密码不一致提示 -->
              <p
                v-if="registerConfirmPassword && registerPassword !== registerConfirmPassword"
                class="text-xs text-red-500 mt-2"
              >
                两次输入的密码不一致
              </p>
            </div>

            <!-- 错误提示区域 -->
            <div v-if="authStore.error" class="text-red-500 text-sm bg-red-50 px-4 py-2 rounded-lg">
              {{ authStore.error }}
            </div>

            <!-- 注册成功提示 -->
            <div v-if="registerSuccess" class="text-green-600 text-sm bg-green-50 px-4 py-3 rounded-lg flex items-center gap-2">
              <CheckCircle2 class="w-5 h-5" />
              注册成功！请切换到登录页进行登录
            </div>

            <!-- 注册按钮 -->
            <button 
              class="w-full py-4 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-blue-500/30 disabled:bg-slate-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              :disabled="authStore.isLoading || !isRegisterValid || registerSuccess"
              @click="handleRegister"
            >
              <Loader2 v-if="authStore.isLoading" class="w-5 h-5 animate-spin" />
              {{ authStore.isLoading ? '注册中...' : '立即注册' }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, Loader2, CreditCard, UserPlus, Lock, ArrowLeft, Info, Eye, EyeOff, CheckCircle2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

// 路由和状态管理初始化
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据定义
const loginMethod = ref<'card' | 'register'>('card') // 模式：读者证登录或注册
const studentId = ref('') // 读者证号/学号（登录用）
const password = ref('') // 密码（登录用）

// 注册表单数据
const registerId = ref('') // 读者证号（注册用）
const registerPassword = ref('') // 密码（注册用）
const registerConfirmPassword = ref('') // 确认密码（注册用）
const showRegisterPassword = ref(false) // 注册密码可见性
const registerSuccess = ref(false) // 注册成功标记

// 注册表单有效性
const isRegisterValid = computed(() => {
  return (
    registerId.value.trim() !== '' &&
    registerPassword.value.length >= 6 &&
    registerPassword.value === registerConfirmPassword.value
  )
})

/**
 * 切换登录/注册模式
 * @param m 模式类型：'card' 或 'register'
 */
function setMethod(m: 'card' | 'register') {
  loginMethod.value = m
  // 切换时清除错误信息
  authStore.error = null
}

/**
 * 处理读者证登录
 * 验证输入并调用认证store的登录方法
 */
async function handleLogin() {
  // 验证读者证号是否为空
  if (!studentId.value) return
  
  // 验证密码是否为空
  if (!password.value) {
    authStore.error = '请输入密码'
    return
  }
  
  // 调用认证store的登录方法
  const success = await authStore.login(studentId.value, password.value)
  
  // 登录成功后跳转到首页
  if (success) router.push('/')
}

/**
 * 处理新用户注册
 * 校验表单后调用注册接口，成功后提示用户切换登录
 */
async function handleRegister() {
  if (!isRegisterValid.value) return

  const success = await authStore.register(
    registerId.value.trim(),
    registerPassword.value,
  )

  if (success) {
    registerSuccess.value = true
    // 2秒后自动切回登录页
    setTimeout(() => {
      registerSuccess.value = false
      loginMethod.value = 'card'
      // 把注册的读者证号填入登录表单，方便用户直接登录
      studentId.value = registerId.value
    }, 2000)
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
