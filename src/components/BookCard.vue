<template>
  <div class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
    <div class="flex gap-4">
      <!-- 图书封面 -->
      <router-link :to="`/book/${book.id}`" class="flex-shrink-0">
        <img 
          :src="book.coverImageUrl" 
          :alt="book.title"
          class="w-20 h-28 object-cover rounded-md"
          @error="handleImageError"
        >
      </router-link>
      
      <!-- 图书信息 -->
      <router-link :to="`/book/${book.id}`" class="flex-1 min-w-0 block">
        <h3 class="text-lg font-semibold text-gray-900 truncate">{{ book.title }}</h3>
        <p class="text-sm text-gray-600 mt-1">作者：{{ book.author }}</p>
        <p class="text-sm text-gray-500 mt-1">出版社：{{ book.publisher }}</p>
        <p class="text-sm text-gray-500">索书号：{{ book.location }}</p>
        
        <!-- 可借状态 -->
        <div class="mt-2">
          <span 
            :class="[
              'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
              book.availableCopies > 0 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            ]"
          >
            <span class="w-2 h-2 rounded-full mr-1" :class="book.availableCopies > 0 ? 'bg-green-400' : 'bg-red-400'"></span>
            {{ book.availableCopies > 0 ? `可借 ${book.availableCopies}/${book.totalCopies} 本` : '暂无库存' }}
          </span>
        </div>

      </router-link>
      
      <!-- 操作按钮 -->
      <div class="flex-shrink-0 flex flex-col justify-center">
        <button 
          @click="$router.push(`/book/${book.id}`)"
          class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
        >
          查看详情
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { MapPin } from 'lucide-vue-next'
import type { Book } from '@/stores/books'

interface Props {
  book: Book
}

const props = defineProps<Props>()
const router = useRouter()

// 处理图片加载错误
function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement
  target.src = `https://via.placeholder.com/80x112/9CA3AF/FFFFFF?text=${encodeURIComponent(props.book.title.slice(0, 2))}`
}
</script>
