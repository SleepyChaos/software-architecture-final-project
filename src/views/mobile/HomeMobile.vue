<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部导航栏：显示系统标题和用户入口 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-semibold text-gray-900">图书借阅系统</h1>
        <router-link to="/mobile/profile" class="text-blue-600">我的</router-link>
      </div>
    </div>

    <!-- 搜索栏：提供图书搜索功能 -->
    <SearchBar />

    <!-- 主要内容区域：功能入口和推荐图书 -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 功能入口：四个主要功能的快速入口 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <!-- 搜索图书入口 -->
        <router-link to="/search" class="bg-white rounded-lg p-4 shadow-sm text-center">
          <span class="text-sm text-gray-700">搜索图书</span>
        </router-link>
        <!-- 借阅历史入口 -->
        <router-link to="/history" class="bg-white rounded-lg p-4 shadow-sm text-center">
          <span class="text-sm text-gray-700">借阅历史</span>
        </router-link>
        <!-- 我的借阅入口 -->
        <router-link to="/mobile/profile" class="bg-white rounded-lg p-4 shadow-sm text-center">
          <span class="text-sm text-gray-700">我的借阅</span>
        </router-link>
        <!-- 滞纳金缴纳入口 -->
        <router-link to="/fines" class="bg-white rounded-lg p-4 shadow-sm text-center">
          <span class="text-sm text-gray-700">滞纳金缴纳</span>
        </router-link>
      </div>

      <!-- 热门推荐：显示推荐图书列表 -->
      <h2 class="text-xl font-semibold text-gray-900 mb-4">热门推荐</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <BookCard
          v-for="book in booksStore.recommendedBooks"
          :key="book.id"
          :book="book"
        />
      </div>
    </div>

    <!-- 底部导航：移动端底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import BottomNav from '@/components/BottomNav.vue'
import BookCard from '@/components/BookCard.vue'
import { useBooksStore } from '@/stores/books'

// 状态管理：图书存储实例
const booksStore = useBooksStore()

/**
 * 组件挂载时初始化图书数据
 * 加载推荐图书等基础数据
 */
onMounted(() => {
  booksStore.initialize()
})
</script>
