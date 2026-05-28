<template>
  <!-- 归还图书页面：提供分步骤的图书归还流程 -->
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- 顶部状态栏：显示页面标题、倒计时和退出按钮 -->
    <div class="bg-teal-600 text-white shadow-md z-10">
      <div class="max-w-7xl mx-auto px-8 py-6 flex items-center justify-between">
        <!-- 左侧：页面图标和标题 -->
        <div class="flex items-center gap-4">
          <!-- 页面图标：书本向下图标，半透明背景 -->
          <div class="p-2 bg-white/10 rounded-xl">
            <BookDown class="w-8 h-8" />
          </div>
          <!-- 页面标题：归还图书 -->
          <div class="text-3xl font-bold tracking-wide">归还图书</div>
        </div>
        <!-- 右侧：倒计时和退出按钮 -->
        <div class="flex items-center gap-6">
          <!-- 倒计时显示：时钟图标和剩余秒数 -->
          <div class="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full">
            <Clock class="w-5 h-5" />
            <span class="text-xl font-mono">{{ countdown }}s</span>
          </div>
          <!-- 退出按钮：白色背景，悬停效果 -->
          <button 
            class="px-6 py-2 bg-white text-teal-600 rounded-full font-bold hover:bg-teal-50 transition-colors shadow-sm"
            @click="exit"
          >
            退出
          </button>
        </div>
      </div>
    </div>

    <!-- 主内容区：包含步骤指示器和各步骤内容 -->
    <div class="flex-1 max-w-6xl mx-auto w-full p-8">
      <!-- 步骤指示器：显示当前进度和步骤名称 -->
      <div class="flex items-center justify-center mb-12">
        <div class="flex items-center w-full max-w-3xl relative">
          <!-- 进度条背景：灰色线条 -->
          <div class="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 transform -translate-y-1/2 rounded-full"></div>
          <!-- 进度条前景：根据当前步骤动态宽度 -->
          <div 
            class="absolute top-1/2 left-0 h-1 bg-teal-500 -z-10 transform -translate-y-1/2 rounded-full transition-all duration-500"
            :style="{ width: `${(step - 1) * 33.33}%` }"
          ></div>
          
          <!-- 步骤节点：循环渲染4个步骤 -->
          <div v-for="s in 4" :key="s" class="flex-1 flex flex-col items-center relative">
            <!-- 步骤圆圈：根据是否完成显示不同样式 -->
            <div 
              class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg border-4 transition-all duration-300 bg-white"
              :class="step >= s ? 'border-teal-500 text-teal-600 scale-110' : 'border-gray-200 text-gray-400'"
            >
              {{ s }}
            </div>
            <!-- 步骤名称：根据是否完成显示不同颜色 -->
            <div class="mt-3 text-sm font-medium" :class="step >= s ? 'text-teal-700' : 'text-gray-400'">
              {{ ['选择数量', '放置书籍', '确认归还', '完成'][s-1] }}
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤1：选择数量 -->
      <div v-if="step === 1" class="bg-white rounded-3xl shadow-xl p-12 animate-fade-in">
        <!-- 步骤标题：提示用户选择归还数量 -->
        <h2 class="text-3xl font-bold text-slate-800 mb-8 text-center">请选择您要归还的图书数量</h2>
        
        <!-- 数量选择按钮：1-5的数字按钮 -->
        <div class="grid grid-cols-5 gap-6 mb-12">
          <button 
            v-for="n in 5" 
            :key="n" 
            class="aspect-square rounded-2xl text-4xl font-bold transition-all duration-200 shadow-sm border-2 flex items-center justify-center"
            :class="count === n 
              ? 'bg-teal-600 text-white border-teal-600 shadow-teal-500/30 scale-105' 
              : 'bg-white text-slate-600 border-slate-200 hover:border-teal-300 hover:bg-teal-50'"
            @click="selectCount(n)"
          >
            {{ n }}
          </button>
        </div>

        <!-- 下一步按钮：进入放置书籍步骤 -->
        <div class="flex justify-center">
          <button 
            class="px-16 py-4 bg-teal-600 text-white rounded-2xl font-bold text-xl hover:bg-teal-700 transition-all shadow-lg hover:shadow-teal-500/30 disabled:bg-slate-300 disabled:shadow-none disabled:cursor-not-allowed"
            :disabled="count === 0"
            @click="toPlace"
          >
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤2：放置书籍 -->
      <div v-else-if="step === 2" class="bg-white rounded-3xl shadow-xl p-12 text-center animate-fade-in">
        <!-- 放置区域：蓝色虚线框，模拟感应区 -->
        <div class="w-64 h-48 bg-blue-50 mx-auto mb-8 rounded-2xl flex items-center justify-center border-2 border-dashed border-blue-200 relative overflow-hidden">
          <!-- 脉冲动画：模拟感应效果 -->
          <div class="absolute inset-0 bg-blue-100/30 animate-pulse"></div>
          <!-- 书本图标：蓝色，居中显示 -->
          <BookDown class="w-24 h-24 text-blue-400 relative z-10" />
        </div>
        <!-- 放置提示：显示归还数量和放置要求 -->
        <h2 class="text-3xl font-bold text-slate-800 mb-4">请将 {{ count }} 本图书放置在感应区</h2>
        <p class="text-slate-500 mb-12 text-lg">请确保图书平整放置，不要重叠</p>
        
        <!-- 确认按钮：进入识别步骤 -->
        <button 
          class="px-16 py-4 bg-teal-600 text-white rounded-2xl font-bold text-xl hover:bg-teal-700 transition-all shadow-lg hover:shadow-teal-500/30"
          @click="startDetect"
        >
          我已放置好
        </button>
      </div>

      <!-- 步骤3：检测与确认 -->
      <div v-else-if="step === 3" class="flex gap-8 animate-fade-in">
        <!-- 左侧：识别列表 -->
        <div class="flex-[2] bg-white rounded-3xl shadow-lg flex flex-col overflow-hidden">
          <!-- 列表头部：显示识别结果标题和统计信息 -->
          <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <!-- 标题：识别结果，带扫描图标 -->
            <h3 class="text-xl font-bold text-slate-700 flex items-center gap-2">
              <ScanLine class="w-6 h-6 text-teal-500" />
              识别结果
            </h3>
            <!-- 统计标签：应还数量和实测数量 -->
            <div class="flex gap-2">
              <!-- 应还数量：灰色标签 -->
              <span class="px-3 py-1 bg-slate-100 text-slate-600 rounded-full text-sm font-medium">
                应还 {{ count }} 本
              </span>
              <!-- 实测数量：绿色标签 -->
              <span class="px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm font-bold">
                实测 {{ detected.length }} 本
              </span>
            </div>
          </div>
          
          <!-- 列表内容区：显示识别到的图书或加载状态 -->
          <div class="flex-1 p-6 overflow-y-auto min-h-[400px]">
            <!-- 加载状态：当未识别到图书时显示 -->
            <div v-if="detected.length === 0" class="h-full flex flex-col items-center justify-center text-slate-400">
              <!-- 加载动画：旋转的圆圈 -->
              <div class="w-16 h-16 border-4 border-slate-200 border-t-teal-500 rounded-full animate-spin mb-4"></div>
              <!-- 加载提示：正在读取图书信息 -->
              <p class="text-lg">正在读取图书信息...</p>
            </div>
            
            <!-- 图书列表：当识别到图书时显示 -->
            <ul v-else class="grid grid-cols-1 gap-4">
              <!-- 单本图书信息：循环渲染每本识别到的图书 -->
              <li v-for="r in detected" :key="r.id" class="flex gap-4 p-4 rounded-2xl border border-slate-100 bg-white hover:shadow-md transition-all">
                <!-- 图书封面：缩略图显示 -->
                <img :src="r.bookCover" class="w-20 h-28 object-cover rounded-lg shadow-sm" />
                <!-- 图书详情：标题、作者和借阅日期 -->
                <div class="flex-1 flex flex-col justify-center">
                  <!-- 图书标题：加粗显示 -->
                  <h4 class="text-lg font-bold text-slate-800 mb-1">{{ r.bookTitle }}</h4>
                  <!-- 图书作者：灰色文字 -->
                  <p class="text-slate-500 text-sm mb-1">{{ r.bookAuthor }}</p>
                  <!-- 借阅日期：灰色小字 -->
                  <p class="text-sm text-slate-400">借阅日期: {{ formatDate(r.borrowDate) }}</p>
                </div>
                <!-- 归还信息：到期时间和状态 -->
                <div class="flex flex-col justify-center items-end px-2">
                  <!-- 到期时间标签：灰色小字 -->
                  <div class="text-xs text-slate-500 mb-1">到期时间</div>
                  <!-- 到期日期：等宽字体，加粗 -->
                  <div class="font-mono font-bold text-slate-700 mb-2">{{ formatDate(r.dueDate) }}</div>
                  <!-- 状态标签：根据是否逾期显示不同颜色 -->
                  <span 
                    class="px-2 py-1 rounded text-xs font-bold"
                    :class="r.status==='overdue' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'"
                  >
                    {{ r.status==='overdue' ? '已逾期' : '正常' }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- 右侧：操作区 -->
        <div class="flex-1 flex flex-col gap-6">
          <!-- 信息提示卡片：核对信息说明 -->
          <div class="bg-teal-50 rounded-3xl p-6 border border-teal-100">
            <!-- 卡片标题：核对信息，带信息图标 -->
            <h4 class="font-bold text-teal-800 mb-2 flex items-center gap-2">
              <Info class="w-5 h-5" />
              核对信息
            </h4>
            <!-- 提示文字：说明核对要求和操作步骤 -->
            <p class="text-teal-600 text-sm leading-relaxed">
              请核对识别出的图书信息是否正确。如有遗漏，请点击"重新识别"。确认无误后点击"确认归还"。
            </p>
          </div>

          <!-- 操作按钮区：确认归还和重新选择 -->
          <div class="mt-auto flex flex-col gap-4">
            <!-- 确认归还按钮：主要操作，绿色背景 -->
            <button 
              class="w-full py-5 bg-teal-600 text-white rounded-2xl font-bold text-xl hover:bg-teal-700 transition-all shadow-xl hover:shadow-teal-500/30 disabled:bg-slate-300 disabled:shadow-none disabled:cursor-not-allowed flex items-center justify-center gap-2"
              :disabled="detected.length === 0 || isSubmitting"
              @click="confirmReturn"
            >
              <!-- 加载动画：当提交中时显示旋转圆圈 -->
              <div v-if="isSubmitting" class="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
              <!-- 按钮文字：根据提交状态显示不同文字 -->
              <span>{{ isSubmitting ? '处理中...' : '确认归还' }}</span>
            </button>
            
            <!-- 重新选择按钮：次要操作，白色背景 -->
            <button 
              class="w-full py-4 bg-white text-slate-600 rounded-2xl font-bold text-lg hover:bg-slate-50 transition-colors border border-slate-200"
              @click="reset"
              :disabled="isSubmitting"
            >
              重新选择数量
            </button>
          </div>
        </div>
      </div>

      <!-- 步骤4：完成 -->
      <div v-else-if="step === 4" class="flex flex-col items-center justify-center p-8 animate-fade-in">
        <!-- 完成卡片：白色背景，圆角阴影 -->
        <div class="bg-white rounded-3xl shadow-xl p-12 max-w-2xl w-full text-center">
          <!-- 成功图标：绿色背景，白色勾选 -->
          <div class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce-slow">
            <Check class="w-12 h-12 text-green-600" />
          </div>
          <!-- 完成标题：归还完成 -->
          <h2 class="text-4xl font-bold text-slate-800 mb-4">归还完成</h2>
          <!-- 结果统计：显示成功和失败数量 -->
          <p class="text-xl text-slate-500 mb-8">
            成功归还 <span class="text-green-600 font-bold">{{ successCount }}</span> 本，
            失败 <span class="text-red-500 font-bold">{{ failedCount }}</span> 本
          </p>
          
          <!-- 操作按钮：返回首页和继续归还 -->
          <div class="flex gap-4">
            <!-- 返回首页按钮：灰色背景 -->
            <button 
              class="flex-1 py-4 bg-gray-100 text-slate-600 rounded-xl font-bold text-lg hover:bg-gray-200 transition-colors"
              @click="exit"
            >
              返回首页
            </button>
            <!-- 继续归还按钮：绿色背景 -->
            <button 
              class="flex-1 py-4 bg-teal-600 text-white rounded-xl font-bold text-lg hover:bg-teal-700 transition-colors shadow-lg hover:shadow-teal-500/30"
              @click="restart"
            >
              继续归还
            </button>
          </div>
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
      <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">还书流程异常模拟</h3>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { BookDown, Clock, ScanLine, Check, Info } from 'lucide-vue-next'
import AlertModal from '@/components/AlertModal.vue'
import { useAuthStore } from '@/stores/auth'
import { useLoansStore } from '@/stores/loans'
import { formatDate } from '@/utils'

// 路由和状态管理
const router = useRouter()

// 异常模拟状态
const showDebug = ref(false)
const showAlert = ref(false)
const alertTitle = ref('')
const alertMessage = ref('')
const alertType = ref<'error' | 'warning' | 'info'>('info')

const exceptions = [
  { label: '系统超时', title: '操作超时', message: '系统繁忙，请稍后再试', type: 'warning' },
  { label: '不在还书时段', title: '无法还书', message: '当前不在还书时段，请在工作时间段内归还', type: 'warning' },
  { label: '书籍逾期', title: '逾期提醒', message: '检测到逾期行为，将根据规定限制下次借书权限', type: 'warning' },
  { label: '多本逾期', title: '逾期提醒', message: '你还有其他书需要一起归还，请一并处理', type: 'info' },
  { label: '书籍不匹配', title: '识别错误', message: '书籍不匹配，非本馆图书或未借阅该书', type: 'error' },
  { label: '还有其他书', title: '归还提示', message: '检测到您名下还有其他待还书籍', type: 'info' }
] as const

function triggerException(err: typeof exceptions[number]) {
  alertTitle.value = err.title
  alertMessage.value = err.message
  alertType.value = err.type
  showAlert.value = true
}
const auth = useAuthStore()
const loansStore = useLoansStore()

// 倒计时状态：用于自动退出
const countdown = ref(60)
let timer: any = null

// 步骤状态：控制归还流程的当前步骤
const step = ref(1)
// 归还数量：用户选择的归还图书数量
const count = ref(0)
// 识别结果：存储识别到的图书信息
const detected = ref<any[]>([])
// 提交状态：控制按钮的加载状态
const isSubmitting = ref(false)
// 成功数量：记录成功归还的图书数量
const successCount = ref(0)
// 失败数量：记录归还失败的图书数量
const failedCount = ref(0)

/**
 * 退出函数：登出并返回首页
 */
function exit() {
  // 如果用户已登录则登出，否则直接返回
  if (auth.user) auth.logout()
  router.push('/')
}

/**
 * 选择数量函数：设置归还数量
 * @param n 选择的数量
 */
function selectCount(n: number) { count.value = n }

/**
 * 进入放置步骤：验证数量后进入下一步
 */
function toPlace() { if (count.value > 0) step.value = 2 }

/**
 * 开始识别函数：模拟图书识别过程
 */
async function startDetect() {
  step.value = 3
  detected.value = []
  
  // 模拟识别延迟
  await new Promise(resolve => setTimeout(resolve, 300))
  
  // 获取当前借阅记录作为识别池
  const pool = loansStore.currentBorrows.slice(0, 10)
  
  // 模拟识别出用户选择数量的书籍
  let mockDetected = pool.slice(0, Math.min(count.value, pool.length))
  
  // 如果没有在借记录，生成演示数据
  if (mockDetected.length === 0) {
     mockDetected = Array.from({ length: count.value }).map((_, i) => ({
       id: `mock-${i}`,
       bookId: `book-${i}`,
       bookTitle: '演示图书 ' + (i + 1),
       bookAuthor: '未知作者',
       bookCover: 'https://via.placeholder.com/150',
       borrowDate: new Date().toISOString(),
       dueDate: new Date(Date.now() + 86400000 * 10).toISOString(),
       status: 'borrowed'
     }))
  }
  
  detected.value = mockDetected
}

/**
 * 确认归还函数：处理图书归还逻辑
 */
async function confirmReturn() {
  if (detected.value.length === 0) return
  
  isSubmitting.value = true
  successCount.value = 0
  failedCount.value = 0
  
  // 处理每本图书的归还
  for (const r of detected.value) {
    const ok = await loansStore.returnBookByBookId(r.bookId)
    if (ok) successCount.value++; else failedCount.value++
  }
  
  // 模拟处理延迟
  await new Promise(resolve => setTimeout(resolve, 300))
  
  isSubmitting.value = false
  step.value = 4
  countdown.value = 10 // 成功页倒计时缩短
}

/**
 * 重置函数：重置所有状态到初始值
 */
function reset() { 
  step.value = 1
  count.value = 0
  detected.value = []
  successCount.value = 0
  failedCount.value = 0
  countdown.value = 60
}

/**
 * 重新开始函数：调用重置函数
 */
function restart() { reset() }

/**
 * 倒计时函数：每秒递减，归零时退出
 */
function tick() {
  countdown.value--
  if (countdown.value <= 0) exit()
}

// 组件挂载时：初始化数据并启动倒计时
onMounted(() => { 
  loansStore.initialize()
  timer = setInterval(tick, 1000) 
})

// 组件卸载时：清除定时器
onUnmounted(() => { 
  if (timer) clearInterval(timer) 
})
</script>

<style scoped>
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
