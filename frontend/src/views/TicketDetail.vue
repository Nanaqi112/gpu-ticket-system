<template>
  <div class="ticket-detail" v-loading="loading">
    <template v-if="ticket">
      <!-- 返回按钮和标题 -->
      <div class="page-header">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>工单详情</h2>
      </div>

      <!-- 基本信息 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <div>
              <el-tag :type="getStatusType(ticket.status)" size="large" effect="dark" style="margin-right: 12px;">
                {{ ticket.status_display }}
              </el-tag>
              <el-button v-if="userStore.isAdmin" type="primary" @click="showEditDialog">
                <el-icon><Edit /></el-icon>
                编辑工单
              </el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="序列号">
            {{ ticket.serial_number }}
          </el-descriptions-item>
          <el-descriptions-item label="型号类别">
            {{ ticket.model_display }}
          </el-descriptions-item>
          <el-descriptions-item label="来源地">
            {{ ticket.source }}
          </el-descriptions-item>
          <el-descriptions-item label="已过天数">
            <el-tag :type="ticket.days_elapsed >= 21 ? 'danger' : 'warning'">
              {{ ticket.days_elapsed }} 天
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(ticket.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(ticket.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="故障描述" :span="2">
            <div class="fault-desc">{{ ticket.fault_description }}</div>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 状态更新 (仅管理员可见) -->
      <el-card v-if="userStore.isAdmin" class="status-card" shadow="hover">
        <template #header>
          <span>更新状态</span>
        </template>
        <el-radio-group v-model="currentStatus" @change="handleStatusChange">
          <el-radio-button value="in_progress">进行中</el-radio-button>
          <el-radio-button value="completed">已完成</el-radio-button>
        </el-radio-group>
      </el-card>

      <!-- 图片附件 -->
      <el-card class="attachments-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>附件 ({{ ticket.attachments?.length || 0 }})</span>
            <el-upload
              v-if="userStore.isAdmin"
              :show-file-list="false"
              :before-upload="handleUpload"
              multiple
            >
              <el-button type="primary">
                <el-icon><Upload /></el-icon>
                上传附件
              </el-button>
            </el-upload>
          </div>
        </template>

        <!-- 图片列表 -->
        <div v-if="imageAttachments.length > 0" class="section">
          <h4>图片</h4>
          <div class="image-grid">
            <div v-for="img in imageAttachments" :key="img.id" class="image-item">
              <el-image
                :src="img.url"
                :preview-src-list="imageAttachments.map(i => i.url)"
                fit="cover"
                class="preview-image"
              />
              <div class="image-info">
                <span class="file-name">{{ img.file_name }}</span>
                <el-button v-if="userStore.isAdmin" type="danger" link @click="handleDeleteAttachment(img.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 文件列表 -->
        <div v-if="fileAttachments.length > 0" class="section">
          <h4>文件</h4>
          <el-table :data="fileAttachments" style="width: 100%">
            <el-table-column prop="file_name" label="文件名" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag>{{ getFileTypeLabel(row.file_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column prop="uploaded_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.uploaded_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" :width="userStore.isAdmin ? 120 : 80">
              <template #default="{ row }">
                <el-button type="primary" link :href="row.url" target="_blank">
                  下载
                </el-button>
                <el-button v-if="userStore.isAdmin" type="danger" link @click="handleDeleteAttachment(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-empty v-if="!ticket.attachments?.length" description="暂无附件" />
      </el-card>

      <!-- 编辑对话框 -->
      <el-dialog v-model="editDialogVisible" title="编辑工单" :width="isMobile ? '95%' : '600px'">
        <el-form :model="editForm" label-width="100px">
          <el-form-item label="型号类别">
            <el-select v-model="editForm.model_type" style="width: 100%">
              <el-option label="H100" value="H100" />
              <el-option label="H200" value="H200" />
              <el-option label="B200" value="B200" />
              <el-option label="H100底板" value="H100_BD" />
              <el-option label="H200底板" value="H200_BD" />
              <el-option label="B200底板" value="B200_BD" />
              <el-option label="A100" value="A100" />
              <el-option label="A800" value="A800" />
              <el-option label="L40S" value="L40S" />
              <el-option label="其他" value="OTHER" />
            </el-select>
          </el-form-item>
          <el-form-item label="序列号">
            <el-input v-model="editForm.serial_number" />
          </el-form-item>
          <el-form-item label="来源地">
            <el-input v-model="editForm.source" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="editForm.status" style="width: 100%">
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="更新时间">
            <el-date-picker
              v-model="editForm.updated_at"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="故障描述">
            <el-input v-model="editForm.fault_description" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">保存</el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticket'
import { useUserStore } from '../stores/user'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useTicketStore()
const userStore = useUserStore()
const { currentTicket: ticket, loading } = storeToRefs(store)

const currentStatus = ref('')
const editDialogVisible = ref(false)
const isMobile = ref(window.innerWidth <= 768)
const editForm = ref({
  model_type: '',
  serial_number: '',
  source: '',
  fault_description: '',
  status: '',
  updated_at: ''
})

window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth <= 768
})

onMounted(async () => {
  await store.fetchTicketDetail(route.params.id)
  if (ticket.value) {
    currentStatus.value = ticket.value.status
  }
})

function showEditDialog() {
  editForm.value = {
    model_type: ticket.value.model_type,
    serial_number: ticket.value.serial_number,
    source: ticket.value.source,
    fault_description: ticket.value.fault_description,
    status: ticket.value.status,
    updated_at: ticket.value.updated_at?.split('T')[0] || ''
  }
  editDialogVisible.value = true
}

async function handleEditSubmit() {
  try {
    await store.updateTicket(route.params.id, editForm.value)
    ElMessage.success('工单更新成功')
    editDialogVisible.value = false
    await store.fetchTicketDetail(route.params.id)
    currentStatus.value = ticket.value.status
  } catch {
    ElMessage.error('更新失败')
  }
}

const imageAttachments = computed(() => {
  return ticket.value?.attachments?.filter(a => a.file_type === 'image') || []
})

const fileAttachments = computed(() => {
  return ticket.value?.attachments?.filter(a => a.file_type !== 'image') || []
})

async function handleStatusChange(status) {
  try {
    await store.updateTicket(route.params.id, { status })
    ElMessage.success('状态更新成功')
    await store.fetchTicketDetail(route.params.id)
  } catch {
    ElMessage.error('状态更新失败')
    currentStatus.value = ticket.value.status
  }
}

async function handleUpload(file) {
  try {
    await store.updateTicket(route.params.id, { attachments: [file] })
    ElMessage.success('上传成功')
    await store.fetchTicketDetail(route.params.id)
  } catch {
    ElMessage.error('上传失败')
  }
  return false
}

async function handleDeleteAttachment(attachmentId) {
  try {
    await ElMessageBox.confirm('确定要删除此附件吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await store.deleteAttachment(route.params.id, attachmentId)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

function getStatusType(status) {
  const types = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

function getFileTypeLabel(type) {
  const labels = {
    image: '图片',
    document: '文档',
    log: '日志',
    other: '其他'
  }
  return labels[type] || '其他'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.ticket-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.info-card,
.status-card,
.attachments-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.fault-desc {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #606266;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 15px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.image-item {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

.preview-image {
  width: 100%;
  height: 150px;
}

.image-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fafafa;
}

.file-name {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .image-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .preview-image {
    height: 120px;
  }

  :deep(.el-descriptions) {
    font-size: 13px;
  }

  :deep(.el-descriptions__label) {
    width: 80px !important;
  }
}
</style>