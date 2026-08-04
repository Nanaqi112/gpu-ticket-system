<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-container">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-card class="stat-card stat-total" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon :size="48"><Tickets /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">工单总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="stat-card stat-completed" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon :size="48"><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.completed }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card class="stat-card stat-progress" shadow="hover">
            <div class="stat-content">
              <div class="stat-icon">
                <el-icon :size="48"><Loading /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.in_progress }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近工单 -->
    <el-card class="recent-tickets" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>最近工单</span>
          <el-button type="primary" @click="router.push('/tickets')">
            查看全部
          </el-button>
        </div>
      </template>

      <div class="table-wrapper">
        <el-table :data="tickets" style="width: 100%" v-loading="loading">
          <el-table-column prop="serial_number" label="序列号" width="180" />
          <el-table-column prop="model_display" label="型号" width="100" />
          <el-table-column prop="source" label="来源地" width="150" />
          <el-table-column prop="status_display" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="120">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="已过天数" width="100">
            <template #default="{ row }">
              <el-tag :type="row.days_elapsed >= 21 ? 'danger' : 'warning'">
                {{ row.days_elapsed }} 天
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" link @click="router.push(`/tickets/${row.id}`)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticket'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useTicketStore()
const { tickets, stats, loading } = storeToRefs(store)

onMounted(async () => {
  await Promise.all([
    store.fetchStats(),
    store.fetchTickets({ page_size: 10 })
  ])
})

function getStatusType(status) {
  const types = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
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
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-container {
  margin-bottom: 10px;
}

.stats-container .el-col {
  margin-bottom: 12px;
}

.stat-card {
  border-radius: 12px;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-completed .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-progress .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.recent-tickets {
  border-radius: 12px;
}

.table-wrapper {
  overflow-x: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .stat-card :deep(.el-card__body) {
    padding: 16px;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
  }

  .stat-icon .el-icon {
    font-size: 32px !important;
  }

  .stat-value {
    font-size: 28px;
  }

  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>