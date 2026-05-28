/**
 * 主应用入口文件
 * 负责创建Vue应用实例并配置核心插件
 */

// 导入Vue核心函数
import { createApp } from 'vue'
// 导入Pinia状态管理库
import { createPinia } from 'pinia'
// 导入Vue Router路由配置
import router from './router'
// 导入根组件
import App from './App.vue'
// 导入全局样式文件
import './index.css'

// 创建Vue应用实例
const app = createApp(App)

// 注册Pinia状态管理插件
app.use(createPinia())
// 注册Vue Router路由插件
app.use(router)

// 挂载应用到DOM元素
app.mount('#app')