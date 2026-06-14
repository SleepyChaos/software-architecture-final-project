9000/**
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
  const token = ref<string | null>(null)   // JWT 令牌
  const isLoading = ref(false)             // 登录加载状态
  const error = ref<string | null>(null)   // 错误信息

  // 计算属性：判断用户是否已认证
  const isAuthenticated = computed(() => !!user.value && !!token.value)

  /**
   * 获取当前 token（供 http 工具使用）
   */
  function getToken(): string | null {
    return token.value
  }

  /**
   * 用户登录函数
   * 调用后端API验证用户凭据并设置用户信息和令牌
   * @param studentId - 学号/读者证号
   * @param password - 用户密码
   * @returns 登录是否成功
   */
  async function login(studentId: string, password: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reader_id: studentId, password: password }),
      })

      if (!response.ok) {
        throw new Error('登录失败')
      }

      const data = await response.json()

      // 存储 JWT 令牌
      token.value = data.access_token

      // 适配用户数据
      user.value = {
        id: data.reader_id,
        email: `${data.reader_id}@school.edu.cn`,
        studentId: data.reader_id,
        fullName: `读者${data.reader_id}`,
        department: '通用学院'
      }

      // 持久化用户信息和令牌
      localStorage.setItem('user', JSON.stringify(user.value))
      localStorage.setItem('token', token.value)

      return true
    } catch (err) {
      error.value = '登录失败，请检查账号密码'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 用户登出函数
   * 清除当前用户信息、令牌和本地存储
   */
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  /**
   * 用户注册函数
   * 调用后端API注册新用户
   * @param readerId - 读者证号
   * @param password - 用户密码
   * @returns 注册是否成功
   */
  async function register(readerId: string, password: string): Promise<boolean> {
    isLoading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reader_id: readerId, password }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || '注册失败')
      }

      return true
    } catch (err: any) {
      error.value = err.message || '注册失败，请稍后重试'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 初始化用户函数
   * 从本地存储恢复用户登录状态和令牌
   */
  function initializeUser() {
    const storedUser = localStorage.getItem('user')
    const storedToken = localStorage.getItem('token')
    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser)
        token.value = storedToken
      } catch (error) {
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
  }

  return {
    // 状态导出
    user,           // 当前用户信息
    token,          // JWT 令牌
    isLoading,      // 登录加载状态
    error,          // 错误信息
    isAuthenticated, // 认证状态

    // 方法导出
    getToken,       // 获取令牌函数
    login,          // 登录函数
    logout,         // 登出函数
    register,       // 注册函数
    initializeUser  // 初始化用户函数
  }
})
