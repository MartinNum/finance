<template>
  <div>
    <h2>工种管理</h2>
    <el-button v-if="canEdit()" type="primary" @click="showDialog">添加工种</el-button>
    <el-table :data="jobTypes" style="margin-top: 20px" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="工种名称" />
      <el-table-column label="计费方式">
        <template #default="{ row }">
          {{ billingLabel(row.billing_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="default_price" label="默认单价" />
      <el-table-column v-if="canEdit()" label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editJobType(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteJobType(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑工种' : '添加工种'" width="500">
      <el-form :model="form" label-width="100">
        <el-form-item label="工种名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="计费方式">
          <el-radio-group v-model="form.billing_type">
            <el-radio value="daily">按天</el-radio>
            <el-radio value="hourly">按小时</el-radio>
            <el-radio value="monthly">按月</el-radio>
            <el-radio value="quantity">按量</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="默认单价">
          <el-input-number v-model="form.default_price" :min="0" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { jobTypeApi } from '../api'
import { useAuthStore } from '../store/auth'

const jobTypes = ref([])
const { canEdit } = useAuthStore()
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  name: '',
  billing_type: 'daily',
  default_price: 0
})
const editId = ref(null)

const billingLabel = (type) => {
  return { daily: '按天', hourly: '按小时', monthly: '按月', quantity: '按量' }[type] || type
}

const loadJobTypes = async () => {
  const res = await jobTypeApi.list()
  jobTypes.value = res.data
}

const showDialog = () => {
  isEdit.value = false
  form.value = { name: '', billing_type: 'daily', default_price: 0 }
  dialogVisible.value = true
}

const editJobType = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { id: row.id, name: row.name, billing_type: row.billing_type, default_price: row.default_price }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    const payload = {
      name: form.value.name,
      billing_type: form.value.billing_type,
      default_price: form.value.default_price
    }
    if (isEdit.value) {
      await jobTypeApi.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await jobTypeApi.create(payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadJobTypes()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const deleteJobType = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个工种吗？', '提示', { type: 'warning' })
    await jobTypeApi.delete(id)
    ElMessage.success('删除成功')
    loadJobTypes()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadJobTypes)
</script>
