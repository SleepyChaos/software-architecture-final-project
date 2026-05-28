<template>
  <!-- 个人中心页面：显示用户个人信息和借阅统计 -->
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部个人信息区：蓝色背景，显示用户基本信息 -->
    <div class="bg-blue-500 text-white px-8 pt-8 pb-24 relative">
      <!-- 顶部栏：标题与退出控制 -->
      <div class="flex items-center justify-between mb-8">
        <!-- 页面标题：个人中心 -->
        <div class="text-2xl font-semibold">个人中心</div>
        <!-- 右侧控制区：倒计时和返回按钮 -->
        <div class="flex items-center gap-3">
          <!-- 倒计时显示：显示剩余时间，半透明背景 -->
          <div class="bg-blue-400/50 px-3 py-1 rounded-full text-sm backdrop-blur-sm">
            {{ countdown }}s 后退出
          </div>
          <!-- 返回首页按钮：半透明背景，悬停效果 -->
          <button 
            class="px-4 py-1 bg-white/20 hover:bg-white/30 text-white rounded-full text-sm transition-colors backdrop-blur-sm" 
            @click="exit"
          >
            返回首页
          </button>
        </div>
      </div>

      <!-- 用户基本信息区：显示姓名、证号和借阅统计 -->
      <div class="flex justify-between items-end">
        <div class="flex-1">
          <!-- 用户姓名和查看图标 -->
          <div class="flex items-center gap-4 mb-2">
            <!-- 用户姓名：脱敏显示 -->
            <h1 class="text-4xl font-bold">{{ maskedName }}</h1>
            <!-- 查看图标：眼睛图标，半透明 -->
            <div class="flex items-center gap-1 opacity-80">
              <Eye class="w-5 h-5" />
            </div>
          </div>
          <!-- 用户详细信息：证号和借阅统计 -->
          <div class="flex items-center gap-6 text-blue-100">
            <!-- 读者证号：脱敏显示 -->
            <p class="font-mono text-lg tracking-wide">读者证号：{{ maskedId }}</p>
            <!-- 借阅统计：当前借阅数量和进度条 -->
            <div class="flex items-center gap-2">
              <!-- 借阅数量文本：显示当前借阅数量和上限 -->
              <span class="text-sm">在借图书：{{ loansStore.currentBorrows.length }}/10</span>
              <!-- 进度条：显示借阅数量占比，白色进度条 -->
              <div class="w-32 h-2 bg-blue-400/50 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-white rounded-full" 
                  :style="{ width: `${Math.min((loansStore.currentBorrows.length / 10) * 100, 100)}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 悬浮统计卡片：白色背景，显示借阅统计信息 -->
    <div class="max-w-6xl mx-auto px-4 -mt-16 relative z-10 mb-8">
      <!-- 统计卡片容器：三栏布局，分割线分隔 -->
      <div class="bg-white rounded-xl shadow-lg p-6 grid grid-cols-3 divide-x divide-gray-100">
        <!-- 当前借阅统计：显示当前借阅数量 -->
        <div class="text-center px-4">
          <!-- 数量显示：蓝色大字体 -->
          <div class="text-3xl font-bold text-blue-600 mb-1">{{ loansStore.currentBorrows.length }}</div>
          <!-- 标签：当前借阅，带图标 -->
          <div class="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <BookOpen class="w-4 h-4 text-blue-500" />
            当前借阅
          </div>
        </div>
        <!-- 历史借阅统计：显示历史借阅数量 -->
        <div class="text-center px-4">
          <!-- 数量显示：绿色大字体 -->
          <div class="text-3xl font-bold text-green-600 mb-1">{{ loansStore.returnedBooks.length }}</div>
          <!-- 标签：历史借阅，带图标 -->
          <div class="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <History class="w-4 h-4 text-green-500" />
            历史借阅
          </div>
        </div>
        <!-- 滞纳金统计：显示滞纳金金额 -->
        <div class="text-center px-4">
          <!-- 金额显示：橙色大字体 -->
          <div class="text-3xl font-bold text-orange-500 mb-1">0</div>
          <!-- 标签：滞纳金，带图标 -->
          <div class="flex items-center justify-center gap-2 text-gray-500 text-sm">
            <AlertCircle class="w-4 h-4 text-orange-500" />
            滞纳金 (元)
          </div>
        </div>
      </div>
    </div>

    <!-- 列表区域：显示当前借阅图书列表 -->
    <div class="max-w-6xl mx-auto px-4">
      <!-- 列表容器：白色背景，圆角阴影 -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden min-h-[400px]">
        <!-- 列表头：灰色背景，显示列标题 -->
        <div class="grid grid-cols-12 gap-4 px-6 py-4 bg-gray-50 border-b border-gray-100 text-sm font-medium text-gray-500">
          <div class="col-span-1">编号</div>
          <div class="col-span-6">在借书单</div>
          <div class="col-span-5 text-right">逾期日期</div>
        </div>
        
        <!-- 列表内容区：根据是否有借阅记录显示不同内容 -->
        <div v-if="loansStore.currentBorrows.length === 0" class="flex flex-col items-center justify-center py-20 text-gray-400">
          <!-- 空状态图标：书本图标 -->
          <BookOpen class="w-16 h-16 mb-4 text-gray-300" />
          <!-- 空状态文字：暂无借阅记录 -->
          <p>暂无借阅记录</p>
        </div>
        
        <!-- 借阅记录列表：当存在借阅记录时显示 -->
        <div v-else class="divide-y divide-gray-50">
          <!-- 单本图书记录：循环渲染每本借阅的图书 -->
          <div 
            v-for="(record, index) in loansStore.currentBorrows" 
            :key="record.id"
            class="grid grid-cols-12 gap-4 px-6 py-5 items-center hover:bg-blue-50/50 transition-colors"
          >
            <!-- 编号：两位数格式，不足补零 -->
            <div class="col-span-1 text-gray-400 font-mono">{{ String(index + 1).padStart(2, '0') }}</div>
            <!-- 图书信息：标题、作者和借阅日期 -->
            <div class="col-span-6">
              <!-- 图书标题：加粗显示 -->
              <div class="font-bold text-gray-800 text-lg mb-1">{{ record.bookTitle }}</div>
              <!-- 图书详情：作者和借阅日期 -->
              <div class="text-sm text-gray-500 flex gap-4">
                <span>{{ record.bookAuthor }}</span>
                <span class="text-gray-300">|</span>
                <span>借阅于 {{ record.borrowDate }}</span>
              </div>
            </div>
            <!-- 归还信息：应还日期和状态 -->
            <div class="col-span-5 text-right">
              <!-- 应还日期：根据是否逾期显示不同颜色 -->
              <div class="text-lg font-medium" :class="isOverdue(record.dueDate) ? 'text-red-500' : 'text-gray-700'">
                {{ record.dueDate }}
              </div>
              <!-- 逾期警告：当图书已逾期时显示 -->
              <div v-if="isOverdue(record.dueDate)" class="text-xs text-red-500 mt-1 font-bold flex items-center justify-end gap-1">
                <!-- 警告图标：三角形警告图标 -->
                <AlertTriangle class="w-3 h-3" />
                <!-- 逾期天数：显示已逾期天数 -->
                已逾期 {{ getOverdueDays(record.dueDate) }} 天
              </div>
              <!-- 剩余天数：当图书未逾期时显示 -->
              <div v-else class="text-xs text-gray-400 mt-1">
                <!-- 剩余天数：显示距离应还日期的剩余天数 -->
                剩余 {{ getRemainingDays(record.dueDate) }} 天
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, BookOpen, Eye, AlertCircle, AlertTriangle, History } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useLoansStore } from '@/stores/loans'

