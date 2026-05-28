<template>
  <!-- 主应用容器：设置最小高度和背景色，确保页面占满视口 -->
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 路由视图：根据当前路由动态渲染对应的页面组件 -->
    <router-view />
  </div>
</template>

<script setup lang="ts">
/**
 * 主应用根组件
 * 作为整个应用的入口，提供基础布局和路由渲染功能
 */
</script>

<style scoped>
/* 应用根元素样式：设置现代系统字体族 */
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style>