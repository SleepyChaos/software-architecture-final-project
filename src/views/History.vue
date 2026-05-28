<!--
  借阅历史页面组件
  功能：展示用户的借阅历史记录，包括当前借阅和已归还图书
  特点：
  - 分类展示：区分当前借阅和历史借阅
  - 状态管理：显示图书借阅状态（正常、即将到期、逾期）
  - 续借功能：支持在线续借操作
  - 交互友好：提供续借、归还等操作按钮
  - 响应式设计：适配不同屏幕尺寸
-->
<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 页面标题栏 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <!-- 页面标题：根据路由显示"续借"或"借阅历史" -->
        <h1 class="text-xl font-semibold text-gray-900">{{ isRenew ? '续借' : '借阅历史' }}</h1>
        <!-- 续借模式下的倒计时和退出按钮 -->
        <div v-if="isRenew" class="flex items-center gap-2">
          <span class="text-sm text-gray-600">{{ countdown }} s</span>
          <button class="px-3 py-1 bg-blue-600 text-white rounded" @click="exit">退出</button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 续借区域：显示当前借阅的图书 -->
      <div class="mb-8">
        <h2 class="text-lg font-medium text-gray-900 mb-4">续借 ({{ currentBorrows.length }})</h2>
        
        <!-- 续借模式下的操作提示 -->
        <p v-if="isRenew" class="mb-4 text-blue-600 font-medium flex items-center gap-2">
          <BookOpen class="w-5 h-5" />
          请把书放入指定区域，会自动扫描到这本书
        </p>
        
        <!-- 空状态：当前无借阅图书 -->
        <div v-if="currentBorrows.length === 0" class="bg-white rounded-lg p-8 text-center">
          <BookOpen class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500">暂无借阅图书</p>
          <router-link :to="isRenew ? '/borrow' : '/search'" class="text-blue-600 hover:text-blue-700 mt-2 inline-block">
            去借阅图书
          </router-link>
        </div>
        
        <!-- 当前借阅图书列表 -->
        <div v-else class="space-y-4">
          <div
            v-for="record in currentBorrows"
            :key="record.id"
            class="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <!-- 单本图书信息 -->
            <div class="flex items-center gap-4">
              <!-- 图书封面 -->
              <img
                :src="record.bookCover"
                :alt="record.bookTitle"
                class="w-16 h-20 object-cover rounded"
              >
              <!-- 图书详情 -->
              <div class="flex-1 min-w-0">
                <h3 class="font-medium text-gray-900">{{ record.bookTitle }}</h3>
                <p class="text-sm text-gray-600">{{ record.bookAuthor }}</p>
                <div class="mt-2 space-y-1">
                  <!-- 借阅日期 -->
                  <p class="text-sm text-gray-500">
                    借阅日期：{{ formatDate(record.borrowDate) }}
                  </p>
                  <!-- 应还日期 -->
                  <p class="text-sm text-gray-500">
                    应还日期：{{ formatDate(record.dueDate) }}
                  </p>
                  <!-- 借阅状态标签 -->
                  <div>
                    <span
                      :class="[
                        'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        getStatusClass(record)
                      ]"
                    >
                      {{ getStatusText(record) }}
                    </span>
                  </div>
                </div>
              </div>
              <!-- 操作按钮 -->
              <div class="flex flex-col gap-2">

                <!-- 续借按钮 -->
                <button
                  @click="renewBook(record.id)"
                  :disabled="record.status === 'overdue'"
                  class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  确认续借
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 续借统计结果：显示续借操作的成功和失败数量统计 -->
        <div v-if="isRenew" class="mt-4 text-lg font-medium text-gray-700 bg-white p-4 rounded-lg shadow-sm border border-gray-100">
          成功续借 <span class="text-green-600 font-bold text-xl mx-1">{{ successCount }}</span> 本图书，
          失败 <span class="text-red-500 font-bold text-xl mx-1">{{ failCount }}</span> 本图书
        </div>
      </div>

      <!-- 当前借阅区域：显示用户当前正在借阅的图书列表 -->
      <div>
        <!-- 当前借阅标题：显示当前借阅图书数量 -->
        <h2 class="text-lg font-medium text-gray-900 mb-4">当前借阅 ({{ returnedBooks.length }})</h2>
        
        <!-- 空状态：当没有当前借阅图书时显示 -->
        <div v-if="returnedBooks.length === 0" class="bg-white rounded-lg p-8 text-center">
          <!-- 空状态图标：历史图标 -->
          <HistoryIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <!-- 空状态文本：提示暂无当前借阅 -->
          <p class="text-gray-500">暂无当前借阅</p>
        </div>
        
        <!-- 当前借阅图书列表：当存在当前借阅图书时显示 -->
        <div v-else class="space-y-4">
          <!-- 单本当前借阅图书项：循环渲染每本当前借阅的图书 -->
          <div
            v-for="record in returnedBooks"
            :key="record.id"
            class="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <!-- 单本当前借阅图书信息容器 -->
            <div class="flex items-center gap-4">
              <!-- 图书封面：显示当前借阅图书的封面图片 -->
              <img
                :src="record.bookCover"
                :alt="record.bookTitle"
                class="w-16 h-20 object-cover rounded"
              >
              <!-- 图书详情信息区：显示图书标题、作者和借阅信息 -->
              <div class="flex-1 min-w-0">
                <!-- 图书标题：显示当前借阅图书的名称 -->
                <h3 class="font-medium text-gray-900">{{ record.bookTitle }}</h3>
                <!-- 图书作者：显示当前借阅图书的作者 -->
                <p class="text-sm text-gray-600">{{ record.bookAuthor }}</p>
                <!-- 借阅信息区：显示借阅日期、归还日期和状态 -->
                <div class="mt-2 space-y-1">
                  <!-- 借阅日期：显示图书借阅的开始日期 -->
                  <p class="text-sm text-gray-500">
                    借阅日期：{{ formatDate(record.borrowDate) }}
                  </p>
                  <!-- 归还日期：显示图书应归还的日期 -->
                  <p class="text-sm text-gray-500">
                    归还日期：{{ formatDate(record.returnDate!) }}
                  </p>
                  <!-- 借阅状态标签：显示当前借阅状态（未归还） -->
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    未归还
                  </span>
                </div>
              </div>
              <!-- 续借按钮：点击可续借当前图书 -->
              <button
                @click="borrowAgain(record)"
                class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
              >
                续借
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航栏：在非续借模式下显示底部导航 -->
    <BottomNav v-if="!isRenew" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BookOpen, History as HistoryIcon } from 'lucide-vue-next'
