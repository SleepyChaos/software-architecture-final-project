<!--
  图书借阅页面组件
  功能：处理图书借阅流程，包括图书识别、确认借阅和成功提示
  特点：
  - 多种识别方式：支持RFID感应识别图书
  - 批量借阅：可同时借阅多本图书
  - 借阅确认：显示借阅图书列表和应还日期
  - 用户友好：提供清晰的借阅流程指导和状态反馈
  - 错误处理：处理借阅失败和异常情况
-->
<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- 顶部状态栏：显示页面标题、倒计时和退出按钮 -->
    <div class="bg-blue-600 text-white shadow-md z-10">
      <div class="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
        <!-- 左侧：页面标题和图标 -->
        <div class="flex items-center gap-4">
          <div class="p-2 bg-white/10 rounded-xl">
            <BookUp class="w-8 h-8" />
          </div>
          <div class="text-3xl font-bold tracking-wide">借阅图书</div>
        </div>
        <!-- 右侧：倒计时和退出按钮 -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full">
            <Clock class="w-5 h-5" />
            <span class="text-xl font-mono">{{ countdown }}s</span>
          </div>
          <button 
            class="px-6 py-2 bg-white text-blue-600 rounded-full font-bold hover:bg-blue-50 transition-colors shadow-sm"
            @click="exit"
          >
            退出
          </button>
        </div>
      </div>
    </div>

    <!-- 成功结果页：显示借阅成功信息和操作按钮 -->
    <div v-if="step === 'success'" class="flex-1 flex flex-col items-center justify-center p-8 animate-fade-in">
      <div class="bg-white rounded-3xl shadow-xl p-12 max-w-2xl w-full text-center">
        <!-- 成功图标：绿色圆形背景中的勾选图标 -->
        <div class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce-slow">
          <Check class="w-12 h-12 text-green-600" />
        </div>
        <!-- 成功消息：显示借阅成功标题和数量信息 -->
        <h2 class="text-4xl font-bold text-slate-800 mb-4">借阅成功！</h2>
        <p class="text-xl text-slate-500 mb-8">成功借阅 {{ successCount }} 本图书，请记得取走您的书籍</p>
        
        <!-- 借阅详情卡片：显示应还日期和提示信息 -->
        <div class="bg-slate-50 rounded-2xl p-6 mb-8 text-left">
          <div class="flex justify-between items-center mb-2">
            <span class="text-slate-500">应还日期</span>
            <span class="text-xl font-bold text-blue-600">{{ dueDate }}</span>
          </div>
          <div class="text-sm text-slate-400">请按时归还，祝您阅读愉快</div>
        </div>

        <!-- 操作按钮组：返回首页和继续借阅按钮 -->
        <div class="flex gap-4">
          <button 
            class="flex-1 py-4 bg-gray-100 text-slate-600 rounded-xl font-bold text-lg hover:bg-gray-200 transition-colors"
            @click="exit"
          >
            返回首页
          </button>
          <button 
            class="flex-1 py-4 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 transition-colors shadow-lg hover:shadow-blue-500/30"
            @click="reset"
          >
            继续借阅
          </button>
        </div>
      </div>
    </div>

    <!-- 借阅主流程：包含图书识别列表和操作区域 -->
    <div v-else class="flex-1 max-w-7xl mx-auto w-full p-8 flex gap-8">
      <!-- 左侧：图书识别列表 -->
      <div class="flex-[2] bg-white rounded-3xl shadow-lg flex flex-col overflow-hidden">
        <!-- 列表标题栏：显示列表标题和已识别数量 -->
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h3 class="text-xl font-bold text-slate-700 flex items-center gap-2">
            <Library class="w-6 h-6 text-blue-500" />
            识别列表
          </h3>
          <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-bold">
            已识别 {{ detectedBooks.length }} 本
          </span>
        </div>
        
        <!-- 图书列表内容区：显示空状态或图书列表 -->
        <div class="flex-1 p-6 overflow-y-auto min-h-[500px]">
          <!-- 空状态：提示用户放置图书 -->
          <div v-if="detectedBooks.length === 0" class="h-full flex flex-col items-center justify-center text-slate-400">
            <div class="w-48 h-48 bg-slate-50 rounded-full flex items-center justify-center mb-6">
              <ScanLine class="w-24 h-24 text-slate-300" />
            </div>
            <p class="text-xl">请将图书放置在感应区</p>
            <p class="mt-2 text-sm">系统将自动识别图书信息</p>
          </div>
          
          <!-- 识别到的图书列表：显示每本图书的封面、信息和状态 -->
          <ul v-else class="grid grid-cols-1 gap-4">
            <li v-for="b in detectedBooks" :key="b.id" class="flex gap-6 p-4 rounded-2xl border border-slate-100 bg-white hover:border-blue-200 hover:shadow-md transition-all">
              <!-- 图书封面：显示图书封面图片 -->
              <img :src="b.coverImageUrl" class="w-24 h-32 object-cover rounded-lg shadow-sm" />
              <!-- 图书信息：显示图书标题、作者和ISBN -->
              <div class="flex-1 flex flex-col justify-center">
                <h4 class="text-xl font-bold text-slate-800 mb-2">{{ b.title }}</h4>
                <p class="text-slate-500 mb-1">{{ b.author }}</p>
                <p class="text-slate-400 text-sm">ISBN: {{ b.isbn }}</p>
              </div>
              <!-- 图书状态：显示可借阅状态标签 -->
              <div class="flex flex-col justify-center items-end px-4">
                <div class="text-sm text-slate-500 mb-1">状态</div>
                <div class="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-bold">可借阅</div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 右侧：操作区 -->
      <div class="flex-1 flex flex-col gap-6">
        <!-- 提示卡片：显示借阅操作提示 -->
        <div class="bg-blue-50 rounded-3xl p-6 border border-blue-100">
          <h4 class="font-bold text-blue-800 mb-2 flex items-center gap-2">
            <Info class="w-5 h-5" />
            温馨提示
          </h4>
          <p class="text-blue-600 text-sm leading-relaxed">
            请确保图书放置平整，一次最多可放置5本。识别完成后请点击"确认借阅"。
          </p>
        </div>

        <!-- 模拟感应按钮：触发图书识别过程 -->
        <button 
          class="w-full py-6 rounded-2xl font-bold text-xl transition-all shadow-lg flex flex-col items-center justify-center gap-2 relative overflow-hidden group"
          :class="isDetecting ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-white text-blue-600 hover:bg-blue-50 border-2 border-blue-100'"
          @click="startDetect"
          :disabled="isDetecting"
        >
          <div v-if="isDetecting" class="absolute inset-0 bg-slate-100/50 flex items-center justify-center z-10">
            <div class="w-full h-1 bg-blue-200 absolute top-0 animate-scan"></div>
          </div>
          <Scan class="w-8 h-8" :class="{'animate-pulse': isDetecting}" />
          <span>{{ isDetecting ? '正在识别中...' : '模拟感应图书' }}</span>
        </button>

        <div class="mt-auto flex flex-col gap-4">
          <!-- 合计数量：显示已识别图书总数 -->
          <div class="flex justify-between items-end px-2">
            <span class="text-slate-500">合计数量</span>
            <span class="text-3xl font-bold text-slate-800">{{ detectedBooks.length }} <span class="text-base font-normal text-slate-400">本</span></span>
          </div>
          
          <!-- 确认借阅按钮：提交借阅请求 -->
          <button 
            class="w-full py-5 bg-blue-600 text-white rounded-2xl font-bold text-xl hover:bg-blue-700 transition-all shadow-xl hover:shadow-blue-500/30 disabled:bg-slate-300 disabled:shadow-none disabled:cursor-not-allowed flex items-center justify-center gap-2"
            :disabled="detectedBooks.length === 0 || isSubmitting"
            @click="confirmBorrow"
          >
            <div v-if="isSubmitting" class="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
            <span>{{ isSubmitting ? '处理中...' : '确认借阅' }}</span>
          </button>
          
          <!-- 重新识别按钮：重置识别状态 -->
          <button 
            class="w-full py-4 bg-white text-slate-600 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-colors border border-slate-200"
            @click="reset"
            :disabled="isSubmitting"
          >
            重新识别
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 异常提示弹窗 -->
  <AlertModal
    :show="showAlert"
    :title="alertTitle"
    :message="alertMessage"
    :type="alertType"
    @close="showAlert = false"
  />

  <!-- 开发者调试工具：模拟异常情况 -->
  <div class="fixed bottom-4 right-4 z-40">
    <button 
      @click="showDebug = !showDebug"
      class="bg-gray-800 text-white px-4 py-2 rounded-full shadow-lg text-sm font-mono opacity-50 hover:opacity-100 transition-opacity"
    >
      {{ showDebug ? '关闭调试' : '模拟异常' }}
    </button>
    
    <div v-if="showDebug" class="absolute bottom-12 right-0 bg-white p-4 rounded-xl shadow-2xl w-64 border border-gray-200 grid gap-2 max-h-[80vh] overflow-y-auto">
      <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">借书流程异常模拟</h3>
      <button
        v-for="(err, index) in exceptions"
        :key="index"
        @click="triggerException(err)"
        class="text-left px-3 py-2 rounded-lg text-sm hover:bg-red-50 text-gray-600 hover:text-red-600 transition-colors border border-transparent hover:border-red-100"
      >
        {{ err.label }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { BookUp, Clock, ScanLine, Library, Info, Scan, Check } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useBooksStore, type Book } from '@/stores/books'
