<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部标题栏：显示页面标题和滞纳金入口 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-semibold text-gray-900">我的</h1>
        <router-link v-if="auth.isAuthenticated" to="/fines" class="text-blue-600">滞纳金</router-link>
      </div>
    </div>

    <!-- 未登录状态：显示登录表单 -->
    <div v-if="!auth.isAuthenticated" class="max-w-md mx-auto px-4 py-12">
      <div class="bg-white rounded-lg shadow-sm p-8">
        <!-- 登录头部：图标和标题 -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserIcon class="w-8 h-8" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900">用户登录</h2>
          <p class="text-gray-500 mt-2">请使用读者证号登录</p>
        </div>

        <!-- 登录表单：读者证号和密码输入 -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">读者证号</label>
            <input 
              v-model="loginForm.studentId"
              type="text" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="请输入读者证号"
              required
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input 
              v-model="loginForm.password"
              type="password" 
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              placeholder="请输入密码"
              required
            >
          </div>

          <!-- 错误提示：显示登录错误信息 -->
          <div v-if="auth.error" class="text-red-500 text-sm text-center">
            {{ auth.error }}
          </div>

          <!-- 登录按钮：提交表单和加载状态 -->
          <button 
            type="submit" 
            :disabled="auth.isLoading"
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-bold text-lg hover:bg-blue-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Loader2 v-if="auth.isLoading" class="w-5 h-5 animate-spin mr-2" />
            {{ auth.isLoading ? '登录中...' : '立即登录' }}
          </button>
        </form>
        
        <!-- 测试账号提示：显示测试用登录信息 -->
        <div class="mt-6 text-center text-sm text-gray-500">
          <p>测试账号：001 / 123456</p>
        </div>
      </div>
    </div>

    <!-- 已登录状态：显示用户信息和管理功能 -->
    <div v-else class="max-w-7xl mx-auto px-4 py-6">
      <!-- 用户信息卡片：头像、姓名、借阅统计和退出按钮 -->
      <div class="bg-white rounded-lg p-6 mb-6 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <!-- 左侧：用户头像和基本信息 -->
            <div class="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xl">
              {{ initials }}
            </div>
            <div>
              <div class="font-semibold text-gray-900 text-lg">{{ displayName }}</div>
              <div class="text-sm text-gray-600">在借：{{ loansStore.currentBorrows.length }} / 10</div>
            </div>
          </div>
          <!-- 右侧：退出登录按钮 -->
          <button @click="handleLogout" class="text-gray-500 hover:text-red-600 text-sm px-3 py-1 border rounded hover:border-red-600 transition-colors">
            退出
          </button>
        </div>
      </div>

      <!-- 电子读者证：显示读者证信息和条形码 -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
          <h3 class="font-bold text-gray-800">电子读者证</h3>
          <span class="text-sm text-gray-500">用于馆内扫码识别</span>
        </div>
        <div class="p-6 flex items-center gap-6">
          <!-- 左侧：读者证基本信息 -->
          <div class="flex-1">
            <div class="text-lg font-semibold text-gray-900">{{ displayName }}</div>
            <div class="text-sm text-gray-600">读者证号：{{ readerId }}</div>
          </div>
          <!-- 右侧：条形码区域 -->
          <div class="w-48 h-20 bg-gray-100 rounded flex items-center justify-center overflow-hidden">
            <div class="flex gap-1 w-40">
              <div v-for="n in 40" :key="n" :style="{ width: (n%5===0?3:1)+'px', background: n%2===0?'#111':'#eee', height: '100%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 当前借阅：显示正在借阅的图书列表 -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
          <h3 class="font-bold text-gray-800">当前借阅</h3>
        </div>
        <div v-if="loansStore.currentBorrows.length === 0" class="p-8 text-center text-gray-500">暂无借阅</div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="rec in loansStore.currentBorrows" :key="rec.id" class="flex items-center gap-4 p-4">
            <!-- 左侧：图书封面 -->
            <img :src="rec.bookCover" class="w-12 h-16 object-cover rounded" />
            <!-- 中间：图书信息和到期时间 -->
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ rec.bookTitle }}</div>
              <div class="text-sm text-gray-600">到期：{{ rec.dueDate }}</div>
            </div>
            <!-- 右侧：查看详情链接 -->
            <router-link :to="`/book/${rec.bookId}`" class="text-blue-600">详情</router-link>
          </div>
        </div>
      </div>

      <!-- 历史记录：显示已归还的图书列表 -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden mt-6">
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
          <h3 class="font-bold text-gray-800">历史记录</h3>
        </div>
        <div v-if="loansStore.returnedBooks.length === 0" class="p-8 text-center text-gray-500">暂无记录</div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="rec in loansStore.returnedBooks" :key="rec.id" class="flex items-center gap-4 p-4">
            <!-- 左侧：图书封面 -->
            <img :src="rec.bookCover" class="w-12 h-16 object-cover rounded" />
            <!-- 右侧：图书信息和归还日期 -->
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ rec.bookTitle }}</div>
              <div class="text-sm text-gray-600">归还：{{ rec.returnDate }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 预约记录：显示图书预约申请记录 -->
      <div class="bg-white rounded-lg shadow-sm overflow-hidden mt-6">
        <div class="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
          <h3 class="font-bold text-gray-800">预约记录</h3>
          <router-link to="/search" class="text-blue-600 text-sm">去预约</router-link>
        </div>
        <div v-if="reservations.length === 0" class="p-8 text-center text-gray-500">暂无预约</div>
        <div v-else class="divide-y divide-gray-100">
          <div v-for="r in reservations" :key="r.id" class="flex items-center gap-4 p-4">
            <!-- 左侧：预约图书信息 -->
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ r.bookTitle }}</div>
              <div class="text-sm text-gray-600">条码：{{ r.barcode || '未指定' }} · 取书分馆：{{ r.pickupBranch }}</div>
              <div class="text-xs text-gray-400">申请时间：{{ r.requestedAt }}</div>
            </div>
            <!-- 中间：预约状态标签 -->
            <span 
              class="px-2 py-1 rounded text-xs"
              :class="r.status==='requested' ? 'bg-yellow-100 text-yellow-700' : r.status==='fulfilled' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
            >
              {{ r.status === 'requested' ? '待处理' : r.status === 'fulfilled' ? '已完成' : '已取消' }}
            </span>
            <!-- 右侧：取消预约按钮（仅待处理状态显示） -->
            <button v-if="r.status==='requested'" @click="cancelReservation(r.id)" class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm">取消</button>
          </div>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import BottomNav from '@/components/BottomNav.vue'
