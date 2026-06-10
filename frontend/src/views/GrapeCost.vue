<template>
  <div>
    <h2>葡萄每斤成本分析</h2>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>计算参数</template>
          <el-form :model="form" label-width="160" inline>
            <el-form-item label="统计日期范围">
              <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadInvestment" />
            </el-form-item>
            <el-form-item label="快捷范围">
              <el-button-group>
                <el-button @click="setQuickRange('thisMonth')">本月</el-button>
                <el-button @click="setQuickRange('thisQuarter')">本季</el-button>
                <el-button @click="setQuickRange('thisCycle')">本周期</el-button>
              </el-button-group>
            </el-form-item>
          </el-form>

          <el-divider>投入数据</el-divider>
          <el-form :model="form" label-width="160" inline>
            <el-form-item label="总投入（自动汇总）">
              <el-input-number v-model="form.totalInvestment" :precision="2" :controls="false" disabled style="width: 180px" />
              <span style="margin-left: 8px; color: #999">元</span>
            </el-form-item>
          </el-form>

          <el-divider>产出数据</el-divider>
          <el-form :model="bunchConfig" label-width="160">
            <el-form-item label="计算方式">
              <el-radio-group v-model="bunchConfig.calc_mode" @change="onCalcModeChange">
                <el-radio value="by_weight">按每串重量计算总重量</el-radio>
                <el-radio value="by_total">按总重量计算每串重量</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="葡萄串数量">
              <el-input-number v-model="bunchConfig.bunch_count" :min="0" :precision="0" style="width: 180px" @change="onFieldChange('bunch_count')" />
              <span style="margin-left: 8px; color: #999">串</span>
            </el-form-item>
            <el-form-item label="每串重量">
              <el-input-number v-model="bunchConfig.bunch_weight" :min="0" :precision="2" :step="0.1" style="width: 180px" :disabled="bunchConfig.calc_mode === 'by_total'" @change="onFieldChange('bunch_weight')" />
              <span style="margin-left: 8px; color: #999">斤 / 串</span>
              <span v-if="bunchConfig.calc_mode === 'by_total'" style="margin-left: 8px; color: #E6A23C; font-size: 12px">（自动计算）</span>
            </el-form-item>
            <el-form-item label="总重量">
              <el-input-number v-model="bunchConfig.total_weight" :min="0" :precision="2" :step="1" style="width: 180px" :disabled="bunchConfig.calc_mode === 'by_weight'" @change="onFieldChange('total_weight')" />
              <span style="margin-left: 8px; color: #999">斤</span>
              <span v-if="bunchConfig.calc_mode === 'by_weight'" style="margin-left: 8px; color: #E6A23C; font-size: 12px">（自动计算）</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBunchConfig">保存产出数据</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" style="text-align: center">
          <div style="color: #909399; font-size: 14px; margin-bottom: 10px">每斤葡萄成本</div>
          <div style="font-size: 48px; color: #F56C6C; font-weight: bold">¥ {{ costPerJin.toFixed(2) }}</div>
          <el-divider></el-divider>
          <div style="text-align: left; color: #606266; line-height: 2">
            <div>总投入：<strong>¥ {{ form.totalInvestment.toFixed(2) }}</strong></div>
            <div>葡萄串数：<strong>{{ bunchConfig.bunch_count }}</strong> 串</div>
            <div>每串重量：<strong>{{ bunchConfig.bunch_weight.toFixed(2) }}</strong> 斤</div>
            <div>总重量：<strong>{{ bunchConfig.total_weight.toFixed(2) }}</strong> 斤</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>投入明细</template>
      <el-table :data="sortedBreakdownData" border>
        <el-table-column prop="name" label="类别" />
        <el-table-column label="金额（元）">
          <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="占比">
          <template #default="{ row }">
            <el-progress :percentage="getRatio(row.amount)" :format="(p) => p.toFixed(1) + '%'" />
          </template>
        </el-table-column>
        <el-table-column label="折合每斤成本">
          <template #default="{ row }">¥ {{ getCostPerJin(row.amount).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { reportApi, grapeBunchApi } from '../api'
