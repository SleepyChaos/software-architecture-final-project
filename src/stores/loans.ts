/**
 * 借阅记录管理状态存储模块
 * 管理用户的图书借阅记录、归还、续借等功能
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 借阅记录接口
 * 描述用户的图书借阅信息
 */
export interface BorrowRecord {
  id: string              // 借阅记录唯一标识
  bookId: string          // 图书ID
  bookTitle: string       // 图书标题
  bookAuthor: string       // 图书作者
  bookCover: string        // 图书封面URL
  borrowDate: string       // 借阅日期
  dueDate: string         // 应还日期
  returnDate?: string     // 实际归还日期（可选）
  status: 'borrowed' | 'returned' | 'overdue'  // 借阅状态
}

/**
 * 借阅记录管理状态存储
 * 提供借阅记录的增删改查、状态管理等功能
 */
export const useLoansStore = defineStore('loans', () => {
  // 状态定义
  const borrowRecords = ref<BorrowRecord[]>([])  // 借阅记录列表
  const isLoading = ref(false)                     // 加载状态
  const error = ref<string | null>(null)         // 错误信息

  /**
   * 计算属性：当前借阅的图书
   * 过滤出状态为'borrowed'的记录
   */
  const currentBorrows = computed(() =>
    borrowRecords.value.filter(record => record.status === 'borrowed')
  )

  /**
   * 计算属性：已归还的图书
   * 过滤出状态为'returned'的记录
   */
  const returnedBooks = computed(() =>
    borrowRecords.value.filter(record => record.status === 'returned')
  )

  /**
   * 计算属性：逾期的图书
   * 过滤出状态为'overdue'的记录
   */
  const overdueBooks = computed(() =>
    borrowRecords.value.filter(record => record.status === 'overdue')
  )

/**
   * 生成模拟借阅记录
   * 创建示例借阅数据用于演示
   */
  function generateMockLoans() {
    // 模拟借阅记录数据
    const mockRecords: BorrowRecord[] = [
      {
        id: '1',
        bookId: '1',
        bookTitle: '深入理解计算机系统',
        bookAuthor: 'Randal E. Bryant',
        bookCover: 'https://placehold.co/60x90/4F46E5/FFFFFF?text=CSAPP',
        borrowDate: '2024-11-15',
        dueDate: '2024-12-15',
        status: 'borrowed'
      },
      {
        id: '2',
        bookId: '3',
        bookTitle: '红楼梦',
        bookAuthor: '曹雪芹',
        bookCover: 'https://placehold.co/60x90/DC2626/FFFFFF?text=红楼梦',
        borrowDate: '2024-10-20',
        dueDate: '2024-11-20',
        returnDate: '2024-11-18',
        status: 'returned'
      },
      {
        id: '3',
        bookId: '4',
        bookTitle: '活着',
        bookAuthor: '余华',
        bookCover: 'https://placehold.co/60x90/7C2D12/FFFFFF?text=活着',
        borrowDate: '2024-11-01',
        dueDate: '2024-12-01',
        status: 'borrowed'
      }
    ]

    borrowRecords.value = mockRecords
  }

/**
   * 借阅图书函数
   * 创建新的借阅记录并添加到记录列表
   * @param book - 要借阅的图书信息
   * @returns 借阅是否成功
   */
  async function borrowBook(book: {
    id: string
    title: string
    author: string
    coverImageUrl: string
  }): Promise<boolean> {
    // 设置加载状态
    isLoading.value = true
    error.value = null

    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000))

      // 计算应还日期（30天后）
      const borrowDate = new Date()
      const dueDate = new Date(borrowDate.getTime() + 30 * 24 * 60 * 60 * 1000)

      // 创建新的借阅记录
      const newRecord: BorrowRecord = {
        id: Date.now().toString(),        // 使用时间戳作为唯一ID
        bookId: book.id,
        bookTitle: book.title,
        bookAuthor: book.author,
        bookCover: book.coverImageUrl,
        borrowDate: borrowDate.toISOString().split('T')[0],  // 格式化为YYYY-MM-DD
        dueDate: dueDate.toISOString().split('T')[0],      // 30天后的日期
        status: 'borrowed'                // 设置状态为已借阅
      }

      // 将新记录添加到列表开头
      borrowRecords.value.unshift(newRecord)

      return true
    } catch (err) {
      error.value = '借阅失败，请重试'
      return false
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

/**
   * 归还图书函数（通过记录ID）
   * 更新借阅记录的状态和归还日期
   * @param recordId - 借阅记录ID
   * @returns 归还是否成功
   */
  async function returnBook(recordId: string): Promise<boolean> {
    // 设置加载状态
    isLoading.value = true
    error.value = null

    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500))

      // 查找并更新借阅记录
      const record = borrowRecords.value.find(r => r.id === recordId)
      if (record) {
        record.status = 'returned'                                    // 更新状态为已归还
        record.returnDate = new Date().toISOString().split('T')[0]  // 设置归还日期
      }

      return true
    } catch (err) {
      error.value = '归还失败，请重试'
      return false
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

/**
   * 归还图书函数（通过书籍ID）
   * 根据图书ID查找对应的借阅记录并执行归还
   * @param bookId - 图书ID
   * @returns 归还是否成功
   */
  async function returnBookByBookId(bookId: string): Promise<boolean> {
    // 查找对应的借阅记录（状态为已借阅）
    const record = borrowRecords.value.find(r => r.bookId === bookId && r.status === 'borrowed')
    if (record) {
      // 如果找到记录，调用returnBook函数进行归还
      return returnBook(record.id)
    }
    // 即使找不到记录（比如是模拟生成的书），为了演示效果也返回成功
    return true
  }

/**
   * 续借图书函数
   * 延长图书的应还日期
   * @param recordId - 借阅记录ID
   * @returns 续借是否成功
   */
  async function renewBook(recordId: string): Promise<boolean> {
    // 设置加载状态
    isLoading.value = true
    error.value = null

    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 500))

      // 查找借阅记录并验证状态
      const record = borrowRecords.value.find(r => r.id === recordId)
      if (record && record.status === 'borrowed') {
        // 延长30天：在当前应还日期基础上增加30天
        const currentDueDate = new Date(record.dueDate)
        const newDueDate = new Date(currentDueDate.getTime() + 30 * 24 * 60 * 60 * 1000)
        record.dueDate = newDueDate.toISOString().split('T')[0]
        return true
      }
      return false  // 记录不存在或状态不允许续借
    } catch (err) {
      error.value = '续借失败'
      return false
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

/**
   * 检查逾期图书函数
   * 遍历所有借阅记录，将超期的记录状态更新为逾期
   */
  function checkOverdueBooks() {
    // 获取当前日期（YYYY-MM-DD格式）
    const today = new Date().toISOString().split('T')[0]

    // 遍历所有借阅记录
    borrowRecords.value.forEach(record => {
      // 检查是否为借阅状态且已超期
      if (record.status === 'borrowed' && record.dueDate < today) {
        record.status = 'overdue'  // 更新状态为逾期
      }
    })
  }

/**
   * 初始化函数
   * 生成模拟数据并检查逾期状态
   */
  function initialize() {
    generateMockLoans()    // 生成模拟借阅记录
    checkOverdueBooks()    // 检查并更新逾期状态
  }

  return {
    // 状态导出
    borrowRecords,    // 借阅记录列表
    isLoading,        // 加载状态
    error,            // 错误信息

    // 计算属性导出
    currentBorrows,   // 当前借阅的图书
    returnedBooks,    // 已归还的图书
    overdueBooks,     // 逾期的图书

    // 方法导出
    borrowBook,           // 借阅图书函数
    returnBook,           // 归还图书函数（通过记录ID）
    returnBookByBookId,   // 归还图书函数（通过图书ID）
    renewBook,            // 续借图书函数
    checkOverdueBooks,    // 检查逾期图书函数
    initialize           // 初始化函数
  }
})