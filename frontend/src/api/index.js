import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 工单API
export const ticketApi = {
  // 获取工单列表
  getList(params = {}) {
    return api.get('/tickets/', { params })
  },

  // 获取工单详情
  getDetail(id) {
    return api.get(`/tickets/${id}/`)
  },

  // 创建工单
  create(data) {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (key === 'attachments') {
        data[key]?.forEach(file => {
          formData.append('attachments', file)
        })
      } else {
        formData.append(key, data[key])
      }
    })
    return api.post('/tickets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 更新工单
  update(id, data) {
    const formData = new FormData()
    Object.keys(data).forEach(key => {
      if (key === 'attachments') {
        data[key]?.forEach(file => {
          formData.append('attachments', file)
        })
      } else {
        formData.append(key, data[key])
      }
    })
    return api.patch(`/tickets/${id}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 删除工单
  delete(id) {
    return api.delete(`/tickets/${id}/`)
  },

  // 获取统计数据
  getStats() {
    return api.get('/tickets/stats/')
  },

  // 删除附件
  deleteAttachment(ticketId, attachmentId) {
    return api.delete(`/tickets/${ticketId}/delete_attachment/`, {
      data: { attachment_id: attachmentId }
    })
  }
}

export default api