<template>
  <div>
    <h2>首页概览</h2>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center">
            <div style="color: #909399; font-size: 14px">本月总支出</div>
            <div style="font-size: 28px; color: #F56C6C; font-weight: bold">¥ {{ summary.total.toFixed(2) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="18">
        <el-row :gutter="20">
          <el-col :span="6" v-for="cat in summary.categories" :key="cat.name">
            <el-card shadow="hover">
              <div style="text-align: center">
                <div style="color: #909399; font-size: 13px">{{ cat.name }}</div>
                <div style="font-size: 20px; font-weight: bold">¥ {{ cat.amount.toFixed(2) }}</div>
                <div style="font-size: 12px; color: #409EFF">{{ (cat.ratio * 100).toFixed(1) }}%</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>本月支出占比</template>
          <div ref="pieRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>最近记录</template>
          <el-table :data="recentRecords" size="small">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.isWage ? 'warning' : 'primary'" size="small">
                  {{ row.isWage ? '工资' : '支出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="amount" label="金额" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { reportApi, wageApi, expenseApi } from '../api'
import { useCycleStore } from '../store/cycle.js'

const cycleStore = useCycleStore()
const summary = ref({ total: 0, period: {}, categories: [] })
const recentRecords = ref([])
const pieRef = ref(null)
let pieChart = null

const getMonthRange = () => {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), 1)
  const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  return {
    start_date: start.toISOString().slice(0, 10),
    end_date: end.toISOString().slice(0, 10)
  }
}

const loadData = async () => {
  const range = getMonthRange()
  const cycleId = cycleStore.state.currentCycleId
  const [summaryRes, wagesRes, expensesRes] = await Promise.all([
    reportApi.summary({ cycle_id: cycleId, ...range }),
    wageApi.list({ cycle_id: cycleId, ...range }),
    expenseApi.list({ cycle_id: cycleId, ...range })
  ])

  summary.value = summaryRes.data

  const wages = (wagesRes.data || []).slice(0, 10).map(w => ({
    date: w.expense_date, name: w.job_type?.name || '-', amount: w.amount, isWage: true
  }))
  const expenses = (expensesRes.data || []).slice(0, 10).map(e => ({
    date: e.expense_date, name: e.sub_category, amount: e.amount, isWage: false
  }))

  recentRecords.value = [...wages, ...expenses]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 15)

  renderPieChart()
}

const renderPieChart = () => {
  if (!pieRef.value) return
  if (!pieChart) pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { bottom: 10 },
    series: [{
      type: 'pie',
      radius: ['40%', '60%'],
      data: summary.value.categories.map(c => ({ name: c.name, value: c.amount })),
      label: { formatter: '{b}\n{d}%' }
    }]
  })
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => pieChart?.resize())
})

onBeforeUnmount(() => { pieChart?.dispose() })
</script>