import { useAuthStore } from '@/stores/auth'
import { useLoansStore } from '@/stores/loans'
import { useRequestsStore } from '@/stores/requests'
import { computed, onMounted, ref } from 'vue'
import { User as UserIcon, Loader2 } from 'lucide-vue-next'

// 状态管理：用户认证、借阅记录、预约请求存储实例
const auth = useAuthStore()
const loansStore = useLoansStore()
const requestsStore = useRequestsStore()

// 计算属性：显示名称、姓名首字母、读者证号、预约记录列表
const displayName = computed(() => auth.user?.fullName || '未登录')
const initials = computed(() => (auth.user?.fullName ? auth.user.fullName[0] : '客'))
const readerId = computed(() => auth.user?.studentId || '未绑定')
const reservations = computed(() => requestsStore.list)

// 响应式数据：登录表单
const loginForm = ref({
  studentId: '',
  password: ''
})

/**
 * 处理用户登录
 * 验证表单数据并调用认证服务进行登录
 */
async function handleLogin() {
  if (!loginForm.value.studentId || !loginForm.value.password) return
  await auth.login(loginForm.value.studentId, loginForm.value.password)
}

/**
 * 处理用户退出
 * 清除登录状态并重置登录表单
 */
function handleLogout() {
  auth.logout()
  loginForm.value = { studentId: '', password: '' }
}

/**
 * 取消预约
 * @param id - 预约记录ID
 */
function cancelReservation(id: string) {
  requestsStore.cancelReservation(id)
}

/**
 * 组件挂载时初始化数据
 * 加载借阅记录，如未登录则初始化用户信息
 */
onMounted(() => {
  loansStore.initialize()
  if (!auth.isAuthenticated) {
    auth.initializeUser()
  }
})
</script>
