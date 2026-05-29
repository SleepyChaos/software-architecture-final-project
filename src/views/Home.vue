<!--
  首页组件 - PC端主界面
  功能：提供图书借阅系统的主入口，包含借阅、归还、个人中心等功能入口
  特点：
  - 顶部状态栏显示系统名称、用户信息和当前时间
  - 主体区域提供三个主要功能入口卡片：借阅图书、归还图书、个人中心
  - 底部提供图书续借快捷入口
  - 响应式设计，适配不同屏幕尺寸
-->
<template>
  <!-- 首页容器：全屏高度，浅灰色背景，垂直布局 -->
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- 顶部状态栏：白色背景，阴影效果，显示系统名称、用户信息和时间 -->
    <div class="w-full bg-white shadow-sm z-10">
      <!-- 顶部状态栏内容区：最大宽度限制，水平居中，左右分布 -->
      <div class="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <!-- 左侧：系统Logo和名称 -->
        <div class="flex items-center gap-3">
          <!-- 系统Logo：蓝色圆形背景，白色书本图标 -->
          <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
            <BookOpen class="w-6 h-6 text-white" />
          </div>
          <!-- 系统名称：中文名称和英文副标题 -->
          <div>
            <div class="text-xl font-bold text-slate-800 tracking-wide">自助借还书机</div>
            <div class="text-xs text-slate-500 uppercase tracking-wider">Self-service Kiosk</div>
          </div>
        </div>
        
        <!-- 右侧：用户信息和时间显示 -->
        <div class="flex items-center gap-6 text-slate-600">
          <!-- 登录状态组件：显示用户头像、姓名和部门，未登录时显示登录按钮 -->
          <div 
            class="flex items-center gap-3 px-3 py-1 rounded-full transition-colors cursor-pointer hover:bg-slate-50"
