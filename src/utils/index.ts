/**
 * 工具函数集合
 */

/**
 * 格式化日期
 * @param date - 日期字符串或Date对象
 * @param format - 格式字符串，默认为 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date, format: string = 'YYYY-MM-DD'): string {
  const d = typeof date === 'string' ? new Date(date) : date

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
}

/**
 * 计算剩余天数
 * @param dueDate - 到期日期
 * @returns 剩余天数，负数表示已逾期
 */
export function getRemainingDays(dueDate: string): number {
  const today = new Date()
  const due = new Date(dueDate)
  const diffTime = due.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

/**
 * 判断是否为逾期
 * @param dueDate - 到期日期
 * @returns 是否逾期
 */
export function isOverdue(dueDate: string): boolean {
  const today = new Date()
  const due = new Date(dueDate)
  return today > due
}

/**
 * 生成随机ID
 * @param prefix - ID前缀
 * @returns 随机ID
 */
export function generateId(prefix: string = ''): string {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substr(2, 9)
  return `${prefix}${timestamp}-${random}`
}

/**
 * 防抖函数
 * @param func - 要执行的函数
 * @param wait - 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function (...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      func(...args)
    }, wait)
  }
}

/**
 * 节流函数
 * @param func - 要执行的函数
 * @param limit - 时间限制（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return function (...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 本地存储操作
 */
export const storage = {
  /**
   * 设置本地存储
   * @param key - 存储键
   * @param value - 存储值
   */
  set<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('Failed to save to localStorage:', error)
    }
  },

  /**
   * 获取本地存储
   * @param key - 存储键
   * @returns 存储值，不存在时返回null
   */
  get<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : null
    } catch (error) {
      console.error('Failed to load from localStorage:', error)
      return null
    }
  },

  /**
   * 删除本地存储
   * @param key - 存储键
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('Failed to remove from localStorage:', error)
    }
  },

  /**
   * 清空本地存储
   */
  clear(): void {
    try {
      localStorage.clear()
    } catch (error) {
      console.error('Failed to clear localStorage:', error)
    }
  }
}