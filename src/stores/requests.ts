/**
 * 预约委托管理状态存储模块
 * 管理用户的图书预约和委托请求
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 预约记录接口
 * 描述用户的图书预约和委托信息
 */
export interface Reservation {
  id: string                    // 预约记录唯一标识
  bookId: string                // 图书ID
  bookTitle: string             // 图书标题
  barcode?: string              // 图书条码（可选）
  pickupBranch: string          // 取书分馆
  notes?: string                // 备注信息（可选）
  status: 'requested' | 'fulfilled' | 'canceled'  // 预约状态
  requestedAt: string           // 预约请求时间
}

/**
 * 预约委托管理状态存储
 * 提供预约记录的创建、取消、查询等功能
 */
export const useRequestsStore = defineStore('requests', () => {
  // 状态定义
  const list = ref<Reservation[]>([])  // 预约记录列表

  /**
   * 创建预约记录函数
   * 创建新的图书预约或委托记录
   * @param payload - 预约信息（不包含id、status、requestedAt）
   * @returns 创建的预约记录
   */
  function createReservation(payload: Omit<Reservation, 'id' | 'status' | 'requestedAt'>) {
    // 构建完整的预约记录
    const record: Reservation = {
      id: Date.now().toString(),        // 使用时间戳作为唯一ID
      status: 'requested',              // 设置状态为已请求
      requestedAt: new Date().toISOString().split('T')[0],  // 设置请求时间为当前日期
      ...payload
    }
    // 将新记录添加到列表开头
    list.value.unshift(record)
    return record
  }

  /**
   * 取消预约函数
   * 根据预约ID取消预约请求
   * @param id - 预约记录ID
   */
  function cancelReservation(id: string) {
    // 查找对应的预约记录
    const target = list.value.find(r => r.id === id)
    if (target) {
      target.status = 'canceled'  // 更新状态为已取消
    }
  }

  /**
   * 按图书筛选函数
   * 根据图书ID获取相关的预约记录
   * @param bookId - 图书ID
   * @returns 对应的预约记录数组
   */
  function getByBook(bookId: string) {
    // 过滤出指定图书ID的预约记录
    return list.value.filter(r => r.bookId === bookId)
  }

  return {
    // 状态导出
    list,  // 预约记录列表

    // 方法导出
    createReservation,  // 创建预约记录函数
    cancelReservation,    // 取消预约函数
    getByBook           // 按图书筛选函数
  }
})

