<template>
  <div>
    <h2>分账管理</h2>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">周期总收入</div>
            <div style="font-size: 28px; color: #67C23A; font-weight: bold">¥ {{ totalIncome.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">已分账总额</div>
            <div style="font-size: 28px; color: #409EFF; font-weight: bold">¥ {{ totalDividend.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">待分账总额</div>
            <div style="font-size: 28px; color: #E6A23C; font-weight: bold">¥ {{ totalPending.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">投资人数量</div>
            <div style="font-size: 28px; color: #909399; font-weight: bold">{{ summary.length }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 20px">
      <template #header>投资人分账汇总</template>
      <el-table :data="summary" border>
        <el-table-column prop="investor_name" label="投资人" />
        <el-table-column label="投资金额">
          <template #default="{ row }">¥ {{ row.total_investment.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="投资占比">
          <template #default="{ row }">{{ (row.ratio * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="已分账金额">
          <template #default="{ row }">
            <span style="color: #67C23A">¥ {{ row.total_dividend.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="待分账金额">
          <template #default="{ row }">
            <span :style="{ color: row.pending >= 0 ? '#E6A23C' : '#F56C6C' }">¥ {{ row.pending.toFixed(2) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>分账明细</span>
          <el-select v-model="filterInvestor" placeholder="全部投资人" clearable style="width: 180px" @change="loadDividends">
            <el-option v-for="name in investorNames" :key="name" :label="name" :value="name" />
          </el-select>
        </div>
      </template>
      <el-table :data="dividends" border>
        <el-table-column prop="income_date" label="日期" width="120" />
        <el-table-column prop="investor_name" label="投资人" />
        <el-table-column label="分账比例">
          <template #default="{ row }">{{ (row.ratio * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="分账金额">
          <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { incomeApi, dividendApi } from '../api'
import { useCycleStore } from '../store/cycle.js'

const cycleStore = useCycleStore()
const dividends = ref([])
const summary = ref([])
const filterInvestor = ref('')

const investorNames = computed(() => [...new Set(summary.value.map(s => s.investor_name))])

const totalDividend = computed(() => summary.value.reduce((s, x) => s + x.total_dividend, 0))
const totalPending = computed(() => summary.value.reduce((s, x) => s + x.pending, 0))
const totalIncome = computed(() => totalDividend.value + totalPending.value)

const loadSummary = async () => {
  const res = await dividendApi.summary({ cycle_id: cycleStore.state.currentCycleId })
  summary.value = res.data
}

const loadDividends = async () => {
  const params = { cycle_id: cycleStore.state.currentCycleId }
  if (filterInvestor.value) params.investor_name = filterInvestor.value
  const res = await dividendApi.list(params)
  dividends.value = res.data
}

onMounted(() => {
  loadSummary()
  loadDividends()
})
</script>
