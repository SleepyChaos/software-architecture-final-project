<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部搜索栏：提供搜索输入功能 -->
    <SearchBar />
    
    <!-- 主要内容：搜索结果展示区域 -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 顶部筛选工具条：提供筛选和排序选项 -->
      <div class="flex items-center gap-3 mb-4">
        <button
          :class="[
            'px-3 py-1 rounded-full text-sm',
            onlyAvailable ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
          @click="toggleAvailable"
        >
          仅看可借
        </button>
        <select v-model="sortKey" class="px-3 py-1 border rounded bg-white text-sm">
          <option value="default">综合排序</option>
          <option value="year_desc">出版年 (新→旧)</option>
          <option value="year_asc">出版年 (旧→新)</option>
          <option value="title_asc">题名 (A→Z)</option>
          <option value="available">库存数量</option>
        </select>
      </div>
      
      <!-- 分类筛选：提供图书分类筛选功能 -->
      <div class="mb-6">
        <h3 class="text-lg font-medium text-gray-900 mb-3">图书分类</h3>
        <div class="flex flex-wrap gap-2">
          <button
            @click="selectCategory('')"
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium transition-colors',
              selectedCategory === '' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            全部分类
          </button>
          <button
            v-for="category in booksStore.categories"
            :key="category.id"
            @click="selectCategory(category.name)"
            :class="[
              'px-3 py-1 rounded-full text-sm font-medium transition-colors',
              selectedCategory === category.name 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ category.name }}
          </button>
        </div>
      </div>

      <!-- 搜索结果统计：显示搜索结果数量 -->
      <div class="mb-4">
        <p class="text-gray-600">
          找到 <span class="font-medium text-gray-900">{{ filteredBooks.length }}</span> 本图书
          <span v-if="searchQuery" class="ml-2">
            搜索词："<span class="font-medium">{{ searchQuery }}</span>"
          </span>
        </p>
      </div>

      <!-- 加载状态：显示搜索中的加载提示 -->
      <div v-if="booksStore.isLoading" class="text-center py-12">
        <Loader2 class="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
        <p class="text-gray-500">搜索中...</p>
      </div>

      <!-- 无结果：当没有搜索结果时显示 -->
      <div v-else-if="filteredBooks.length === 0" class="text-center py-12">
        <Search class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">未找到相关图书</h3>
        <p class="text-gray-500 mb-4">试试其他关键词或浏览推荐图书</p>
        <button
          @click="clearFilters"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          清除筛选
        </button>
      </div>

      <!-- 搜索结果：显示筛选后的图书列表 -->
      <div v-else class="space-y-4">
        <BookCard
          v-for="book in sortedBooks"
          :key="book.id"
          :book="book"
          @borrow="handleBorrow"
        />
      </div>

      <!-- 推荐图书（当没有搜索结果时）：显示热门推荐图书 -->
      <div v-if="!searchQuery && filteredBooks.length === 0" class="mt-12">
        <h3 class="text-lg font-medium text-gray-900 mb-4">热门推荐</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <BookCard
            v-for="book in recommendedBooks"
            :key="book.id"
            :book="book"
            @borrow="handleBorrow"
          />
        </div>
      </div>
    </div>
    
    <!-- 底部导航：页面底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Search, Loader2 } from 'lucide-vue-next'
import SearchBar from '@/components/SearchBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import BookCard from '@/components/BookCard.vue'
import { useBooksStore } from '@/stores/books'
import type { Book } from '@/stores/books'

// 状态管理：图书存储实例
const booksStore = useBooksStore()

// 计算属性：搜索相关数据
const filteredBooks = computed(() => booksStore.filteredBooks) // 筛选后的图书列表
const onlyAvailable = ref(false) // 仅显示可借图书开关
const sortKey = ref<'default' | 'available' | 'year_desc' | 'year_asc' | 'title_asc'>('default') // 排序方式

// 计算属性：排序后的图书列表
const sortedBooks = computed(() => {
  let list = filteredBooks.value
  if (onlyAvailable.value) {
    list = list.filter(b => b.availableCopies > 0)
  }
  switch (sortKey.value) {
    case 'available':
      return [...list].sort((a,b) => b.availableCopies - a.availableCopies)
    case 'year_desc':
      return [...list].sort((a,b) => b.publishYear - a.publishYear)
    case 'year_asc':
      return [...list].sort((a,b) => a.publishYear - b.publishYear)
    case 'title_asc':
      return [...list].sort((a,b) => a.title.localeCompare(b.title, 'zh-CN'))
    default:
      return list
  }
})

// 计算属性：搜索相关状态
const searchQuery = computed(() => booksStore.searchQuery) // 当前搜索关键词
const selectedCategory = computed(() => booksStore.selectedCategory) // 选中的分类
const recommendedBooks = computed(() => booksStore.recommendedBooks) // 推荐图书列表

// 组件挂载时初始化图书数据
onMounted(() => {
  booksStore.initialize()
})

/**
 * 选择分类
 * 按指定分类筛选图书
 * @param {string} category - 分类名称
 */
function selectCategory(category: string) {
  booksStore.filterByCategory(category)
}

/**
 * 清除筛选条件
 * 重置搜索关键词和分类筛选
 */
function clearFilters() {
  booksStore.searchBooks('')
  booksStore.filterByCategory('')
}

/**
 * 处理图书借阅
 * 处理用户点击借阅按钮的操作
 * @param {Book} book - 要借阅的图书对象
 */
function handleBorrow(book: Book) {
  console.log('借阅图书:', book.title)
}

/**
 * 切换"仅看可借"开关
 * 控制是否只显示可借阅的图书
 */
function toggleAvailable() {
  onlyAvailable.value = !onlyAvailable.value
}
</script>
