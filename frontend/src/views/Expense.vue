<template>
  <div>
    <h2>支出录入</h2>
    <el-card v-if="canEdit()" style="margin-bottom: 20px">
      <el-form :model="form" label-width="80" inline>
        <el-form-item label="大类">
          <el-select v-model="form.category" placeholder="请选择大类" @change="onCategoryChange" style="width: 160px">
            <el-option v-for="cat in categoryOptions" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="子类">
          <el-select v-model="form.sub_category" placeholder="请选择子类" style="width: 160px">
            <el-option v-for="sub in subCategoryOptions" :key="sub" :label="sub" :value="sub" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 150px" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.expense_date" type="date" value-format="YYYY-MM-DD" style="width: 180px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitExpense">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>支出记录</span>
          <div>
            <el-select v-model="filterCategory" placeholder="全部大类" clearable style="width: 150px; margin-right: 10px" @change="loadExpenses">
              <el-option v-for="cat in categoryOptions" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-date-picker v-model="filterRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadExpenses" />
          </div>
        </div>
      </template>
      <div style="margin-bottom: 10px">
        <el-tag type="warning" size="large">合计：¥ {{ totalAmount.toFixed(2) }}</el-tag>
      </div>
      <el-table :data="expenses" border>
        <el-table-column prop="expense_date" label="日期" width="120" />
        <el-table-column prop="category" label="大类" width="120" />
        <el-table-column prop="sub_category" label="子类" width="140" />
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column v-if="canEdit()" label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteExpense(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editDialogVisible" title="编辑支出记录" width="500">
      <el-form :model="editForm" label-width="80">
        <el-form-item label="大类">
          <el-select v-model="editForm.category" @change="editForm.sub_category = ''" style="width: 100%">
            <el-option v-for="cat in categoryOptions" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="子类">
          <el-select v-model="editForm.sub_category" style="width: 100%">
            <el-option v-for="sub in editSubCategoryOptions" :key="sub" :label="sub" :value="sub" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="editForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="editForm.expense_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { expenseApi, expenseCategoryApi } from '../api'
import { useCycleStore } from '../store/cycle.js'
import { useAuthStore } from '../store/auth'

const cycleStore = useCycleStore()
const { canEdit } = useAuthStore()
const categories = ref([])
const categoryOptions = computed(() => [...new Set(categories.value.map(c => c.category))])
const subCategoryOptions = computed(() =>
  categories.value.filter(c => c.category === form.value.category).map(c => c.sub_category)
)
const editSubCategoryOptions = computed(() =>
  categories.value.filter(c => c.category === editForm.value.category).map(c => c.sub_category)
)

const editDialogVisible = ref(false)
const editId = ref(null)
const editForm = ref({
  category: '',
  sub_category: '',
  amount: 0,
  expense_date: '',
  remark: ''
})

const form = ref({
  category: '',
  sub_category: '',
  amount: 0,
  expense_date: new Date().toISOString().slice(0, 10),
  remark: ''
})

const expenses = ref([])
const filterRange = ref(null)
const filterCategory = ref('')

const totalAmount = computed(() => expenses.value.reduce((sum, e) => sum + e.amount, 0))

const onCategoryChange = () => { form.value.sub_category = '' }

const loadCategories = async () => {
  const res = await expenseCategoryApi.list()
  categories.value = res.data
}

const loadExpenses = async () => {
  const params = { cycle_id: cycleStore.state.currentCycleId }
  if (filterRange.value) {
    params.start_date = filterRange.value[0]
    params.end_date = filterRange.value[1]
  }
  if (filterCategory.value) {
    params.category = filterCategory.value
  }
  const res = await expenseApi.list(params)
  expenses.value = res.data
}

const submitExpense = async () => {
  if (!form.value.category || !form.value.sub_category) {
    ElMessage.warning('请选择大类和子类')
    return
  }
  if (form.value.amount <= 0) {
    ElMessage.warning('请输入金额')
    return
  }
  try {
    await expenseApi.create({
      cycle_id: cycleStore.state.currentCycleId,
      category: form.value.category,
      sub_category: form.value.sub_category,
      amount: form.value.amount,
      expense_date: form.value.expense_date,
      remark: form.value.remark || null
    })
    ElMessage.success('保存成功')
    form.value.amount = 0
    form.value.remark = ''
    loadExpenses()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const openEditDialog = (row) => {
  editId.value = row.id
  editForm.value = {
    category: row.category,
    sub_category: row.sub_category,
    amount: row.amount,
    expense_date: row.expense_date,
    remark: row.remark || ''
  }
  editDialogVisible.value = true
}

const submitEdit = async () => {
  if (!editForm.value.category || !editForm.value.sub_category) {
    ElMessage.warning('请选择大类和子类')
    return
  }
  if (editForm.value.amount <= 0) {
    ElMessage.warning('请输入金额')
    return
  }
  try {
    const updateData = {
      category: editForm.value.category,
      sub_category: editForm.value.sub_category,
      amount: editForm.value.amount,
      expense_date: editForm.value.expense_date,
      remark: editForm.value.remark || null
    }
    const res = await expenseApi.update(editId.value, updateData)
    if (res.status === 200) {
      ElMessage.success('修改成功')
      editDialogVisible.value = false
      loadExpenses()
    }
  } catch (err) {
    const detail = err.response?.data?.detail || '未知错误'
    ElMessage.error(`修改失败: ${detail}`)
  }
}

const deleteExpense = async (id) => {
  try {
    await expenseApi.delete(id)
    ElMessage.success('删除成功')
    loadExpenses()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadCategories()
  loadExpenses()
})
</script>
