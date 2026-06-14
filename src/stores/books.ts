/**
 * 图书管理状态存储模块
 * 管理图书信息、分类、搜索过滤和推荐功能
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/utils/http'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 图书副本信息接口
 * 描述每册图书的具体信息和状态
 */
export interface BookCopy {
  barcode: string      // 图书条码号
  location: string     // 馆藏地，例如 "仓前校区", "本部"
  shelf: string        // 图书位置，例如 "3楼A区"
  status: 'available' | 'borrowed' | 'unavailable'  // 副本状态
  returnDate?: string  // 应还日期（仅当状态为borrowed时有效）
}

/**
 * 图书信息接口
 * 描述图书的基本信息和馆藏情况
 */
export interface Book {
  id: string              // 图书唯一标识
  isbn: string            // ISBN编号
  title: string           // 图书标题
  author: string          // 作者
  publisher: string       // 出版社
  publishYear: number     // 出版年份
  category: string        // 图书分类
  coverImageUrl: string   // 封面图片URL
  location: string        // 图书索书号
  totalCopies: number     // 总副本数
  availableCopies: number // 可借副本数
  barcodes: string[]      // 每册图书的条码号列表（用于展示馆藏副本与预约）
  copies: BookCopy[]     // 详细副本信息
  description: string     // 图书描述
}

/**
 * 图书分类接口
 * 描述图书分类信息
 */
export interface Category {
  id: string          // 分类唯一标识
  name: string        // 分类名称
  description: string // 分类描述
}

/**
 * 图书管理状态存储
 * 提供图书搜索、过滤、分类管理等功能
 */