import { useLoansStore } from '@/stores/loans'
import AlertModal from '@/components/AlertModal.vue'

// 路由和状态管理
const router = useRouter()
const auth = useAuthStore()
const booksStore = useBooksStore()
const loansStore = useLoansStore()

// 倒计时状态：用于自动退出
const countdown = ref(60)
let timer: any = null

// 异常模拟状态
const showDebug = ref(false)
const showAlert = ref(false)
const alertTitle = ref('')
const alertMessage = ref('')
const alertType = ref<'error' | 'warning' | 'info'>('info')

const exceptions = [
  { label: '系统超时', title: '操作超时', message: '目前系统繁忙请稍后再试', type: 'warning' },
  { label: '不在借阅时段', title: '无法借阅', message: '当前不在可借阅时段，请在规定时段内借书', type: 'warning' },
  { label: '身份无法识别', title: '身份识别失败', message: '人脸或者ID卡无法识别，请联系工作人员处理', type: 'error' },
  { label: '借阅数量超限', title: '数量超限', message: '可借阅数量已达上限，请先归还部分图书', type: 'warning' },
  { label: '存在逾期行为', title: '存在逾期', message: '目前有书籍逾期未归还，请先处理逾期书籍', type: 'error' },
  { label: '续借到期', title: '无法续借', message: '当前已达到可续借上限', type: 'info' },
  { label: '书籍无法识别', title: '识别失败', message: '书本异常，无法读取标签信息', type: 'error' },
  { label: '珍贵书籍', title: '无法外借', message: '该书为珍贵书籍，无法外借，仅限馆内阅读', type: 'warning' }
] as const

