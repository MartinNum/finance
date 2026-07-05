<template>
  <div>
    <h2>报表面板</h2>
    <el-card style="margin-bottom: 20px">
      <el-space wrap>
        <span>日期范围：</span>
        <el-button-group>
          <el-button @click="setQuickRange('thisMonth')" :type="activeRange === 'thisMonth' ? 'primary' : ''">本月</el-button>
          <el-button @click="setQuickRange('lastMonth')" :type="activeRange === 'lastMonth' ? 'primary' : ''">上月</el-button>
          <el-button @click="setQuickRange('thisQuarter')" :type="activeRange === 'thisQuarter' ? 'primary' : ''">本季</el-button>
          <el-button @click="setQuickRange('thisCycle')" :type="activeRange === 'thisCycle' ? 'primary' : ''">本周期</el-button>
        </el-button-group>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="onRangeChange" />
        <el-button type="primary" @click="loadReport" :disabled="!dateRange">查询</el-button>
      </el-space>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>支出占比</template>
          <div ref="pieRef" style="height: 400px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>支出明细</template>
          <div style="margin-bottom: 15px">
            <el-tag type="info" size="large">总支出：¥ {{ summary.total.toFixed(2) }}</el-tag>
          </div>
          <el-table :data="[...summary.categories].sort((a, b) => b.ratio - a.ratio)" border>
            <el-table-column prop="name" label="类别" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="占比" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.ratio * 100" :format="(p) => p.toFixed(1) + '%'" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="selectedCategory" style="margin-top: 20px" v-loading="detailLoading">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>「{{ selectedCategory }}」明细</span>
          <el-tag type="info">合计：¥ {{ filteredDetails.reduce((s, r) => s + r.amount, 0).toFixed(2) }}</el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="10">
          <div ref="subPieRef" style="height: 300px"></div>
          <el-table :data="subSummary" border size="small" style="margin-top: 12px">
            <el-table-column prop="name" label="子类" />
            <el-table-column label="金额">
              <template #default="{ row }">¥ {{ row.value.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="占比" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.ratio * 100" :format="(p) => p.toFixed(1) + '%'" />
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="14">
          <div v-if="selectedSubName" style="margin-bottom: 12px; display: flex; align-items: center; gap: 10px">
            <el-tag type="warning" size="large" closable @close="clearSubFilter">
              当前筛选：{{ selectedSubName }}
            </el-tag>
            <el-button text type="primary" @click="clearSubFilter">显示全部</el-button>
          </div>
          <!-- 工资明细 -->
          <el-table v-if="detailType === 'wage'" :data="filteredDetails" border>
            <el-table-column prop="expense_date" label="日期" width="120" />
            <el-table-column label="工种">
              <template #default="{ row }">{{ row.job_type?.name }}</template>
            </el-table-column>
            <el-table-column label="详情">
              <template #default="{ row }">
                <template v-if="row.job_type?.billing_type === 'quantity'">数量: {{ row.days }}</template>
                <template v-else-if="row.job_type?.billing_type === 'hourly'">{{ row.headcount }}人 × {{ row.days }}小时</template>
                <template v-else-if="row.job_type?.billing_type === 'monthly'">{{ row.headcount }}人 × {{ row.days }}月</template>
                <template v-else>{{ row.headcount }}人 × {{ row.days }}天</template>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" />
          </el-table>

          <!-- 支出明细 -->
          <el-table v-else :data="filteredDetails" border>
            <el-table-column prop="expense_date" label="日期" width="120" />
            <el-table-column prop="sub_category" label="子类" width="140" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { reportApi, expenseApi, wageApi } from '../api'
import { useCycleStore } from '../store/cycle.js'

const cycleStore = useCycleStore()
const dateRange = ref(null)
const activeRange = ref('')
const summary = ref({ total: 0, period: {}, categories: [] })
const pieRef = ref(null)
let pieChart = null

const selectedCategory = ref('')
const categoryDetails = ref([])
const subSummary = ref([])
const detailType = ref('') // 'expense' | 'wage'
const detailLoading = ref(false)
const subPieRef = ref(null)
let subPieChart = null

// 子饼图扇区筛选
const selectedSubName = ref('')
const filteredDetails = computed(() => {
  if (!selectedSubName.value) return categoryDetails.value
  if (detailType.value === 'wage') {
    return categoryDetails.value.filter(r => (r.job_type?.name || '未知') === selectedSubName.value)
  }
  return categoryDetails.value.filter(r => r.sub_category === selectedSubName.value)
})
const clearSubFilter = () => { selectedSubName.value = '' }

