import { createRouter, createWebHashHistory } from 'vue-router'
import HomeMobile from '@/views/mobile/HomeMobile.vue'
import Search from '@/views/Search.vue'
import BookDetail from '@/views/BookDetail.vue'
import History from '@/views/History.vue'
import ProfileMobile from '@/views/mobile/ProfileMobile.vue'
import Fines from '@/views/mobile/Fines.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/mobile.html', redirect: '/' },
    { path: '/', name: 'MHome', component: HomeMobile, meta: { title: '首页' } },
    { path: '/mobile', component: HomeMobile, meta: { title: '首页' } },
    { path: '/search', name: 'MSearch', component: Search, meta: { title: '搜索图书' } },
    { path: '/book/:id', name: 'MBookDetail', component: BookDetail, meta: { title: '图书详情' } },
    { path: '/history', name: 'MHistory', component: History, meta: { title: '借阅历史' } },
    { path: '/profile', name: 'MProfile', component: ProfileMobile, meta: { title: '我的' } },
    { path: '/mobile/profile', component: ProfileMobile, meta: { title: '我的' } },
    { path: '/fines', name: 'MFines', component: Fines, meta: { title: '滞纳金' } },
  ]
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 用户端` : '用户端'
  next()
})

export default router