export const useBooksStore = defineStore('books', () => {
  // 状态定义
  const books = ref<Book[]>([])                    // 图书列表
  const remoteBooks = ref<Book[] | null>(null)      // 后端检索结果
  const categories = ref<Category[]>([])         // 图书分类列表
  const isLoading = ref(false)                     // 加载状态
  const error = ref<string | null>(null)         // 错误信息
  const searchQuery = ref('')                     // 搜索关键词
  const selectedCategory = ref('')               // 选中的分类

  /**
   * 计算属性：过滤后的图书列表
   * 根据搜索词和分类进行双重过滤
   */
  const filteredBooks = computed(() => {
    let result = remoteBooks.value ?? books.value

    // 按搜索词过滤（标题、作者、ISBN）
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(book =>
        book.title.toLowerCase().includes(query) ||
        book.author.toLowerCase().includes(query) ||
        book.isbn.includes(query)
      )
    }

    // 按分类过滤
    if (selectedCategory.value) {
      result = result.filter(book => book.category === selectedCategory.value)
    }

    return result
  })

  /**
     * 计算属性：可借图书列表
     * 过滤出所有可借副本数大于0的图书
     */
  const availableBooks = computed(() =>
    books.value.filter(book => book.availableCopies > 0)
  )

  /**
   * 计算属性：推荐图书列表
   * 返回前6本可借阅的图书作为推荐
   */
  const recommendedBooks = computed(() => {
    // 返回推荐图书（这里模拟返回前6本可借阅的图书）
    return availableBooks.value.slice(0, 6)
  })

  /**
     * 辅助函数：生成图书副本信息
     * 根据条码号和可借数量生成详细的副本列表
     * @param barcodes - 图书条码号列表
     * @param availableCount - 可借副本数量
     * @returns 图书副本信息数组
     */
  function generateCopies(barcodes: string[], availableCount: number): BookCopy[] {
    return barcodes.map((code, idx) => {
      // 判断副本是否可借
      const isAvailable = idx < availableCount
      const status = isAvailable ? 'available' : 'borrowed'

      // 随机分配馆藏地和书架位置
      const branch = idx % 2 === 0 ? '仓前校区' : '本部'
      const shelf = idx % 2 === 0 ? '3楼A区' : '2楼C区'

      // 为已借出的副本生成应还日期
      let returnDate
      if (!isAvailable) {
        const days = Math.floor(Math.random() * 30) + 1  // 随机1-30天
        const date = new Date()
        date.setDate(date.getDate() + days)
        returnDate = date.toISOString().split('T')[0]  // 格式化为YYYY-MM-DD
      }

      return {
        barcode: code,
        location: branch,
        shelf: shelf,
        status,
        returnDate
      }
    })
  }

  /**
     * 生成模拟图书数据
     * 创建包含多种类型图书的示例数据集
     */
  function generateMockBooks() {
    // 模拟图书数据数组
    const mockBooks: Book[] = [
      {
        id: '1',
        isbn: '9787111421900',
        title: '深入理解计算机系统',
        author: 'Randal E. Bryant',
        publisher: '机械工业出版社',
        publishYear: 2016,
        category: '科技',
        coverImageUrl: 'https://placehold.co/200x300/4F46E5/FFFFFF?text=CSAPP',
        location: 'TP3-42',
        totalCopies: 5,
        availableCopies: 2,
        barcodes: ['01755621', '01755622', '01755623', '01755624', '01755625'],
        copies: generateCopies(['01755621', '01755622', '01755623', '01755624', '01755625'], 2),
        description: '从程序员的视角详细阐述计算机系统的本质概念，并展示这些概念如何实实在在地影响应用程序的正确性、性能和实用性。'
      },
      {
        id: '2',
        isbn: '9787115543739',
        title: '算法导论',
        author: 'Thomas H. Cormen',
        publisher: '机械工业出版社',
        publishYear: 2020,
        category: '科技',
        coverImageUrl: 'https://placehold.co/200x300/059669/FFFFFF?text=CLRS',
        location: 'TP301.6-51',
        totalCopies: 3,
        availableCopies: 1,
        barcodes: ['01755630', '01755631', '01755632'],
        copies: generateCopies(['01755630', '01755631', '01755632'], 1),
        description: '全面介绍了计算机算法。对每一个算法的分析既易于理解又十分有趣，并保持了数学严谨性。'
      },
      {
        id: '3',
        isbn: '9787020002207',
        title: '红楼梦',
        author: '曹雪芹',
        publisher: '人民文学出版社',
        publishYear: 2018,
        category: '文学',
        coverImageUrl: 'https://placehold.co/200x300/DC2626/FFFFFF?text=红楼梦',
        location: 'I242.4-51',
        totalCopies: 10,
        availableCopies: 5,
        barcodes: ['01755640', '01755641', '01755642', '01755643', '01755644', '01755645', '01755646', '01755647', '01755648', '01755649'],
        copies: generateCopies(['01755640', '01755641', '01755642', '01755643', '01755644', '01755645', '01755646', '01755647', '01755648', '01755649'], 5),
        description: '中国古代章回体长篇小说，中国古典四大名著之一。'
      },
      {
        id: '4',
        isbn: '9787020139590',
        title: '活着',
        author: '余华',
        publisher: '作家出版社',
        publishYear: 2012,
        category: '文学',
        coverImageUrl: 'https://placehold.co/200x300/7C2D12/FFFFFF?text=活着',
        location: 'I247.5-42',
        totalCopies: 8,
        availableCopies: 3,
        barcodes: ['01755650', '01755651', '01755652', '01755653', '01755654', '01755655', '01755656', '01755657'],
        copies: generateCopies(['01755650', '01755651', '01755652', '01755653', '01755654', '01755655', '01755656', '01755657'], 3),
        description: '讲述了农村人福贵悲惨的人生遭遇。'
      },
      {
        id: '5',
        isbn: '9787508695472',
        title: '人类简史',
        author: '尤瓦尔·赫拉利',
        publisher: '中信出版社',
        publishYear: 2017,
        category: '历史',
        coverImageUrl: 'https://placehold.co/200x300/92400E/FFFFFF?text=人类简史',
        location: 'K02-51',
        totalCopies: 6,
        availableCopies: 2,
        barcodes: ['01755670', '01755671', '01755672', '01755673', '01755674', '01755675'],
        copies: generateCopies(['01755670', '01755671', '01755672', '01755673', '01755674', '01755675'], 2),
        description: '从十万年前有生命迹象开始到21世纪资本、科技交织的人类发展史。'
      },
      {
        id: '6',
        isbn: '9787544291170',
        title: '百年孤独',
        author: '加西亚·马尔克斯',
        publisher: '南海出版公司',
        publishYear: 2017,
        category: '文学',
        coverImageUrl: 'https://placehold.co/200x300/1F2937/FFFFFF?text=百年孤独',
        location: 'I775.4-51',
        totalCopies: 4,
        availableCopies: 0,
        barcodes: ['01755680', '01755681', '01755682', '01755683'],
        copies: generateCopies(['01755680', '01755681', '01755682', '01755683'], 0),
        description: '魔幻现实主义文学的代表作，描写了布恩迪亚家族七代人的传奇故事。'
      }
    ]

    /**
         * 模拟分类数据
         * 定义图书的主要分类及其描述
         */
    const mockCategories: Category[] = [
      { id: '1', name: '文学', description: '小说、诗歌、散文等文学作品' },
      { id: '2', name: '科技', description: '科学技术类图书' },
      { id: '3', name: '历史', description: '历史相关图书' },
      { id: '4', name: '艺术', description: '艺术类图书' },
      { id: '5', name: '教育', description: '教育学习类图书' }
    ]

    // 将模拟数据赋值给状态变量
    books.value = mockBooks
    categories.value = mockCategories
  }

  /**
     * 搜索图书函数
     * 根据关键词搜索图书，更新搜索状态
     * @param query - 搜索关键词
     */
  async function searchBooks(query: string) {
    // 更新搜索关键词
    searchQuery.value = query
    // 设置加载状态
    isLoading.value = true
    error.value = null

    try {
      const normalizedQuery = query.trim()
      if (!normalizedQuery) {
        remoteBooks.value = null
        return
      }

      const response = await apiFetch(`/books/search?q=${encodeURIComponent(normalizedQuery)}`)
      if (!response.ok) {
        throw new Error('后端搜索失败')
      }

      remoteBooks.value = await response.json()
    } catch (err) {
      const localQuery = query.trim().toLowerCase()
      remoteBooks.value = localQuery
        ? books.value.filter(book =>
          book.title.toLowerCase().includes(localQuery) ||
          book.author.toLowerCase().includes(localQuery) ||
          book.isbn.includes(localQuery) ||
          book.description.toLowerCase().includes(localQuery)
        )
        : null
      error.value = '搜索服务暂时不可用，已切换到本地检索'
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

  /**
   * 按分类筛选函数
   * 设置选中的图书分类
   * @param category - 分类名称
   */
  function filterByCategory(category: string) {
    selectedCategory.value = category
  }

  /**
   * 获取单本图书详情
   * 根据图书ID查找对应的图书信息
   * @param id - 图书唯一标识
   * @returns 图书信息或undefined
   */
  function getBookById(id: string): Book | undefined {
    return books.value.find(book => book.id === id)
  }

  /**
   * 借阅图书函数
   * 处理图书借阅逻辑，更新图书状态和副本信息
   * @param bookId - 要借阅的图书ID
   * @returns 借阅是否成功
   */
  async function borrowBook(bookId: string): Promise<boolean> {
    // 查找目标图书
    const book = books.value.find(b => b.id === bookId)
    if (!book || book.availableCopies <= 0) {
      return false  // 图书不存在或无可借副本
    }

    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))

      // 更新图书可用数量
      book.availableCopies--

      // 更新副本状态：找到第一个可借副本并标记为已借出
      const availableCopy = book.copies.find(c => c.status === 'available')
      if (availableCopy) {
        availableCopy.status = 'borrowed'
        // 设置应还日期为30天后
        const date = new Date()
        date.setDate(date.getDate() + 30)
        availableCopy.returnDate = date.toISOString().split('T')[0]
      }

      return true
    } catch (err) {
      error.value = '借阅失败，请重试'
      return false
    }
  }

  /**
     * 初始化函数
     * 生成并加载模拟图书数据
     */
  function initialize() {
    generateMockBooks()
    remoteBooks.value = null
  }

  return {
    // 状态导出
    books,              // 图书列表
    remoteBooks,        // 后端检索结果
    categories,         // 分类列表
    isLoading,          // 加载状态
    error,              // 错误信息
    searchQuery,        // 搜索关键词
    selectedCategory,   // 选中的分类

    // 计算属性导出
    filteredBooks,     // 过滤后的图书列表
    availableBooks,    // 可借图书列表
    recommendedBooks,  // 推荐图书列表

    // 方法导出
    searchBooks,        // 搜索图书函数
    filterByCategory,   // 按分类筛选函数
    getBookById,        // 获取图书详情函数
    borrowBook,         // 借阅图书函数
    initialize         // 初始化函数
  }
})
