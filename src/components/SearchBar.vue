<template>
  <div class="search-container bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 py-4">
      <div class="flex items-center gap-4">
        <!-- 搜索输入框 -->
        <div class="flex-1 relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="h-5 w-5 text-gray-400" />
          </div>
          <input v-model="searchValue" type="text" placeholder="搜索书名、作者或ISBN..."
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            @input="handleSearch" @keyup.enter="handleSearchEnter">
          <!-- 清除按钮 -->
          <button v-if="searchValue" @click="clearSearch" class="absolute inset-y-0 right-0 pr-3 flex items-center">
            <X class="h-4 w-4 text-gray-400 hover:text-gray-600" />
          </button>
        </div>

        <!-- 扫一扫按钮（已移除，提高搜索专注度） -->
      </div>

      <!-- 搜索建议 -->
      <div v-if="showSuggestions && suggestions.length > 0"
        class="mt-2 bg-white border border-gray-200 rounded-lg shadow-lg">
        <ul class="py-1">
          <li v-for="(suggestion, index) in suggestions" :key="index" @click="selectSuggestion(suggestion)"
            class="px-4 py-2 hover:bg-gray-100 cursor-pointer">
            {{ suggestion }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, X } from 'lucide-vue-next'
import { useBooksStore } from '@/stores/books'
import { debounce } from '@/utils'

const router = useRouter()
const booksStore = useBooksStore()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const defaultSuggestions = ['深入理解计算机系统', '算法导论', '红楼梦', '活着', '人工智能', '数据结构']

// 状态
const searchValue = ref('')
const showSuggestions = ref(false)
const isSearching = ref(false)
const suggestions = ref<string[]>(defaultSuggestions)

async function loadSuggestions(query: string) {
  if (!query.trim()) {
    suggestions.value = defaultSuggestions
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/search/suggestions?q=${encodeURIComponent(query)}`)
    if (!response.ok) {
      throw new Error('加载搜索建议失败')
    }

    suggestions.value = await response.json()
  } catch (error) {
    console.error('加载搜索建议失败，已降级到默认建议:', error)
    suggestions.value = defaultSuggestions.filter(item =>
      item.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 6)
  }
}

// 防抖搜索
const debouncedSearch = debounce((value: string) => {
  loadSuggestions(value)
  if (value.trim()) {
    performSearch(value)
  } else {
    booksStore.searchBooks('')
  }
}, 300)

// 处理搜索输入
function handleSearch() {
  showSuggestions.value = true
  debouncedSearch(searchValue.value)
}

// 处理回车搜索
function handleSearchEnter() {
  showSuggestions.value = false
  if (searchValue.value.trim()) {
    performSearch(searchValue.value)
    navigateToSearch()
  }
}

// 选择搜索建议
function selectSuggestion(suggestion: string) {
  searchValue.value = suggestion
  showSuggestions.value = false
  performSearch(suggestion)
  navigateToSearch()
}

// 执行搜索
async function performSearch(query: string) {
  isSearching.value = true
  try {
    await booksStore.searchBooks(query)
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    isSearching.value = false
  }
}

// 清除搜索
function clearSearch() {
  searchValue.value = ''
  showSuggestions.value = false
  suggestions.value = defaultSuggestions
  booksStore.searchBooks('')
}

// 跳转到搜索页面
function navigateToSearch() {
  if (router.currentRoute.value.path !== '/search') {
    router.push('/search')
  }
}

// 处理扫一扫
// 已移除扫一扫逻辑

// 点击外部关闭建议
function handleClickOutside(event: Event) {
  const target = event.target as HTMLElement
  if (!target.closest('.search-container')) {
    showSuggestions.value = false
  }
}

// 监听点击外部事件
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.search-container {
  position: relative;
}
</style>
