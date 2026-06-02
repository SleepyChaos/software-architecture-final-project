/**
 * 用户认证状态管理模块
 * 使用Pinia进行用户登录状态、用户信息的管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 用户数据接口定义
 * 描述用户对象的结构和类型
 */
export interface User {
  id: string      // 用户唯一标识
  email: string   // 用户邮箱
  studentId: string // 学号/读者证号
  fullName: string  // 用户全名
  department: string // 所属院系
}

/**
 * 用户认证状态存储
 * 管理用户登录状态、认证信息和相关操作
 */
export const useAuthStore = defineStore('auth', () => {
  // 状态定义
  const user = ref<User | null>(null)      // 当前用户信息
  const isLoading = ref(false)             // 登录加载状态
  const error = ref<string | null>(null)   // 错误信息

  // 计算属性：判断用户是否已认证
  const isAuthenticated = computed(() => !!user.value)

  /**
     * 用户登录函数
     * 调用后端API验证用户凭据并设置用户信息
     * @param studentId - 学号/读者证号
     * @param password - 用户密码
     * @returns 登录是否成功
     */
  async function login(studentId: string, password: string): Promise<boolean> {
    // 设置加载状态和重置错误信息
    isLoading.value = true
    error.value = null

    try {
      // 调用后端登录API
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reader_id: studentId, password: password }),
      })

      // 检查响应状态
      if (!response.ok) {
        throw new Error('登录失败')
      }

      const data = await response.json()

      // 适配用户数据（由于后端只返回ID，其他字段进行Mock处理）
      user.value = {
        id: data.reader_id,
        email: `${data.reader_id}@school.edu.cn`,
        studentId: data.reader_id,
        fullName: `读者${data.reader_id}`,
        department: '通用学院'
      }

      // 将用户信息保存到本地存储，实现登录状态持久化
      localStorage.setItem('user', JSON.stringify(user.value))

      return true
    } catch (err) {
      // 处理登录错误
      error.value = '登录失败，请检查账号密码'
      return false
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

  /**
     * 用户登出函数
     * 清除当前用户信息和本地存储
     */
  function logout() {
    // 重置用户状态
    user.value = null
    // 清除本地存储的用户信息
    localStorage.removeItem('user')
  }

  /**
   * 初始化用户函数
   * 从本地存储恢复用户登录状态
   */
  function initializeUser() {
    // 从本地存储获取用户信息
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        // 解析并恢复用户数据
        user.value = JSON.parse(storedUser)
      } catch (error) {
        // 如果解析失败，清除损坏的存储数据
        localStorage.removeItem('user')
      }
    }
  }

  return {
    // 状态导出
    user,           // 当前用户信息
    isLoading,      // 登录加载状态
    error,          // 错误信息
    isAuthenticated, // 认证状态

    // 方法导出
    login,          // 登录函数
    logout,         // 登出函数
    initializeUser  // 初始化用户函数
  }
})
