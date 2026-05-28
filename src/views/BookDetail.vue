<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部返回栏：显示返回按钮 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4">
        <button
          @click="goBack"
          class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft class="w-5 h-5" />
          <span>返回</span>
        </button>
      </div>
    </div>

    <!-- 图书详情内容：显示图书详细信息 -->
    <div v-if="book" class="max-w-4xl mx-auto px-4 py-6">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="md:flex">
          <!-- 左侧：图书封面展示区 -->
          <div class="md:w-1/3 p-6">
            <img
              :src="book.coverImageUrl"
              :alt="book.title"
              class="w-full h-80 object-cover rounded-lg shadow-md"
              @error="handleImageError"
            >
          </div>
          
          <!-- 右侧：图书基本信息区 -->
          <div class="md:w-2/3 p-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ book.title }}</h1>
            <p class="text-lg text-gray-600 mb-4">作者：{{ book.author }}</p>
            
            <!-- 图书详细信息列表 -->
            <div class="space-y-3 mb-6">
              <div class="flex">
                <span class="text-gray-500 w-20">出版社：</span>
                <span class="text-gray-900">{{ book.publisher }}</span>
              </div>
              <div class="flex">
                <span class="text-gray-500 w-20">出版年：</span>
                <span class="text-gray-900">{{ book.publishYear }}</span>
              </div>
              <div class="flex">
                <span class="text-gray-500 w-20">分类：</span>
                <span class="text-gray-900">{{ book.category }}</span>
              </div>
              <div class="flex">
                <span class="text-gray-500 w-20">ISBN：</span>
                <span class="text-gray-900">{{ book.isbn }}</span>
              </div>
              <div class="flex">
                <span class="text-gray-500 w-20">索书号：</span>
                <span class="text-gray-900">{{ book.location }}</span>
              </div>
              
              <!-- 馆藏数量信息 -->
              <div class="flex">
                <span class="text-gray-500 w-20">馆藏：</span>
                <span class="text-gray-900">
                  {{ book.availableCopies }}/{{ book.totalCopies }} 本可借
                </span>
              </div>
            </div>
            
            <!-- 借阅状态标签 -->
            <div class="mb-6">
              <div
                :class="[
                  'inline-flex items-center px-3 py-2 rounded-full text-sm font-medium',
                  book.availableCopies > 0 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                ]"
              >
                <span 
                  class="w-3 h-3 rounded-full mr-2" 
                  :class="book.availableCopies > 0 ? 'bg-green-400' : 'bg-red-400'"
                ></span>
                {{ book.availableCopies > 0 ? '可借阅' : '暂无可借' }}
              </div>
            </div>
            
          </div>
        </div>
        
        <!-- 图书简介区域 -->
        <div class="border-t border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-3">图书简介</h2>
          <p class="text-gray-700 leading-relaxed">{{ book.description }}</p>
        </div>
        
        <!-- 馆藏副本列表：显示所有副本的详细信息 -->
        <div class="border-t border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-3">馆藏信息</h2>
          <!-- 表头：显示各列标题 -->
          <div class="grid grid-cols-12 gap-2 px-2 py-2 bg-gray-50 text-sm text-gray-600">
            <div class="col-span-2">条码号</div>
            <div class="col-span-2">馆藏地</div>
            <div class="col-span-2">索书号</div>
            <div class="col-span-2">图书位置</div>
            <div class="col-span-2">状态</div>
            <div class="col-span-2">操作</div>
          </div>
          <!-- 副本列表：显示每个副本的具体信息 -->
          <div class="divide-y divide-gray-100">
            <div v-for="copy in book.copies" :key="copy.barcode" class="grid grid-cols-12 gap-2 px-2 py-3 items-center">
              <div class="col-span-2 font-mono text-xs md:text-sm">{{ copy.barcode }}</div>
              <div class="col-span-2 text-xs md:text-sm">{{ copy.location }}</div>
              <div class="col-span-2 text-xs md:text-sm">{{ book.location }}</div>
              <div class="col-span-2 text-xs md:text-sm">{{ copy.shelf }}</div>
              <div class="col-span-2">
                <div :class="copy.status === 'available' ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                  {{ copy.status === 'available' ? '可借' : '不可借' }}
                </div>
                <div v-if="copy.status !== 'available' && copy.returnDate" class="text-xs text-gray-500 mt-0.5">
                  应还: {{ copy.returnDate }}
                </div>
              </div>
              <div class="col-span-2">
                <button v-if="copy.status === 'available'" @click="openReservation(copy.barcode)" class="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">
                  预约
                </button>
                <span v-else class="text-gray-400 text-xs">不可预约</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 委托/预约区域：提供预约功能 -->
        <div class="border-t border-gray-200 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-3">委托/预约</h2>
          <!-- 预约表单：选择分馆、条码号和备注 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label class="block text-sm text-gray-600 mb-1">选择取书分馆</label>
              <select v-model="form.branch" class="w-full border rounded px-3 py-2">
                <option value="仓前校区">仓前校区</option>
                <option value="本部">本部</option>
                <option value="分馆A">分馆A</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">条码号（可选）</label>
              <input v-model="form.barcode" class="w-full border rounded px-3 py-2" placeholder="可指定不可借副本的条码号">
            </div>
            <div>
              <label class="block text-sm text-gray-600 mb-1">备注</label>
              <input v-model="form.notes" class="w-full border rounded px-3 py-2" placeholder="例如：希望尽快通知">
            </div>
          </div>
          <button @click="submitReservation" class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">提交预约</button>

          <!-- 我的预约：显示当前用户的预约记录 -->
          <div class="mt-6">
            <h3 class="font-semibold text-gray-900 mb-2">我的预约</h3>
            <div v-if="reservations.length === 0" class="text-gray-500 text-sm">暂无预约记录</div>
            <div v-else class="space-y-2">
              <div v-for="r in reservations" :key="r.id" class="flex items-center justify-between bg-gray-50 p-3 rounded">
                <div class="text-sm text-gray-700">条码：{{ r.barcode || '未指定' }} · 分馆：{{ r.pickupBranch }} · 状态：{{ r.status }}</div>
                <button v-if="r.status==='requested'" @click="cancelReservation(r.id)" class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 text-sm">取消</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 相关推荐：显示同类别的其他图书 -->
      <div class="mt-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">相关推荐</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
          <BookCard
            v-for="relatedBook in relatedBooks"
            :key="relatedBook.id"
            :book="relatedBook"
            @borrow="handleRelatedBorrow"
          />
        </div>
      </div>
    </div>

    <!-- 加载状态：显示加载中的提示 -->
    <div v-else class="flex items-center justify-center min-h-screen">
      <Loader2 class="w-8 h-8 animate-spin text-blue-600" />
      <span class="ml-2 text-gray-500">加载中...</span>
    </div>

    <!-- 底部导航：页面底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBooksStore } from '@/stores/books'