@click="$router.push(auth.user ? '/profile' : '/login')"
          >
            <!-- 用户头像区域：根据登录状态显示不同内容 -->
            <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden border border-slate-100">
               <!-- 未登录状态：显示用户图标 -->
               <User v-if="!auth.user" class="w-5 h-5 text-slate-400" />
               <!-- 已登录状态：显示用户姓名首字母 -->
               <div v-else class="w-full h-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                 {{ auth.user.fullName[0] }}
               </div>
            </div>
            <!-- 用户信息文字：显示用户姓名和部门 -->
            <div class="flex flex-col">
              <span class="text-sm font-bold text-slate-700">{{ auth.user ? auth.user.fullName : '未登录' }}</span>
              <span v-if="auth.user" class="text-xs text-slate-400">{{ auth.user.department }}</span>
            </div>
          </div>

          <!-- 分隔线：垂直灰色分割线 -->
          <div class="h-8 w-px bg-slate-200"></div>

          <!-- 时间显示区域：显示当前时间和日期 -->
          <div class="flex flex-col items-end">
            <span class="text-sm font-medium">{{ currentTime }}</span>
            <span class="text-xs">{{ currentDate }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区：功能入口卡片 -->
    <div class="flex-1 flex items-center justify-center p-8">
      <!-- 功能卡片网格：三列网格布局，响应式设计 -->
      <div class="w-full max-w-7xl h-full max-h-[800px] grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- 借阅图书入口卡片：跳转到图书借阅页面 -->
        <router-link
          to="/borrow"
          class="group relative overflow-hidden rounded-3xl bg-white shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 flex flex-col"
        >
          <!-- 悬停背景渐变：从蓝色到深蓝色的渐变背景 -->
          <div class="absolute inset-0 bg-gradient-to-br from-blue-500 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <!-- 卡片内容区：垂直居中，图标和文字 -->
          <div class="flex-1 flex flex-col items-center justify-center p-10 relative z-10">
            <!-- 图标容器：浅蓝色背景，借阅图标 -->
            <div class="w-32 h-32 bg-blue-50 rounded-full flex items-center justify-center mb-8 group-hover:bg-white/20 transition-colors duration-300">
              <BookUp class="w-16 h-16 text-blue-600 group-hover:text-white transition-colors duration-300" />
            </div>
            <!-- 卡片标题：借阅图书 -->
            <h2 class="text-3xl font-bold text-slate-800 group-hover:text-white mb-2">借阅图书</h2>
            <!-- 卡片副标题：英文提示 -->
            <p class="text-slate-500 group-hover:text-blue-100">Borrow Books</p>
          </div>
        </router-link>

        <!-- 归还图书入口卡片：跳转到图书归还页面 -->
        <router-link
          to="/return"
          class="group relative overflow-hidden rounded-3xl bg-white shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 flex flex-col"
        >
          <!-- 悬停背景渐变：从青色到深青色的渐变背景 -->
          <div class="absolute inset-0 bg-gradient-to-br from-teal-500 to-teal-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <!-- 卡片内容区：垂直居中，图标和文字 -->
          <div class="flex-1 flex flex-col items-center justify-center p-10 relative z-10">
            <!-- 图标容器：浅青色背景，归还图标 -->
            <div class="w-32 h-32 bg-teal-50 rounded-full flex items-center justify-center mb-8 group-hover:bg-white/20 transition-colors duration-300">
              <BookDown class="w-16 h-16 text-teal-600 group-hover:text-white transition-colors duration-300" />
            </div>
            <!-- 卡片标题：归还图书 -->
            <h2 class="text-3xl font-bold text-slate-800 group-hover:text-white mb-2">归还图书</h2>
            <!-- 卡片副标题：英文提示 -->
            <p class="text-slate-500 group-hover:text-teal-100">Return Books</p>
          </div>
        </router-link>

        <!-- 个人中心入口卡片：跳转到个人中心页面 -->
        <router-link
          to="/profile"
          class="group relative overflow-hidden rounded-3xl bg-white shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 flex flex-col"
        >
          <!-- 悬停背景渐变：从靛蓝色到深靛蓝色的渐变背景 -->
          <div class="absolute inset-0 bg-gradient-to-br from-indigo-500 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <!-- 卡片内容区：垂直居中，图标和文字 -->
          <div class="flex-1 flex flex-col items-center justify-center p-10 relative z-10">
            <!-- 图标容器：浅靛蓝色背景，用户图标 -->
            <div class="w-32 h-32 bg-indigo-50 rounded-full flex items-center justify-center mb-8 group-hover:bg-white/20 transition-colors duration-300">
              <UserCircle class="w-16 h-16 text-indigo-600 group-hover:text-white transition-colors duration-300" />
            </div>
            <!-- 卡片标题：个人中心 -->
            <h2 class="text-3xl font-bold text-slate-800 group-hover:text-white mb-2">个人中心</h2>
            <!-- 卡片副标题：英文提示 -->
            <p class="text-slate-500 group-hover:text-indigo-100">My Profile</p>
          </div>
        </router-link>
      </div>
    </div>

    <div class="w-full bg-white/50 backdrop-blur-sm border-t border-slate-200">
      <div class="max-w-7xl mx-auto px-6 py-6 flex justify-center gap-4">
        <router-link
          to="/renew"
          class="flex items-center gap-3 px-8 py-4 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-blue-300 hover:bg-blue-50 transition-all group"
        >
          <Clock class="w-6 h-6 text-slate-400 group-hover:text-blue-600" />
          <span class="text-lg font-medium text-slate-600 group-hover:text-blue-700">图书续借</span>
        </router-link>
        <router-link
          to="/statistics"
          class="flex items-center gap-3 px-8 py-4 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-emerald-300 hover:bg-emerald-50 transition-all group"
        >
          <BarChart3 class="w-6 h-6 text-slate-400 group-hover:text-emerald-600" />
          <span class="text-lg font-medium text-slate-600 group-hover:text-emerald-700">数据统计</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { BookOpen, BookUp, BookDown, UserCircle, Clock, User, BarChart3 } from 'lucide-vue-next'
import { useBooksStore } from '@/stores/books'
import { useLoansStore } from '@/stores/loans'
import { useAuthStore } from '@/stores/auth'

const booksStore = useBooksStore()
const loansStore = useLoansStore()
const auth = useAuthStore()

const currentTime = ref('')
const currentDate = ref('')
let timer: any = null

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  currentDate.value = now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' })
}

onMounted(() => {
  booksStore.initialize()
  loansStore.initialize()
  auth.initializeUser()
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