const renderSubPieChart = (data) => {
  const total = data.reduce((s, r) => s + r.value, 0)
  subSummary.value = data.map(r => ({ ...r, ratio: total > 0 ? r.value / total : 0 }))
    .sort((a, b) => b.ratio - a.ratio)
  nextTick(() => {
    if (!subPieRef.value) return
    if (!subPieChart) {
      subPieChart = echarts.init(subPieRef.value)
      subPieChart.on('click', (params) => {
        if (params.componentType === 'series') {
          // 再次点击同一项则取消筛选
          selectedSubName.value = selectedSubName.value === params.name ? '' : params.name
        }
      })
    }
    subPieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', textStyle: { fontSize: 11 } },
      series: [{
        name: '占比',
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['60%', '50%'],
        data,
        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
        label: { formatter: '{b}\n{d}%', fontSize: 11 }
      }]
    })
  })
}

const setQuickRange = (type) => {
  activeRange.value = type
  const now = new Date()
  let start, end

  if (type === 'thisMonth') {
    start = new Date(now.getFullYear(), now.getMonth(), 1)
    end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  } else if (type === 'lastMonth') {
    start = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    end = new Date(now.getFullYear(), now.getMonth(), 0)
  } else if (type === 'thisQuarter') {
    const quarter = Math.floor(now.getMonth() / 3)
    start = new Date(now.getFullYear(), quarter * 3, 1)
    end = new Date(now.getFullYear(), quarter * 3 + 3, 0)
  } else if (type === 'thisCycle') {
    const cycle = cycleStore.state.cycles.find(c => c.id === cycleStore.state.currentCycleId)
    if (cycle) {
      dateRange.value = [cycle.start_date, cycle.end_date]
      loadReport()
      return
    }
  }

  dateRange.value = [formatDate(start), formatDate(end)]
  loadReport()
}

const onRangeChange = () => {
  activeRange.value = ''
  if (dateRange.value) loadReport()
}

const formatDate = (d) => d.toISOString().slice(0, 10)

const loadReport = async () => {
  if (!dateRange.value) return
  try {
    const res = await reportApi.summary({
      cycle_id: cycleStore.state.currentCycleId,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })
    summary.value = res.data
    renderPieChart()
  } catch (err) {
    console.error(err)
  }
}

const loadCategoryDetails = async (categoryName) => {
  selectedCategory.value = categoryName
  selectedSubName.value = ''
  detailLoading.value = true
  categoryDetails.value = []
  subSummary.value = []
  if (subPieChart) { subPieChart.dispose(); subPieChart = null }
  try {
    if (categoryName === '工资') {
      detailType.value = 'wage'
      const res = await wageApi.list({
        cycle_id: cycleStore.state.currentCycleId,
        start_date: dateRange.value[0],
        end_date: dateRange.value[1]
      })
      categoryDetails.value = res.data
      // 按工种聚合
      const map = {}
      res.data.forEach(r => {
        const name = r.job_type?.name || '未知'
        map[name] = (map[name] || 0) + r.amount
      })
      renderSubPieChart(Object.entries(map).map(([name, value]) => ({ name, value: +value.toFixed(2) })))
    } else {
      detailType.value = 'expense'
      const res = await expenseApi.list({
        cycle_id: cycleStore.state.currentCycleId,
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        category: categoryName
      })
      categoryDetails.value = res.data
      // 按子类聚合
      const map = {}
      res.data.forEach(r => {
        map[r.sub_category] = (map[r.sub_category] || 0) + r.amount
      })
      renderSubPieChart(Object.entries(map).map(([name, value]) => ({ name, value: +value.toFixed(2) })))
    }
  } finally {
    detailLoading.value = false
  }
}

const renderPieChart = () => {
  if (!pieRef.value) return
  if (!pieChart) {
    pieChart = echarts.init(pieRef.value)
    pieChart.on('click', (params) => {
      if (params.componentType === 'series') {
        loadCategoryDetails(params.name)
      }
    })
  }
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      name: '支出占比',
      type: 'pie',
      radius: '60%',
      data: summary.value.categories.map(c => ({ name: c.name, value: c.amount })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
      label: { formatter: '{b}\n{d}%' }
    }]
  })
}

onMounted(() => {
  setQuickRange('thisMonth')
  window.addEventListener('resize', () => pieChart?.resize())
})

onBeforeUnmount(() => { pieChart?.dispose(); subPieChart?.dispose() })
</script>
