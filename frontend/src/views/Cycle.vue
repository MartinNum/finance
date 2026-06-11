<template>
  <div>
    <h2>周期管理</h2>
    <el-button v-if="canEdit()" type="primary" @click="showDialog">新建周期</el-button>
    <el-table :data="cycles" style="margin-top: 20px" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="周期名称" />
      <el-table-column prop="start_date" label="开始日期" width="140" />
      <el-table-column prop="end_date" label="结束日期" width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_current ? 'success' : 'info'">
            {{ row.is_current ? '当前' : '历史' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canEdit()" label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="activateCycle(row.id)" :disabled="row.is_current">设为当前</el-button>
          <el-button size="small" @click="editCycle(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteCycle(row.id)" :disabled="row.is_current">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑周期' : '新建周期'" width="500">
      <el-form :model="form" label-width="100">
        <el-form-item label="周期名称">
          <el-input v-model="form.name" placeholder="如：2026年周期" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
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
import { cycleApi } from '../api'
import { useCycleStore } from '../store/cycle.js'
import { useAuthStore } from '../store/auth'

const cycleStore = useCycleStore()
const { canEdit } = useAuthStore()
const cycles = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = ref({ name: '', start_date: '', end_date: '' })

const loadCycles = async () => {
  const res = await cycleApi.list()
  cycles.value = res.data
}

const showDialog = () => {
  isEdit.value = false
  form.value = { name: '', start_date: '', end_date: '' }
  dialogVisible.value = true
}

const editCycle = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { name: row.name, start_date: row.start_date, end_date: row.end_date }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.value.name || !form.value.start_date || !form.value.end_date) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (isEdit.value) {
      await cycleApi.update(editId.value, form.value)
      ElMessage.success('更新成功')
    } else {
      await cycleApi.create(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadCycles()
    cycleStore.loadCycles()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const activateCycle = async (id) => {
  try {
    await cycleApi.activate(id)
    ElMessage.success('已切换当前周期')
    loadCycles()
    cycleStore.loadCycles()
    cycleStore.setCurrentCycle(id)
  } catch (err) {
    ElMessage.error('操作失败')
  }
}

const deleteCycle = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个周期吗？相关数据也会丢失。', '提示', { type: 'warning' })
    await cycleApi.delete(id)
    ElMessage.success('删除成功')
    loadCycles()
    cycleStore.loadCycles()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(loadCycles)
</script>
