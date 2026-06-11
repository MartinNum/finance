<template>
  <div>
    <h2>支出分类管理</h2>
    <el-button v-if="canEdit()" type="primary" @click="showDialog">添加分类</el-button>
    <el-table :data="categories" style="margin-top: 20px" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="category" label="大类" />
      <el-table-column prop="sub_category" label="子类" />
      <el-table-column v-if="canEdit()" label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="deleteCategory(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="添加分类" width="500">
      <el-form :model="form" label-width="80">
        <el-form-item label="大类">
          <el-autocomplete
            v-model="form.category"
            :fetch-suggestions="suggestCategory"
            placeholder="输入或选择大类"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="子类">
          <el-input v-model="form.sub_category" placeholder="输入子类名称" />
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
import { expenseCategoryApi } from '../api'
import { useAuthStore } from '../store/auth'

const categories = ref([])
const { canEdit } = useAuthStore()
const dialogVisible = ref(false)
const form = ref({
  category: '',
  sub_category: ''
})

const loadCategories = async () => {
  const res = await expenseCategoryApi.list()
  categories.value = res.data
}

const showDialog = () => {
  form.value = { category: '', sub_category: '' }
  dialogVisible.value = true
}

const suggestCategory = (queryString, cb) => {
  const existingCategories = [...new Set(categories.value.map(c => c.category))]
  const results = queryString
    ? existingCategories.filter(c => c.includes(queryString)).map(c => ({ value: c }))
    : existingCategories.map(c => ({ value: c }))
  cb(results)
}

const submitForm = async () => {
  if (!form.value.category || !form.value.sub_category) {
    ElMessage.warning('请输入大类和子类')
    return
  }
  try {
    await expenseCategoryApi.create(form.value)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    loadCategories()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '添加失败')
  }
}

const deleteCategory = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个分类吗？', '提示', { type: 'warning' })
    await expenseCategoryApi.delete(id)
    ElMessage.success('删除成功')
    loadCategories()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(loadCategories)
</script>
