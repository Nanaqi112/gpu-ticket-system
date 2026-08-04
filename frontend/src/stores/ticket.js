import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ticketApi } from '../api'

export const useTicketStore = defineStore('ticket', () => {
  const tickets = ref([])
  const currentTicket = ref(null)
  const stats = ref({
    total: 0,
    completed: 0,
    in_progress: 0,
    pending: 0
  })
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0
  })

  async function fetchTickets(params = {}) {
    loading.value = true
    try {
      const response = await ticketApi.getList({
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        ...params
      })
      tickets.value = response.results
      pagination.value.total = response.count
    } catch (error) {
      console.error('获取工单列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchTicketDetail(id) {
    loading.value = true
    try {
      currentTicket.value = await ticketApi.getDetail(id)
    } catch (error) {
      console.error('获取工单详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      stats.value = await ticketApi.getStats()
    } catch (error) {
      console.error('获取统计数据失败:', error)
    }
  }

  async function createTicket(data) {
    loading.value = true
    try {
      const result = await ticketApi.create(data)
      return result
    } catch (error) {
      console.error('创建工单失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateTicket(id, data) {
    loading.value = true
    try {
      const result = await ticketApi.update(id, data)
      return result
    } catch (error) {
      console.error('更新工单失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteTicket(id) {
    loading.value = true
    try {
      await ticketApi.delete(id)
    } catch (error) {
      console.error('删除工单失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteAttachment(ticketId, attachmentId) {
    try {
      await ticketApi.deleteAttachment(ticketId, attachmentId)
      if (currentTicket.value) {
        currentTicket.value.attachments = currentTicket.value.attachments.filter(
          a => a.id !== attachmentId
        )
      }
    } catch (error) {
      console.error('删除附件失败:', error)
      throw error
    }
  }

  return {
    tickets,
    currentTicket,
    stats,
    loading,
    pagination,
    fetchTickets,
    fetchTicketDetail,
    fetchStats,
    createTicket,
    updateTicket,
    deleteTicket,
    deleteAttachment
  }
})