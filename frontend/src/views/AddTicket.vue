<template>
  <div class="add-ticket">
    <div class="page-header">
      <el-button @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>添加工单</h2>
    </div>

    <el-card class="form-card" shadow="hover">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="top"
      >
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="型号类别" prop="model_type">
              <el-select v-model="form.model_type" placeholder="请选择型号" style="width: 100%">
                <el-option label="H100" value="H100" />
                <el-option label="H200" value="H200" />
                <el-option label="B200" value="B200" />
                <el-option label="A100" value="A100" />
                <el-option label="A800" value="A800" />
                <el-option label="L40S" value="L40S" />
                <el-option label="其他" value="OTHER" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="序列号" prop="serial_number">
              <el-input v-model="form.serial_number" placeholder="请输入序列号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="创建时间" prop="created_at">
              <el-date-picker
                v-model="form.created_at"
                type="date"
                placeholder="请选择创建时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="更新时间" prop="updated_at">
              <el-date-picker
                v-model="form.updated_at"
                type="date"
                placeholder="请选择更新时间"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="来源地" prop="source">
          <el-input v-model="form.source" placeholder="请输入来源地（机房、项目或客户名称）" />
        </el-form-item>

        <el-form-item label="故障描述" prop="fault_description">
          <el-input
            v-model="form.fault_description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述故障现象和相关信息"
          />
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            v-model:file-list="fileList"
            :auto-upload="false"
            multiple
            :limit="10"
            :on-exceed="handleExceed"
            :before-upload="beforeUpload"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持图片（jpg/png/gif/webp）和文档（pdf/txt/log/zip），单个文件不超过10MB，最多10个文件
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            提交工单
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticket'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useTicketStore()
const formRef = ref(null)
const fileList = ref([])
const submitting = ref(false)

const form = reactive({
  model_type: '',
  serial_number: '',
  source: '',
  fault_description: '',
  created_at: '',
  updated_at: ''
})

const rules = {
  model_type: [
    { required: true, message: '请选择型号类别', trigger: 'change' }
  ],
  serial_number: [
    { required: true, message: '请输入序列号', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  source: [
    { required: true, message: '请输入来源地', trigger: 'blur' }
  ],
  fault_description: [
    { required: true, message: '请输入故障描述', trigger: 'blur' }
  ],
  created_at: [
    { required: true, message: '请选择创建时间', trigger: 'change' }
  ],
  updated_at: [
    { required: true, message: '请选择更新时间', trigger: 'change' }
  ]
}

function beforeUpload(file) {
  const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  const allowedFileTypes = [
    'application/pdf',
    'text/plain',
    'text/csv',
    'application/zip',
    'application/x-tar',
    'application/gzip',
    'application/json',
    'application/xml',
    'text/xml',
    'text/html',
    'text/markdown'
  ]

  const isValidType = [...allowedImageTypes, ...allowedFileTypes].includes(file.type) ||
    file.name.endsWith('.log') || file.name.endsWith('.txt')

  if (!isValidType) {
    ElMessage.error('不支持的文件类型')
    return false
  }

  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }

  return true
}

function handleExceed() {
  ElMessage.warning('最多上传10个文件')
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  try {
    const files = fileList.value.map(f => f.raw).filter(Boolean)
    await store.createTicket({
      ...form,
      attachments: files
    })
    ElMessage.success('工单创建成功')
    router.push('/tickets')
  } catch (error) {
    ElMessage.error(error.response?.data?.serial_number?.[0] || '创建失败，请检查输入')
  } finally {
    submitting.value = false
  }
}

function handleReset() {
  formRef.value?.resetFields()
  fileList.value = []
}
</script>

<style scoped>
.add-ticket {
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

.form-card {
  border-radius: 12px;
  max-width: 800px;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .form-card {
    max-width: 100%;
  }

  :deep(.el-form-item__label) {
    font-size: 13px;
  }

  :deep(.el-date-editor) {
    width: 100% !important;
  }
}
</style>