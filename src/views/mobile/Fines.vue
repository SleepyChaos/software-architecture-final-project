<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- 顶部标题栏：显示页面标题和返回链接 -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-semibold text-gray-900">滞纳金缴纳</h1>
        <router-link to="/mobile/profile" class="text-blue-600">返回我的</router-link>
      </div>
    </div>

    <!-- 主要内容区域：显示逾期图书列表 -->
    <div class="max-w-7xl mx-auto px-4 py-6">
      <!-- 空状态：当没有逾期记录时显示 -->
      <div v-if="overdue.length === 0" class="bg-white rounded-lg p-8 text-center">
        <p class="text-gray-500">暂无逾期记录</p>
      </div>

      <!-- 逾期列表：显示所有逾期的借阅记录 -->
      <div v-else class="space-y-4">
        <div
          v-for="rec in overdue"
          :key="rec.id"
          class="bg-white rounded-lg p-4 shadow-sm flex items-center justify-between"
        >
          <!-- 左侧：图书信息和逾期详情 -->
          <div class="flex items-center gap-4">
            <img :src="rec.bookCover" class="w-12 h-16 object-cover rounded" />
            <div>
              <div class="font-semibold text-gray-900">{{ rec.bookTitle }}</div>
              <div class="text-sm text-gray-600">应还：{{ rec.dueDate }}</div>
              <div class="text-sm text-red-600">逾期：{{ getOverdueDays(rec.dueDate) }} 天</div>
            </div>
          </div>
          <!-- 右侧：滞纳金金额和缴纳按钮 -->
          <div class="text-right">
            <div class="text-lg font-bold text-gray-900">￥{{ calcFine(rec) }}</div>
            <button
              class="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              @click="payFine(rec)"
            >
              立即缴纳
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航：页面底部导航栏 -->
    <BottomNav />
  </div>
</template>

<script setup lang="ts">
import BottomNav from '@/components/BottomNav.vue'
import { useLoansStore, type BorrowRecord } from '@/stores/loans'

// 状态管理：借阅记录存储实例
const loansStore = useLoansStore()

// 计算属性：获取所有逾期的借阅记录
const overdue = loansStore.overdueBooks

/**
 * 计算逾期天数
 * 根据应还日期计算当前逾期天数
 * @param {string} dateStr - 应还日期字符串
 * @returns {number} - 逾期天数（负数表示未逾期）
 */
function getOverdueDays(dateStr: string) {
  const due = new Date(dateStr).getTime()
  const now = new Date().getTime()
  return Math.max(0, Math.floor((now - due) / (1000*60*60*24)))
}

/**
 * 计算滞纳金
 * 根据逾期天数计算应缴纳的滞纳金（每天0.5元）
 * @param {BorrowRecord} rec - 借阅记录对象
 * @returns {string} - 格式化的滞纳金金额
 */
function calcFine(rec: BorrowRecord) {
  return (getOverdueDays(rec.dueDate) * 0.5).toFixed(2)
}

/**
 * 缴纳滞纳金
 * 模拟支付接口，支付成功后自动归还图书
 * @param {BorrowRecord} rec - 要处理的借阅记录
 */
async function payFine(rec: BorrowRecord) {
  // 模拟支付接口：支付后自动归还
  await loansStore.returnBook(rec.id)
  alert('支付成功，已完成归还')
}
</script>