// 路由和状态管理
const router = useRouter()
const authStore = useAuthStore()
const loansStore = useLoansStore()

// 倒计时状态：用于自动返回首页
const countdown = ref(60)
let timer: ReturnType<typeof setInterval> | null = null

/**
 * 退出函数：返回首页
 */
function exit() {
  router.push('/')
}

/**
 * 倒计时逻辑
 */
function tick() {
  countdown.value--
  if (countdown.value <= 0) exit()
}

// 组件挂载时：启动倒计时并初始化数据
onMounted(() => {
  timer = setInterval(tick, 1000)
  if (!authStore.user) authStore.initializeUser()
  loansStore.initialize()
})

// 组件卸载时：清除定时器
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// 计算属性：脱敏处理用户姓名
const maskedName = computed(() => {
  const n = authStore.user?.fullName || '用户'
  if (n.length <= 1) return n
  return n[0] + '*'.repeat(Math.max(1, n.length - 1))
})

// 计算属性：脱敏处理读者证号
const maskedId = computed(() => {
  const id = authStore.user?.studentId || ''
  if (!id) return ''
  if (id.length <= 4) return '****'
  return '********' + id.slice(-4)
})

/**
 * 检查图书是否逾期
 * @param dateStr 应还日期
 * @returns 是否逾期
 */
function isOverdue(dateStr: string) {
  const due = new Date(dateStr).setHours(0, 0, 0, 0)
  const now = new Date().setHours(0, 0, 0, 0)
  return now > due
}

/**
 * 获取逾期天数
 * @param dateStr 应还日期
 * @returns 逾期天数
 */
function getOverdueDays(dateStr: string) {
  const due = new Date(dateStr).getTime()
  const now = new Date().getTime()
  const diff = now - due
  return Math.floor(diff / (1000 * 60 * 60 * 24))
}

/**
 * 获取剩余天数
 * @param dateStr 应还日期
 * @returns 剩余天数
 */
function getRemainingDays(dateStr: string) {
  const due = new Date(dateStr).getTime()
  const now = new Date().getTime()
  const diff = due - now
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}
</script>
