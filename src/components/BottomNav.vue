<template>
  <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
    <div class="flex justify-around items-center h-16">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center justify-center flex-1 h-full text-gray-600 hover:text-blue-600 transition-colors"
        :class="{ 'text-blue-600': $route.path === item.path }"
      >
        <component 
          :is="item.icon" 
          class="w-6 h-6 mb-1"
          :class="{ 'text-blue-600': $route.path === item.path }"
        />
        <span class="text-xs">{{ item.name }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Home, Search, Clock, User } from 'lucide-vue-next'

interface NavItem {
  name: string
  path: string
  icon: any
}

const navItems: NavItem[] = [
  { name: '首页', path: '/mobile', icon: Home },
  { name: '搜索', path: '/search', icon: Search },
  { name: '历史', path: '/history', icon: Clock },
  { name: '我的', path: '/mobile/profile', icon: User }
]
</script>

<style scoped>
/* 为底部导航栏添加安全区域适配 */
@supports (padding-bottom: env(safe-area-inset-bottom)) {
  .fixed {
    padding-bottom: env(safe-area-inset-bottom);
  }
}
</style>
