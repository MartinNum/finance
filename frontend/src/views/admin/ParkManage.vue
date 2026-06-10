<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2 style="margin: 0">园区管理</h2>
      <el-button type="primary" @click="showCreate = true">新建园区</el-button>
    </div>

    <el-table :data="parks" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="园区名称" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ row.created_at ? new Date(row.created_at).toLocaleString() : '' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.is_active ? 'danger' : 'success'"
            @click="toggleActive(row)"
          >
            {{ row.is_active ? '停用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreate" title="新建园区" width="400">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="园区名称">
          <el-input v-model="createForm.name" placeholder="输入园区名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEdit" title="编辑园区" width="400">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="园区名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api'

const parks = ref([])
const showCreate = ref(false)
const showEdit = ref(false)
const createForm = reactive({ name: '' })
const editForm = reactive({ id: null, name: '' })

const loadParks = async () => {
  const res = await adminApi.listParks()
  parks.value = res.data
}

const handleCreate = async () => {
  if (!createForm.name) {
    ElMessage.warning('请输入园区名称')
    return
  }
  try {
    await adminApi.createPark({ name: createForm.name })
    ElMessage.success('创建成功')
    showCreate.value = false
    createForm.name = ''
    loadParks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

const openEdit = (row) => {
  editForm.id = row.id
  editForm.name = row.name
  showEdit.value = true
}

const handleEdit = async () => {
  try {
    await adminApi.updatePark(editForm.id, { name: editForm.name })
    ElMessage.success('更新成功')
    showEdit.value = false
    loadParks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}

const toggleActive = async (row) => {
  try {
    await adminApi.updatePark(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    loadParks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

onMounted(loadParks)
</script>
