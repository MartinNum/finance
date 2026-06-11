<template>
  <div>
    <h2>工资录入</h2>
    <el-card v-if="canEdit()" style="margin-bottom: 20px">
      <el-form :model="form" label-width="100" inline>
        <el-form-item label="录入方式">
          <el-radio-group v-model="form.inputMode" size="small">
            <el-radio-button value="detail">明细录入</el-radio-button>
            <el-radio-button value="total">总额录入</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="工种">
          <el-select v-model="form.job_type_id" placeholder="请选择工种" @change="onJobTypeChange" style="width: 180px">
            <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
          </el-select>
        </el-form-item>

        <!-- 总额录入模式 -->
        <template v-if="form.inputMode === 'total'">
          <template v-if="form.billing === 'quantity'">
            <el-form-item label="数量">
              <el-input-number v-model="form.quantity" :min="0" :precision="2" style="width: 120px" />
            </el-form-item>
          </template>
          <template v-else>
            <el-form-item label="人数">
              <el-input-number v-model="form.headcount" :min="1" style="width: 120px" />
            </el-form-item>
            <el-form-item :label="form.billing === 'hourly' ? '小时数' : form.billing === 'monthly' ? '月数' : '天数'">
              <el-input-number v-model="form.days" :min="0" :precision="1" style="width: 120px" />
            </el-form-item>
          </template>
          <el-form-item label="总工资">
            <el-input-number v-model="form.totalAmount" :min="0" :precision="2" style="width: 150px" />
          </el-form-item>
          <el-form-item label="平均单价">
            <el-tag type="info" size="large">¥ {{ avgPrice.toFixed(2) }} / {{ form.billing === 'hourly' ? '时' : form.billing === 'monthly' ? '月' : form.billing === 'quantity' ? '单位' : '天' }}</el-tag>
          </el-form-item>
        </template>

        <!-- 明细录入：按量 -->
        <template v-else-if="form.billing === 'quantity'">
          <el-form-item label="单价">
            <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 150px" />
            <span style="margin-left: 8px; color: #999">元/单位</span>
          </el-form-item>
          <el-form-item label="数量">
            <el-input-number v-model="form.quantity" :min="0" :precision="2" style="width: 150px" />
          </el-form-item>
        </template>

        <!-- 明细录入：按天/按小时/按月 -->
        <template v-else>
          <el-form-item label="单价">
            <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 150px" />
            <span style="margin-left: 8px; color: #999">{{ form.billing === 'monthly' ? '月薪' : form.billing === 'hourly' ? '时薪' : '日薪' }}</span>
          </el-form-item>
          <el-form-item label="人数">
            <el-input-number v-model="form.headcount" :min="1" style="width: 120px" />
          </el-form-item>
          <el-form-item :label="form.billing === 'hourly' ? '小时数' : form.billing === 'monthly' ? '月数' : '天数'">
            <el-input-number v-model="form.days" :min="0" :precision="1" style="width: 120px" />
          </el-form-item>
        </template>

        <el-form-item label="金额" v-if="form.inputMode === 'detail'">
          <el-tag type="success" size="large">¥ {{ amount.toFixed(2) }}</el-tag>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.expense_date" type="date" value-format="YYYY-MM-DD" style="width: 180px" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitWage">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>工资记录</span>
          <el-date-picker v-model="filterRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="loadWages" />
        </div>
      </template>
      <el-table :data="wages" border>
        <el-table-column prop="expense_date" label="日期" width="120" />
        <el-table-column label="工种">
          <template #default="{ row }">{{ row.job_type?.name }}</template>
        </el-table-column>
        <el-table-column label="计费方式">
          <template #default="{ row }">{{ billingLabel(row.job_type?.billing_type) }}</template>
        </el-table-column>
        <el-table-column label="单价">
          <template #default="{ row }">{{ row.unit_price }}</template>
        </el-table-column>
        <el-table-column label="详情">
          <template #default="{ row }">
            <template v-if="row.job_type?.billing_type === 'quantity'">数量: {{ row.days }}</template>
            <template v-else-if="row.job_type?.billing_type === 'hourly'">{{ row.headcount }}人 × {{ row.days }}小时</template>
            <template v-else-if="row.job_type?.billing_type === 'monthly'">{{ row.headcount }}人 × {{ row.days }}月</template>
            <template v-else>{{ row.headcount }}人 × {{ row.days }}天</template>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column v-if="canEdit()" label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editWage(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteWage(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="editDialogVisible" title="编辑工资记录" width="500">
      <el-form :model="editForm" label-width="80">
        <el-form-item label="工种">
          <el-select v-model="editForm.job_type_id" placeholder="请选择工种" @change="onEditJobTypeChange" style="width: 100%">
            <el-option v-for="jt in jobTypes" :key="jt.id" :label="jt.name" :value="jt.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="人数" v-if="editBilling !== 'quantity'">
          <el-input-number v-model="editForm.headcount" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="editBilling === 'hourly' ? '小时数' : editBilling === 'quantity' ? '数量' : '天数'">
          <el-input-number v-model="editForm.days" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="总金额">
          <el-input-number v-model="editForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价">
          <el-tag type="info" size="large">¥ {{ editAvgPrice.toFixed(2) }} / {{ editBilling === 'hourly' ? '时' : editBilling === 'quantity' ? '单位' : '天' }}</el-tag>
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
import { wageApi, jobTypeApi } from '../api'
import { useCycleStore } from '../store/cycle.js'
import { useAuthStore } from '../store/auth'

const cycleStore = useCycleStore()
const { canEdit } = useAuthStore()
const jobTypes = ref([])
const wages = ref([])
const filterRange = ref(null)
const form = ref({
  inputMode: 'detail',
  job_type_id: null,
  unit_price: 0,
  headcount: 1,
  days: 1,
  quantity: 0,
  totalAmount: 0,
  expense_date: new Date().toISOString().slice(0, 10),
  remark: '',
  billing: 'daily'
})

const amount = computed(() => {
  if (form.value.billing === 'quantity') {
    return form.value.unit_price * form.value.quantity
  }
  return form.value.unit_price * form.value.headcount * form.value.days
})

const avgPrice = computed(() => {
  if (form.value.inputMode === 'total') {
    if (form.value.billing === 'quantity') {
      return form.value.quantity > 0 ? form.value.totalAmount / form.value.quantity : 0
    }
    if (form.value.headcount > 0 && form.value.days > 0) {
      return form.value.totalAmount / (form.value.headcount * form.value.days)
    }
  }
  return 0
})

const billingLabel = (type) => ({ daily: '按天', hourly: '按小时', monthly: '按月', quantity: '按量' }[type] || type)

const onJobTypeChange = (id) => {
  const jt = jobTypes.value.find(j => j.id === id)
  if (jt) {
    form.value.unit_price = jt.default_price
    form.value.billing = jt.billing_type
    if (jt.billing_type === 'quantity') {
      form.value.quantity = 0
    } else {
      form.value.headcount = 1
      form.value.days = 1
    }
  }
}

const loadJobTypes = async () => {
  const res = await jobTypeApi.list()
  jobTypes.value = res.data
}

const loadWages = async () => {
  const params = { cycle_id: cycleStore.state.currentCycleId }
  if (filterRange.value) {
    params.start_date = filterRange.value[0]
    params.end_date = filterRange.value[1]
  }
  const res = await wageApi.list(params)
  wages.value = res.data
}

const submitWage = async () => {
  if (!form.value.job_type_id) {
    ElMessage.warning('请选择工种')
    return
  }

  let headcount, days, unitPrice

  if (form.value.inputMode === 'total') {
    if (form.value.billing === 'quantity') {
      headcount = 1
      days = form.value.quantity
      unitPrice = avgPrice.value
    } else {
      headcount = form.value.headcount
      days = form.value.days
      unitPrice = avgPrice.value
    }
  } else if (form.value.billing === 'quantity') {
    headcount = 1
    days = form.value.quantity
    unitPrice = form.value.unit_price
  } else {
    headcount = form.value.headcount
    days = form.value.days
    unitPrice = form.value.unit_price
  }

  try {
    await wageApi.create({
      cycle_id: cycleStore.state.currentCycleId,
      job_type_id: form.value.job_type_id,
      unit_price: unitPrice,
      headcount: headcount,
      days: days,
      expense_date: form.value.expense_date,
      remark: form.value.remark || null
    })
    ElMessage.success('保存成功')
    loadWages()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const deleteWage = async (id) => {
  try {
    await wageApi.delete(id)
    ElMessage.success('删除成功')
    loadWages()
  } catch (err) {
    ElMessage.error('删除失败')
  }
}

const editDialogVisible = ref(false)
const editForm = ref({})
const editId = ref(null)
const editBilling = ref('daily')

const editAvgPrice = computed(() => {
  const divisor = editBilling.value === 'quantity'
    ? editForm.value.days
    : editForm.value.headcount * editForm.value.days
  return divisor > 0 ? editForm.value.amount / divisor : 0
})

const editWage = (row) => {
  editId.value = row.id
  editBilling.value = row.job_type?.billing_type || 'daily'
  editForm.value = {
    job_type_id: row.job_type_id,
    unit_price: row.unit_price,
    headcount: row.headcount,
    days: row.days,
    amount: row.amount,
    expense_date: row.expense_date,
    remark: row.remark || ''
  }
  editDialogVisible.value = true
}

const onEditJobTypeChange = (id) => {
  const jt = jobTypes.value.find(j => j.id === id)
  if (jt) {
    editBilling.value = jt.billing_type
    editForm.value.unit_price = jt.default_price
  }
}

const submitEdit = async () => {
  try {
    await wageApi.update(editId.value, {
      job_type_id: editForm.value.job_type_id,
      unit_price: editAvgPrice.value,
      headcount: editBilling.value === 'quantity' ? 1 : editForm.value.headcount,
      days: editForm.value.days,
      expense_date: editForm.value.expense_date,
      remark: editForm.value.remark || null
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadWages()
  } catch (err) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadJobTypes()
  loadWages()
})
</script>