function triggerException(err: typeof exceptions[number]) {
  alertTitle.value = err.title
  alertMessage.value = err.message
  alertType.value = err.type
  showAlert.value = true
}

// 步骤状态：控制借阅流程（detect-识别阶段，success-成功阶段）
const step = ref<'detect' | 'success'>('detect')
// 识别状态：控制识别按钮的加载状态
const isDetecting = ref(false)
// 识别到的图书列表：存储识别到的图书信息
const detectedBooks = ref<Book[]>([])
// 提交状态：控制确认借阅按钮的加载状态
const isSubmitting = ref(false)
// 成功数量：记录成功借阅的图书数量
const successCount = ref(0)
// 应还日期：显示借阅成功的应还日期
const dueDate = ref('')

/**
 * 退出函数：登出并返回首页
 */
function exit() {
  auth.logout()
  router.push('/')
}

/**
 * 重置函数：重置所有状态到初始值
 */
function reset() {
  step.value = 'detect'
  detectedBooks.value = []
  successCount.value = 0
  countdown.value = 60 // 重置倒计时
}

/**
 * 开始识别函数：模拟图书识别过程
 */
async function startDetect() {
  if (isDetecting.value) return
  isDetecting.value = true
  detectedBooks.value = []
  
  // 获取可借阅图书池
  const pool = booksStore.availableBooks.slice(0, 10)
  
  // 模拟识别延迟
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // 随机取1-4本书
  const count = Math.floor(Math.random() * 4) + 1
  detectedBooks.value = pool.slice(0, Math.min(count, pool.length))
  isDetecting.value = false
}

/**
 * 确认借阅函数：处理图书借阅逻辑
 */
async function confirmBorrow() {
  // 验证用户登录状态
  if (!auth.user) {
    router.push('/login')
    return
  }
  
  // 验证是否有图书可借阅
  if (detectedBooks.value.length === 0) return
  
  isSubmitting.value = true
  successCount.value = 0
  
  // 计算应还日期（30天后）
  const date = new Date()
  date.setDate(date.getDate() + 30)
  dueDate.value = date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
  
  // 处理每本图书的借阅
  for (const b of detectedBooks.value) {
    const ok = await booksStore.borrowBook(b.id)
    if (ok) {
      await loansStore.borrowBook({ id: b.id, title: b.title, author: b.author, coverImageUrl: b.coverImageUrl })
      successCount.value++
    }
  }
  
  // 模拟处理延迟
  await new Promise(resolve => setTimeout(resolve, 300))
  
  isSubmitting.value = false
  step.value = 'success'
  countdown.value = 10 // 成功页倒计时缩短
}

/**
 * 倒计时函数：每秒递减，归零时退出
 */
function tick() {
  countdown.value--
  if (countdown.value <= 0) exit()
}

// 组件挂载时：初始化数据并启动倒计时
onMounted(() => {
  booksStore.initialize()
  loansStore.initialize()
  timer = setInterval(tick, 1000)
})

// 组件卸载时：清除定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
@keyframes scan {
  0% { top: 0; opacity: 0.5; }
  50% { top: 100%; opacity: 1; }
  100% { top: 0; opacity: 0.5; }
}
.animate-scan {
  animation: scan 2s linear infinite;
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-bounce-slow {
  animation: bounce 2s infinite;
}
</style>
