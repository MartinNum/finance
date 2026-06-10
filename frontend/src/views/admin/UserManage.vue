<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px">
      <h2 style="margin: 0">用户管理</h2>
      <div>
        <el-select v-model="filterParkId" placeholder="按园区筛选" clearable style="margin-right: 10px; width: 180px" @change="loadUsers">
          <el-option v-for="p in parks" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-button type="primary" @click="openCreate">新建用户</el-button>
      </div>
    </div>

    <el-table :data="users" border stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="display_name" label="姓名" width="120" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : ''">
            {{ row.role === 'admin' ? '管理员' : '用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="所属园区" width="150">
        <template #default="{ row }">
          {{ parkMap[row.park_id] || (row.role === 'admin' ? '-' : '未分配') }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="openResetPwd(row)">重置密码</el-button>
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
    <el-dialog v-model="showCreate" title="新建用户" width="450">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="createForm.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="createForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="createForm.display_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="createForm.role === 'user'" label="所属园区">
          <el-select v-model="createForm.park_id" style="width: 100%" placeholder="选择园区">
            <el-option v-for="p in parks" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEdit" title="编辑用户" width="450">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.display_name" />
        </el-form-item>
        <el-form-item label="所属园区">
          <el-select v-model="editForm.park_id" style="width: 100%" placeholder="选择园区" clearable>
            <el-option v-for="p in parks" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Reset Password Dialog -->
    <el-dialog v-model="showResetPwd" title="重置密码" width="400">
      <el-form :model="resetPwdForm" label-width="80px">
        <el-form-item label="新密码">
          <el-input v-model="resetPwdForm.new_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResetPwd = false">取消</el-button>
        <el-button type="primary" @click="handleResetPwd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api'

const users = ref([])
const parks = ref([])
const filterParkId = ref(null)
const showCreate = ref(false)
const showEdit = ref(false)
const showResetPwd = ref(false)

const createForm = reactive({ username: '', password: '', display_name: '', role: 'user', park_id: null })
const editForm = reactive({ id: null, display_name: '', park_id: null })
const resetPwdForm = reactive({ id: null, new_password: '' })

const parkMap = computed(() => {
  const m = {}
  parks.value.forEach(p => { m[p.id] = p.name })
  return m
})

const loadParks = async () => {
  const res = await adminApi.listParks()
  parks.value = res.data
}

const loadUsers = async () => {
  const params = {}
  if (filterParkId.value) params.park_id = filterParkId.value
  const res = await adminApi.listUsers(params)
  users.value = res.data
}

const openCreate = () => {
  createForm.username = ''
  createForm.password = ''
  createForm.display_name = ''
  createForm.role = 'user'
  createForm.park_id = null
  showCreate.value = true
}

const handleCreate = async () => {
  if (!createForm.username || !createForm.password || !createForm.display_name) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (createForm.role === 'user' && !createForm.park_id) {
    ElMessage.warning('请选择所属园区')
    return
  }
  try {
    await adminApi.createUser({
      ...createForm,
      park_id: createForm.role === 'admin' ? null : createForm.park_id,
    })
    ElMessage.success('创建成功')
    showCreate.value = false
    loadUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '创建失败')
  }
}

const openEdit = (row) => {
  editForm.id = row.id
  editForm.display_name = row.display_name
  editForm.park_id = row.park_id
  showEdit.value = true
}

const handleEdit = async () => {
  try {
    await adminApi.updateUser(editForm.id, {
      display_name: editForm.display_name,
      park_id: editForm.park_id,
    })
    ElMessage.success('更新成功')
    showEdit.value = false
    loadUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}

const openResetPwd = (row) => {
  resetPwdForm.id = row.id
  resetPwdForm.new_password = ''
  showResetPwd.value = true
}

const handleResetPwd = async () => {
  if (!resetPwdForm.new_password) {
    ElMessage.warning('请输入新密码')
    return
  }
  try {
    await adminApi.resetPassword(resetPwdForm.id, { new_password: resetPwdForm.new_password })
    ElMessage.success('密码重置成功')
    showResetPwd.value = false
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '重置失败')
  }
}

const toggleActive = async (row) => {
  try {
    await adminApi.updateUser(row.id, { is_active: !row.is_active })
    ElMessage.success(row.is_active ? '已停用' : '已启用')
    loadUsers()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  loadParks()
  loadUsers()
})
</script>
