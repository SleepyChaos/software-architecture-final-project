/**
 * Vue Router路由配置文件
 * 定义应用的所有路由规则和导航守卫
 */

// 导入Vue Router核心函数和类型
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 页面组件导入
import Login from '@/views/Login.vue'
import Home from '@/views/Home.vue'
import HomeMobile from '@/views/mobile/HomeMobile.vue'
import ProfileMobile from '@/views/mobile/ProfileMobile.vue'
import Fines from '@/views/mobile/Fines.vue'
import Search from '@/views/Search.vue'
import BookDetail from '@/views/BookDetail.vue'
import History from '@/views/History.vue'
import Profile from '@/views/Profile.vue'
import Borrow from '@/views/Borrow.vue'
import Return from '@/views/Return.vue'
// import Renew from '@/views/Renew.vue'

/**
 * 路由配置数组
 * 定义应用中所有可用的路由规则
 */
const routes: RouteRecordRaw[] = [
  /**
   * 登录页面路由
   * 用户身份验证入口
   */
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  /**
   * 桌面端首页路由
   * 图书管理系统主界面
   */
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  /**
   * 移动端首页路由
   * 适配移动设备的图书管理界面
   */
  {
    path: '/mobile',
    name: 'HomeMobile',
    component: HomeMobile,
    meta: { title: '首页' }
  },
  /**
   * 图书借阅页面路由
   * 需要用户登录才能访问
   */
  {
    path: '/borrow',
    name: 'Borrow',
    component: Borrow,
    meta: { title: '借阅图书', authRequired: true }
  },
  /**
   * 图书归还页面路由
   * 处理图书归还功能
   */
  {
    path: '/return',
    name: 'Return',
    component: Return,
    meta: { title: '归还图书', authRequired: false }
  },
  /**
   * 图书搜索页面路由
   * 提供图书检索功能
   */
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { title: '搜索图书' }
  },
  /**
   * 图书详情页面路由
   * 显示单本图书的详细信息
   */
  {
    path: '/book/:id',
    name: 'BookDetail',
    component: BookDetail,
    meta: { title: '图书详情' }
  },
  /**
   * 借阅历史页面路由
   * 展示用户的借阅记录
   */
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { title: '借阅历史' }
  },
  /**
   * 图书续借页面路由
   * 需要用户登录才能访问
   */
  {
    path: '/renew',
    name: 'Renew',
    component: History,
    meta: { title: '续借', authRequired: true }
  },
  /**
   * 移动端个人中心路由
   * 移动端用户个人信息管理
   */
  {
    path: '/mobile/profile',
    name: 'ProfileMobile',
    component: ProfileMobile,
    meta: { title: '个人中心', authRequired: true }
  },
  /**
   * 滞纳金缴纳页面路由
   * 处理逾期罚金支付
   */
  {
    path: '/fines',
    name: 'Fines',
    component: Fines,
    meta: { title: '滞纳金缴纳', authRequired: true }
  },
  /**
   * 桌面端个人中心路由
   * 桌面端用户个人信息管理
   */
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '个人中心', authRequired: true }
  }
]

/**
 * 创建Vue Router实例
 * 配置历史模式和路由规则
 */
const router = createRouter({
  // 使用HTML5历史模式，创建干净的URL
  history: createWebHistory(),
  // 应用路由配置
  routes
})

/**
 * 全局路由守卫
 * 处理页面标题设置和登录权限验证
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题：如果路由定义了标题则追加系统名称，否则使用默认标题
  document.title = to.meta.title ? `${to.meta.title} - 图书管理系统` : '图书管理系统'

  // 登录权限验证
  const isLoggedIn = !!localStorage.getItem('user')  // 检查本地存储中是否存在用户信息
  const needAuth = (to.meta as any)?.authRequired    // 获取当前路由是否需要认证
  
  // 如果需要认证且用户未登录，则重定向到登录页面
  if (needAuth && !isLoggedIn) {
    next({ name: 'Login' })
  } else {
    // 否则正常导航
    next()
  }
})

// 导出配置完成的路由实例
export default router
