<template>
  <div>
    <h2>葡萄等级管理</h2>
    <el-button v-if="canEdit()" type="primary" @click="showDialog">添加等级</el-button>
    <el-table :data="grades" style="margin-top: 20px" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="等级名称" />
      <el-table-column label="默认单价">
        <template #default="{ row }">¥ {{ row.default_price.toFixed(2) }} / kg</template>
      </el-table-column>
      <el-table-column label="状态">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canEdit()" label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="editGrade(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteGrade(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑等级' : '添加等级'" width="500">
      <el-form :model="form" label-width="100">
        <el-form-item label="等级名称">
          <el-input v-model="form.name" placeholder="如：特级、一级、二级" />
        </el-form-item>
        <el-form-item label="默认单价">
          <el-input-number v-model="form.default_price" :min="0" :precision="2" />
          <span style="margin-left: 8px; color: #999">元/kg</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
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
import { grapeGradeApi } from '../api'
import { useAuthStore } from '../store/auth'

const grades = ref([])
const { canEdit } = useAuthStore()
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', default_price: 0, is_active: true })
const editId = ref(null)

const loadGrades = async () => {
  const res = await grapeGradeApi.list()
  grades.value = res.data
}

const showDialog = () => {
  isEdit.value = false
  form.value = { name: '', default_price: 0, is_active: true }
  dialogVisible.value = true
}

const editGrade = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.value = { id: row.id, name: row.name, default_price: row.default_price, is_active: row.is_active }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    const payload = {
      name: form.value.name,
      default_price: form.value.default_price,
      is_active: form.value.is_active
    }
    if (isEdit.value) {
      await grapeGradeApi.update(editId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await grapeGradeApi.create(payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadGrades()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

const deleteGrade = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个等级吗？', '提示', { type: 'warning' })
    await grapeGradeApi.delete(id)
    ElMessage.success('删除成功')
    loadGrades()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadGrades)
</script>
