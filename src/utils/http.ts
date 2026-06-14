/**
 * 统一 HTTP 请求工具
 * - 自动携带 JWT token
 * - 统一处理 401 未授权响应
 */

import { useAuthStore } from '@/stores/auth'
import { showToast } from '@/utils/toast'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 带 token 的 fetch 封装
 * 自动在请求头中注入 Authorization: Bearer <token>
 * 收到 401 时触发全局未授权提示
 *
 * @param url - 请求路径（相对于 API_BASE_URL）或完整 URL
 * @param options - fetch 配置项
 * @returns fetch Response
 */
export async function apiFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const authStore = useAuthStore()

  // 构建完整 URL
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`

  // 合并请求头，注入 token
  const headers = new Headers(options.headers || {})
  const token = authStore.getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(fullUrl, {
    ...options,
    headers,
  })

  // 401 统一处理：清除登录态并触发全局提示
  if (response.status === 401) {
    authStore.logout()
    showToast('401 未授权，请先登录', 'error')
  }

  return response
}
