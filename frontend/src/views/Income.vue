<template>
  <div>
    <h2>收入录入</h2>
    <el-card style="margin-bottom: 20px">
      <template #header>新增收入记录</template>
      <el-form :model="form" label-width="100" inline>
        <el-form-item label="葡萄等级">
          <el-select v-model="form.grade_id" placeholder="请选择等级" @change="onGradeChange" style="width: 180px">
            <el-option v-for="g in grades" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量(kg)">
          <el-input-number v-model="form.quantity_kg" :min="0" :precision="2" style="width: 150px" />
        </el-form-item>
        <el-form-item label="单价(元/kg)">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 150px" />
        </el-form-item>
        <el-form-item label="金额">
          <el-tag type="success" size="large">¥ {{ amount.toFixed(2) }}</el-tag>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.income_date" type="date" value-format="YYYY-MM-DD" style="width: 180px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitIncome">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>收入记录</span>
          <el-date-picker v-model="filterRange" type="daterange" range-separator="至"
            start-placeholder="开始日期" end-placeholder="结束日期"
            value-format="YYYY-MM-DD" @change="loadIncomes" />
        </div>
      </template>
      <el-table :data="incomes" border>
        <el-table-column prop="income_date" label="日期" width="120" />
        <el-table-column label="等级">
          <template #default="{ row }">{{ row.grade?.name }}</template>
        </el-table-column>
        <el-table-column label="数量(kg)">
          <template #default="{ row }">{{ row.quantity_kg.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="单价(元/kg)">
          <template #default="{ row }">{{ row.unit_price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="金额">
          <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteIncome(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { incomeApi, grapeGradeApi } from '../api'
import { useCycleStore } from '../store/cycle.js'

const cycleStore = useCycleStore()
const grades = ref([])
const incomes = ref([])
const filterRange = ref(null)
const form = ref({
  grade_id: null,
  quantity_kg: 0,
  unit_price: 0,
  income_date: new Date().toISOString().slice(0, 10),
  remark: ''
})

const amount = computed(() => form.value.quantity_kg * form.value.unit_price)

const onGradeChange = (id) => {
  const g = grades.value.find(x => x.id === id)
  if (g) form.value.unit_price = g.default_price
}

const loadGrades = async () => {
  const res = await grapeGradeApi.list()
  grades.value = res.data
}

const loadIncomes = async () => {
  const params = { cycle_id: cycleStore.state.currentCycleId }
  if (filterRange.value) {
    params.start_date = filterRange.value[0]
    params.end_date = filterRange.value[1]
  }
  const res = await incomeApi.list(params)
  incomes.value = res.data
}

const submitIncome = async () => {
  if (!form.value.grade_id) {
    ElMessage.warning('请选择葡萄等级')
    return
  }
  if (form.value.quantity_kg <= 0) {
    ElMessage.warning('请输入数量')
    return
  }
  if (form.value.unit_price <= 0) {
    ElMessage.warning('请输入单价')
    return
  }
  try {
    await incomeApi.create({
      cycle_id: cycleStore.state.currentCycleId,
      grade_id: form.value.grade_id,
      quantity_kg: form.value.quantity_kg,
      unit_price: form.value.unit_price,
      income_date: form.value.income_date,
      remark: form.value.remark || null
    })
    ElMessage.success('保存成功')
    form.value.quantity_kg = 0
    form.value.remark = ''
    loadIncomes()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const deleteIncome = async (id) => {
  try {
    await incomeApi.delete(id)
    ElMessage.success('删除成功')
    loadIncomes()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadGrades()
  loadIncomes()
})
</script>
