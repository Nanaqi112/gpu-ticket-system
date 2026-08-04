<template>
  <div class="ticket-list">
    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="hover">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchText"
            placeholder="搜索序列号、来源地、故障描述"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="statusFilter" placeholder="按状态筛选" clearable>
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="router.push('/tickets/add')">
            <el-icon><Plus /></el-icon>
            添加工单
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 工单表格 -->
    <el-card class="table-card" shadow="hover">
      <el-table :data="tickets" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="serial_number" label="序列号" width="180" sortable />
        <el-table-column prop="model_display" label="型号" width="100" />
        <el-table-column prop="source" label="来源地" width="150" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="attachment_count" label="附件数" width="80" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="120" sortable>
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="已过天数" width="120" sortable>
          <template #default="{ row }">
            <el-tag
              :type="row.days_elapsed >= 21 ? 'danger' : 'warning'"
              effect="plain"
            >
              {{ row.days_elapsed }} 天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="router.push(`/tickets/${row.id}`)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticket'
import { storeToRefs } from 'pinia'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const store = useTicketStore()
const { tickets, loading, pagination } = storeToRefs(store)

const searchText = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

onMounted(() => {
  loadData()
})

watch(statusFilter, () => {
  currentPage.value = 1
  loadData()
})

async function loadData() {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  if (searchText.value) {
    params.search = searchText.value
  }
  if (statusFilter.value) {
    params.status = statusFilter.value
  }
  await store.fetchTickets(params)
}

function handleSearch() {
  currentPage.value = 1
  loadData()
}

function handleReset() {
  searchText.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  loadData()
}

function handleSizeChange() {
  currentPage.value = 1
  loadData()
}

function handlePageChange() {
  loadData()
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除工单 ${row.serial_number} 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await store.deleteTicket(row.id)
    ElMessage.success('删除成功')
    loadData()
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
.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card {
  border-radius: 12px;
}

.table-card {
  border-radius: 12px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>