import { useCycleStore } from '../store/cycle.js'
import { ElMessage } from 'element-plus'

const cycleStore = useCycleStore()
const dateRange = ref(null)
const form = ref({ totalInvestment: 0 })
const breakdownData = ref([])
const bunchConfig = ref({
  bunch_count: 0,
  bunch_weight: 0.8,
  total_weight: 0,
  calc_mode: 'by_weight'
})

const costPerJin = computed(() => bunchConfig.value.total_weight > 0 ? form.value.totalInvestment / bunchConfig.value.total_weight : 0)

const sortedBreakdownData = computed(() => {
  return [...breakdownData.value].sort((a, b) => {
    const costA = bunchConfig.value.total_weight > 0 ? a.amount / bunchConfig.value.total_weight : 0
    const costB = bunchConfig.value.total_weight > 0 ? b.amount / bunchConfig.value.total_weight : 0
    return costB - costA
  })
})

const onCalcModeChange = () => {
  recalculate()
}

const onFieldChange = (field) => {
  recalculate()
}

const recalculate = () => {
  const { calc_mode, bunch_count, bunch_weight, total_weight } = bunchConfig.value
  if (calc_mode === 'by_weight') {
    bunchConfig.value.total_weight = bunch_count * bunch_weight
  } else {
    if (bunch_count > 0) {
      bunchConfig.value.bunch_weight = parseFloat((total_weight / bunch_count).toFixed(2))
    }
  }
}

const setQuickRange = (type) => {
  const now = new Date()
  let start, end

  if (type === 'thisCycle') {
    const cycle = cycleStore.state.cycles.find(c => c.id === cycleStore.state.currentCycleId)
    if (cycle) {
      dateRange.value = [cycle.start_date, cycle.end_date]
      loadInvestment()
    }
    return
  }
  if (type === 'thisMonth') {
    start = new Date(now.getFullYear(), now.getMonth(), 1)
    end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  } else if (type === 'thisQuarter') {
    const quarter = Math.floor(now.getMonth() / 3)
    start = new Date(now.getFullYear(), quarter * 3, 1)
    end = new Date(now.getFullYear(), quarter * 3 + 3, 0)
  }
  dateRange.value = [start.toISOString().slice(0, 10), end.toISOString().slice(0, 10)]
  loadInvestment()
}

const loadInvestment = async () => {
  if (!dateRange.value) return
  try {
    const res = await reportApi.summary({
      cycle_id: cycleStore.state.currentCycleId,
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    })
    form.value.totalInvestment = res.data.total
    breakdownData.value = res.data.categories
  } catch (err) {
    console.error(err)
  }
}

const loadBunchConfig = async () => {
  try {
    const res = await grapeBunchApi.get({ cycle_id: cycleStore.state.currentCycleId })
    bunchConfig.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const saveBunchConfig = async () => {
  try {
    const res = await grapeBunchApi.update(
      { cycle_id: cycleStore.state.currentCycleId },
      {
        bunch_count: bunchConfig.value.bunch_count,
        bunch_weight: bunchConfig.value.bunch_weight,
        total_weight: bunchConfig.value.total_weight,
        calc_mode: bunchConfig.value.calc_mode
      }
    )
    bunchConfig.value = res.data
    ElMessage.success('产出数据已保存')
  } catch (err) {
    ElMessage.error('保存失败')
    console.error(err)
  }
}

const getRatio = (amount) => form.value.totalInvestment === 0 ? 0 : (amount / form.value.totalInvestment) * 100
const getCostPerJin = (amount) => bunchConfig.value.total_weight === 0 ? 0 : amount / bunchConfig.value.total_weight

onMounted(() => {
  loadBunchConfig()
})
</script>