import { useAuthStore } from '@/stores/auth'
import { useRequestsStore } from '@/stores/requests'
import { ArrowLeft, Loader2 } from 'lucide-vue-next'
import BookCard from '@/components/BookCard.vue'
import BottomNav from '@/components/BottomNav.vue'

// 路由和状态管理：获取当前路由、路由器和存储实例
const route = useRoute()
const router = useRouter()
const bookStore = useBooksStore()
const userStore = useAuthStore()
const requestsStore = useRequestsStore()

// 响应式数据：图书详情、相关推荐、预约记录和表单数据
const book = ref(null) // 当前图书详情
const relatedBooks = ref([]) // 相关推荐图书列表
const reservations = ref([]) // 当前用户的预约记录
const form = ref({
  branch: '仓前校区', // 默认取书分馆
  barcode: '', // 可选的条码号
  notes: '' // 备注信息
})

// 状态管理：加载状态
const isLoading = ref(false) // 图书详情加载状态
const isReserving = ref(false) // 预约提交状态

// 计算属性：获取当前登录用户信息
const currentUser = computed(() => userStore.user)

/**
 * 加载图书详情
 * 获取图书基本信息、相关推荐和用户的预约记录
 */
const loadBookDetail = async () => {
  isLoading.value = true
  try {
    const bookId = route.params.id
    const bookData = await bookStore.getBookById(bookId)
    book.value = bookData
    
    // 加载相关推荐：同类别或同作者的其他图书
    if (bookStore.books.length === 0) bookStore.initialize()
    const books = bookStore.books
    relatedBooks.value = books.filter(b => 
      b.id !== bookId && 
      (b.category === bookData.category || b.author === bookData.author)
    ).slice(0, 4)
    
    // 加载预约记录
    await loadReservations()
  } catch (error) {
    console.error('加载图书详情失败:', error)
  } finally {
    isLoading.value = false
  }
}

/**
 * 加载用户预约记录
 * 获取当前用户对该图书的所有预约记录
 */
const loadReservations = async () => {
  try {
    const bookReservations = requestsStore.getByBook(book.value.id)
    if (currentUser.value) {
      // 过滤出当前用户的预约记录（即使接口未定义userId，但在创建时已存入）
      reservations.value = bookReservations.filter(r => r.userId === currentUser.value.id)
    } else {
      reservations.value = []
    }
  } catch (error) {
    console.error('加载预约记录失败:', error)
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.back()
}

/**
 * 处理图片加载错误
 * 当图书封面图片加载失败时显示默认占位图
 */
const handleImageError = (event) => {
  event.target.src = 'https://via.placeholder.com/300x400?text=暂无封面'
}

/**
 * 打开预约表单并预填条码号
 * @param {string} barcode - 要预约的图书条码号
 */
const openReservation = (barcode) => {
  form.value.barcode = barcode
}

/**
 * 提交预约申请
 * 创建新的图书预约记录
 */
const submitReservation = async () => {
  if (!form.value.branch) {
    alert('请选择取书分馆')
    return
  }
  
  isReserving.value = true
  try {
    const reservation = {
      bookId: book.value.id,
      bookTitle: book.value.title,
      barcode: form.value.barcode,
      pickupBranch: form.value.branch,
      notes: form.value.notes,
      userId: currentUser.value.id,
      userName: currentUser.value.name,
      status: 'requested',
      requestDate: new Date().toISOString()
    }
    
    requestsStore.createReservation(reservation)
    
    // 重置表单
    form.value = {
      branch: '仓前校区',
      barcode: '',
      notes: ''
    }
    
    // 重新加载预约记录
    await loadReservations()
    
    alert('预约提交成功！')
  } catch (error) {
    console.error('预约失败:', error)
    alert('预约失败，请重试')
  } finally {
    isReserving.value = false
  }
}

/**
 * 取消预约
 * @param {string} reservationId - 要取消的预约记录ID
 */
const cancelReservation = async (reservationId) => {
  try {
    requestsStore.cancelReservation(reservationId)
    await loadReservations()
    alert('预约已取消')
  } catch (error) {
    console.error('取消预约失败:', error)
    alert('取消预约失败')
  }
}

/**
 * 处理相关推荐图书的借阅操作
 * 跳转到对应图书的详情页面
 * @param {string} bookId - 相关图书的ID
 */
const handleRelatedBorrow = (bookId) => {
  router.push(`/book/${bookId}`)
  // 重新加载新图书详情
  setTimeout(() => {
    loadBookDetail()
  }, 100)
}

// 组件挂载时加载图书详情
onMounted(() => {
  loadBookDetail()
})
</script>
