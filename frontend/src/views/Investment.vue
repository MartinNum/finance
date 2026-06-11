<template>
  <div>
    <h2>投资管理</h2>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">总投入</div>
            <div style="font-size: 32px; color: #67C23A; font-weight: bold">¥ {{ balanceData.total_investment.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">总支出</div>
            <div style="font-size: 32px; color: #F56C6C; font-weight: bold">¥ {{ balanceData.total_expense.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">剩余余额</div>
            <div :style="{ fontSize: '32px', fontWeight: 'bold', color: balanceData.balance >= 0 ? '#67C23A' : '#F56C6C' }">
              ¥ {{ balanceData.balance.toFixed(2) }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="canEdit()" style="margin-bottom: 20px">
      <template #header>新增投资记录</template>
      <el-form :model="form" label-width="100" inline>
        <el-form-item label="投资人">
          <el-autocomplete v-model="form.investor_name" :fetch-suggestions="suggestInvestor" placeholder="输入投资人名称" style="width: 180px" />
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 180px" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.invest_date" type="date" value-format="YYYY-MM-DD" style="width: 180px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitInvestment">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>投资记录</span>
          <el-select v-model="filterInvestor" placeholder="全部投资人" clearable style="width: 180px" @change="loadInvestments">
            <el-option v-for="name in investorNames" :key="name" :label="name" :value="name" />
          </el-select>
        </div>
      </template>
      <el-table :data="investments" border>
        <el-table-column prop="invest_date" label="日期" width="120" />
        <el-table-column prop="investor_name" label="投资人" />
        <el-table-column label="金额">
          <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column v-if="canEdit()" label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteInvestment(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { investmentApi } from '../api'
import { useCycleStore } from '../store/cycle.js'
import { useAuthStore } from '../store/auth'

const cycleStore = useCycleStore()
const { canEdit } = useAuthStore()
const investments = ref([])
const balanceData = ref({ total_investment: 0, total_expense: 0, balance: 0 })
const filterInvestor = ref('')
const form = ref({
  investor_name: '',
  amount: 0,
  invest_date: new Date().toISOString().slice(0, 10),
  remark: ''
})

const investorNames = computed(() => [...new Set(investments.value.map(i => i.investor_name))])

const suggestInvestor = (queryString, cb) => {
  const results = queryString
    ? investorNames.value.filter(n => n.includes(queryString)).map(n => ({ value: n }))
    : investorNames.value.map(n => ({ value: n }))
  cb(results)
}

const loadInvestments = async () => {
  const params = { cycle_id: cycleStore.state.currentCycleId }
  if (filterInvestor.value) {
    params.investor_name = filterInvestor.value
  }
  const res = await investmentApi.list(params)
  investments.value = res.data
}

const loadBalance = async () => {
  const res = await investmentApi.balance({ cycle_id: cycleStore.state.currentCycleId })
  balanceData.value = res.data
}

const submitInvestment = async () => {
  if (!form.value.investor_name) {
    ElMessage.warning('请输入投资人')
    return
  }
  if (form.value.amount <= 0) {
    ElMessage.warning('请输入金额')
    return
  }
  try {
    await investmentApi.create({
      cycle_id: cycleStore.state.currentCycleId,
      investor_name: form.value.investor_name,
      amount: form.value.amount,
      invest_date: form.value.invest_date,
      remark: form.value.remark || null
    })
    ElMessage.success('保存成功')
    form.value.amount = 0
    form.value.remark = ''
    loadInvestments()
    loadBalance()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const deleteInvestment = async (id) => {
  try {
    await investmentApi.delete(id)
    ElMessage.success('删除成功')
    loadInvestments()
    loadBalance()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadInvestments()
  loadBalance()
})
</script>