import BottomNav from '@/components/BottomNav.vue'
import { useLoansStore } from '@/stores/loans'
import { useBooksStore } from '@/stores/books'
import { formatDate, getRemainingDays, isOverdue } from '@/utils'

// 状态管理
const loansStore = useLoansStore()
const booksStore = useBooksStore()
const route = useRoute()
const router = useRouter()

// 响应式数据
const isRenew = computed(() => route.name === 'Renew') // 是否为续借模式
const countdown = ref(60) // 倒计时（秒）
const successCount = ref(0) // 续借成功数量
const failCount = ref(0) // 续借失败数量
let timer: any = null // 定时器引用

/**
 * 退出当前页面
 * 功能：清除定时器并返回首页
 */
function exit() { 
  router.push('/'); 
  clearInterval(timer) 
}

// 计算属性：从store获取数据
const currentBorrows = computed(() => loansStore.currentBorrows) // 当前借阅列表
const returnedBooks = computed(() => loansStore.returnedBooks) // 已归还图书列表

/**
 * 获取借阅状态样式类
 * @param record - 借阅记录对象
 * @returns 状态样式类字符串
 */
function getStatusClass(record: any) {
  if (record.status === 'overdue') {
    return 'bg-red-100 text-red-800'
  }
  
  const remainingDays = getRemainingDays(record.dueDate)
  if (remainingDays <= 3) {
    return 'bg-yellow-100 text-yellow-800'
  }
  
  return 'bg-green-100 text-green-800'
}

/**
 * 获取借阅状态文本
 * @param record - 借阅记录对象
 * @returns 状态描述文本
 */
function getStatusText(record: any) {
  if (record.status === 'overdue') {
    return '已逾期'
  }
  
  const remainingDays = getRemainingDays(record.dueDate)
  if (remainingDays < 0) {
    return `逾期 ${Math.abs(remainingDays)} 天`
  } else if (remainingDays === 0) {
    return '今天到期'
  } else {
    return `还有 ${remainingDays} 天`
  }
}

/**
 * 归还图书
 * @param recordId - 借阅记录ID
 */
async function handleReturn(recordId: string) {
  await loansStore.returnBook(recordId)
}

/**
 * 续借图书
 * @param recordId - 借阅记录ID
 */
async function renewBook(recordId: string) {
  const success = await loansStore.renewBook(recordId)
  if (success) {
    successCount.value++
    alert('续借成功！')
  } else {
    failCount.value++
    alert('续借失败')
  }
}

// 再次借阅
async function borrowAgain(record: any) {
  // 查找对应的图书
  const book = booksStore.getBookById(record.bookId)
  if (book) {
    if (book.availableCopies > 0) {
      // 执行借阅操作
      const success = await booksStore.borrowBook(book.id)
      if (success) {
        await loansStore.borrowBook({
          id: book.id,
          title: book.title,
          author: book.author,
          coverImageUrl: book.coverImageUrl
        })
        alert(`成功借阅《${book.title}》！`)
      } else {
        alert('借阅失败，请重试')
      }
    } else {
      alert('该图书暂无库存')
    }
  }
}

// 初始化
onMounted(() => {
  loansStore.initialize()
  booksStore.initialize()
  if (isRenew.value) {
    timer = setInterval(() => { countdown.value--; if (countdown.value<=0) exit() }, 1000)
  }
})
</script>
