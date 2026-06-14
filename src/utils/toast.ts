/**
 * 全局 Toast 事件总线
 * 供路由守卫、HTTP 工具等模块触发全局提示
 */

type ToastHandler = (message: string, type: 'error' | 'success' | 'warning' | 'info') => void

let handler: ToastHandler | null = null

/**
 * 注册全局 Toast 处理器
 * @param fn - 显示 Toast 的回调函数
 */
export function onToast(fn: ToastHandler) {
  handler = fn
}

/**
 * 触发全局 Toast 提示
 * @param message - 提示文字
 * @param type - 提示类型，默认 error
 */
export function showToast(message: string, type: 'error' | 'success' | 'warning' | 'info' = 'error') {
  handler?.(message, type)
}
