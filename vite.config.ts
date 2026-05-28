/**
 * Vite 配置文件
 * 
 * 这个配置文件定义了项目的构建和开发服务器设置
 * 主要包含以下功能：
 * 
 * 1. 路径别名配置 - 将 @ 映射到 src 目录
 * 2. 多入口配置 - 支持 PC 端和移动端双入口
 * 3. Vue 插件支持 - 使用 Vue3 单文件组件
 * 4. TypeScript 路径映射支持
 * 5. Trae AI 徽章插件（仅生产环境）
 * 
 * 项目结构：
 * - main: index.html -> PC 端应用入口
 * - mobile: mobile.html -> 移动端应用入口
 * 
 * @author 图书管理系统开发团队
 * @description Vite 构建工具配置文件
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tsconfigPaths from "vite-tsconfig-paths";
import { traeBadgePlugin } from 'vite-plugin-trae-solo-badge';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  // 路径解析配置
  resolve: {
    alias: {
      // 配置 @ 别名指向 src 目录，方便在代码中使用 @/components 这样的路径
      '@': path.resolve(__dirname, './src')
    }
  },
  
  // 构建配置
  build: {
    // 生成隐藏的 source map 文件，用于生产环境调试但不暴露源代码
    sourcemap: 'hidden',
    
    // Rollup 打包配置
    rollupOptions: {
      // 多入口配置，支持同时构建 PC 端和移动端
      input: {
        // PC 端入口文件，对应 index.html
        main: path.resolve(__dirname, 'index.html'),
        // 移动端入口文件，对应 mobile.html  
        mobile: path.resolve(__dirname, 'mobile.html')
      }
    }
  },
  
  // 插件配置
  plugins: [
    // Vue3 插件，支持 .vue 单文件组件
    vue(),
    
    // Trae AI 徽章插件配置（仅在生产环境显示）
    traeBadgePlugin({
      variant: 'dark',                    // 深色主题
      position: 'bottom-right',          // 显示在右下角
      prodOnly: true,                    // 仅生产环境显示
      clickable: true,                   // 可点击
      clickUrl: 'https://www.trae.ai/solo?showJoin=1', // 点击跳转链接
      autoTheme: true,                   // 自动主题适配
      autoThemeTarget: '#app'            // 主题适配目标元素
    }),
    
    // TypeScript 配置路径插件，支持 tsconfig.json 中的路径映射
    tsconfigPaths()
  ],
})
