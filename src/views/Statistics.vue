<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <div class="w-full bg-white shadow-sm z-10">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button @click="$router.push('/')" class="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
            <ArrowLeft class="w-5 h-5" />
          </button>
          <h1 class="text-lg font-bold text-slate-800">数据统计</h1>
        </div>
        <span class="text-xs text-slate-400">数据来源：系统模拟</span>
      </div>
    </div>

    <div class="flex-1 p-6">
      <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-base font-bold text-slate-700 mb-4">图书分类占比</h2>
          <v-chart :option="categoryOption" autoresize style="height: 350px" />
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-base font-bold text-slate-700 mb-4">月度借阅量</h2>
          <v-chart :option="monthlyOption" autoresize style="height: 350px" />
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 lg:col-span-2">
          <h2 class="text-base font-bold text-slate-700 mb-4">热门图书 Top 10</h2>
          <v-chart :option="topBooksOption" autoresize style="height: 400px" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useBooksStore } from '@/stores/books'

use([CanvasRenderer, PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const booksStore = useBooksStore()

const categoryOption = computed(() => {
  const count: Record<string, number> = {}
  booksStore.books.forEach(book => {
    count[book.category] = (count[book.category] || 0) + 1
  })
  const data = Object.entries(count).map(([name, value]) => ({ name, value }))

  return {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { color: '#64748b' } },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['40%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 3 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      data,
    }],
  }
})

const monthlyOption = computed(() => {
  const months: string[] = []
  const values: number[] = []
  const now = new Date()
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    months.push(`${d.getMonth() + 1}月`)
    values.push(Math.floor(Math.random() * 40) + 30)
  }

  return {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b' },
    },
    series: [{
      type: 'bar',
      data: values,
      barWidth: '50%',
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: '#6366f1',
      },
    }],
  }
})

const topBooksOption = computed(() => {
  const titles = booksStore.books.map(b => b.title)
  const books = [
    { title: '深入理解计算机系统', count: 87 },
    { title: '活着', count: 76 },
    { title: '红楼梦', count: 68 },
    { title: '算法导论', count: 59 },
    { title: '人类简史', count: 52 },
    { title: '百年孤独', count: 45 },
    { title: '三体', count: 41 },
    { title: '围城', count: 36 },
    { title: '数据结构与算法', count: 30 },
    { title: '计算机网络', count: 25 },
  ]

  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: { color: '#64748b' },
    },
    yAxis: {
      type: 'category',
      data: books.map(b => b.title).reverse(),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#334155' },
    },
    series: [{
      type: 'bar',
      data: books.map(b => b.count).reverse(),
      barWidth: '60%',
      itemStyle: {
        borderRadius: [0, 6, 6, 0],
        color: '#10b981',
      },
    }],
  }
})
</script>
