<!--
  登录页面组件
  功能：提供读者证登录和人脸识别登录两种方式，支持用户身份验证
  特点：
  - 双重登录方式：读者证登录和人脸识别登录
  - 动态切换登录方式，提供流畅的用户体验
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
            请选择您喜欢的登录方式，支持读者证刷卡登录或人脸识别快速登录。
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
          <!-- 人脸识别登录按钮 -->
          <button 
            class="flex-1 py-4 rounded-xl border-2 font-bold transition-all flex items-center justify-center gap-2"
            :class="loginMethod === 'face' ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-slate-100 text-slate-400 hover:border-blue-200 hover:bg-slate-50'"
            @click="setMethod('face')"
          >
            <ScanFace class="w-5 h-5" />
            人脸识别
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

        <!-- 人脸识别区域：人脸识别登录界面 -->
        <div v-else class="animate-fade-in text-center">
          <!-- 人脸识别视频区域：摄像头视频显示和扫描动画 -->
          <div class="relative w-64 h-64 mx-auto mb-8 rounded-full overflow-hidden border-4 border-blue-100 bg-slate-900">
            <!-- 视频元素：显示摄像头实时画面，水平翻转 -->
            <video ref="videoRef" class="w-full h-full object-cover transform scale-x-[-1]" autoplay muted playsinline></video>
            
            <!-- 扫描动画覆盖层：人脸识别时的扫描线动画 -->
            <div v-if="isFaceRunning" class="absolute inset-0 z-10">
              <!-- 扫描线：蓝色扫描线，带有发光效果 -->
              <div class="w-full h-1 bg-blue-400/80 absolute top-0 shadow-[0_0_15px_rgba(59,130,246,0.5)] animate-face-scan"></div>
              <!-- 扫描边框：蓝色半透明边框 -->
              <div class="absolute inset-0 border-4 border-blue-500/30 rounded-full"></div>
              <!-- 扫描框：白色虚线框 -->
              <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 border-2 border-dashed border-white/30 rounded-2xl"></div>
            </div>

            <!-- 未运行状态：显示人脸识别图标 -->
            <div v-if="!isFaceRunning" class="absolute inset-0 flex items-center justify-center bg-slate-900/50">
              <ScanFace class="w-20 h-20 text-white/50" />
            </div>
          </div>

          <!-- 人脸识别状态提示：根据运行状态显示不同提示信息 -->
          <p class="text-slate-500 mb-8" v-if="isFaceRunning">
            正在识别您的身份... <br>
            <span class="text-xs text-slate-400">请保持正对摄像头</span>
          </p>
          <p class="text-slate-500 mb-8" v-else>
            点击下方按钮开始人脸识别
          </p>

          <!-- 人脸识别按钮：启动或停止人脸识别 -->
          <button 
            class="w-full py-4 rounded-xl font-bold text-lg transition-all shadow-lg flex items-center justify-center gap-2"
            :class="isFaceRunning ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-blue-500/30'"
            :disabled="isFaceRunning"
            @click="startFaceLogin"
          >
            <!-- 图标：根据状态显示不同图标 -->
            <ScanFace v-if="!isFaceRunning" class="w-6 h-6" />
            <Loader2 v-else class="w-6 h-6 animate-spin" />
            <!-- 按钮文字：根据状态显示不同文本 -->
            {{ isFaceRunning ? '识别中...' : '开始人脸识别' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, Loader2, CreditCard, ScanFace, Lock, ArrowLeft, Info } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

// 路由和状态管理初始化
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据定义
const loginMethod = ref<'card' | 'face'>('card') // 登录方式：读者证或人脸识别
const studentId = ref('') // 读者证号/学号
const password = ref('') // 密码
const isFaceRunning = ref(false) // 人脸识别运行状态
const videoRef = ref<HTMLVideoElement | null>(null) // 视频元素引用
let stream: MediaStream | null = null // 媒体流对象

/**
 * 设置登录方式
 * @param m 登录方式类型：'card' 或 'face'
 */
function setMethod(m: 'card' | 'face') {
  loginMethod.value = m
  // 如果切换到读者证登录，停止摄像头
  if (m === 'card') {
    stopCamera()
  }
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
 * 启动人脸识别登录流程
 * 获取摄像头权限，显示视频流，模拟识别过程
 */
async function startFaceLogin() {
  // 防止重复启动
  if (isFaceRunning.value) return
  
  try {
    // 设置运行状态为true
    isFaceRunning.value = true
    
    // 获取摄像头权限并设置视频流
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 640, facingMode: 'user' } 
    })
    
    // 将视频流绑定到video元素
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
    
    // 模拟识别延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟成功登录（实际应用中应调用真实的人脸识别API）
    const ok = await authStore.login('face-user', 'face')
    if (ok) {
      stopCamera()
      router.push('/')
    }
  } catch (e) {
    // 处理摄像头访问失败或识别失败的情况
    alert('无法访问摄像头或识别失败')
  }
}

/**
 * 停止摄像头
 * 释放媒体流资源
 */
function stopCamera() {
  // 停止人脸识别状态
  isFaceRunning.value = false
  
  // 释放媒体流
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  
  // 清空视频源
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 可以在这里添加初始化逻辑
})

// 组件卸载时的清理
onUnmounted(() => {
  // 确保摄像头被正确释放
  stopCamera()
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scan {
  0% { top: 0; opacity: 0.8; }
  50% { top: 100%; opacity: 0.4; }
  100% { top: 0; opacity: 0.8; }
}
.animate-face-scan {
  animation: scan 2s ease-in-out infinite;
}
</style>
