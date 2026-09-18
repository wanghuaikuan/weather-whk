<script setup>
import { ref } from 'vue'
import { exportCSV } from '../api'

const props = defineProps({
  items: { type: Array, default: () => [] },
  filter: { type: Object, required: true },
  loading: { type: Boolean, default: false }
})

const exporting = ref(false)

async function downloadCSV() {
  exporting.value = true
  try {
    const res = await exportCSV(props.filter)
    const url = URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'anomaly.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('导出失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    exporting.value = false
  }
}

function anomalyClass(v) {
  if (v > 0) return 'pos'
  if (v < 0) return 'neg'
  return 'zero'
}
</script>

<template>
  <section class="card">
    <div class="head">
      <h2>4. 计算结果</h2>
      <button class="btn" :disabled="!items.length || exporting" @click="downloadCSV">
        {{ exporting ? '导出中…' : '导出 CSV' }}
      </button>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>年份</th>
            <th>月份</th>
            <th>地区</th>
            <th>月平均气温 (℃)</th>
            <th>距平值 (℃)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="hint">加载中…</td>
          </tr>
          <tr v-else-if="!items.length">
            <td colspan="5" class="hint">暂无数据，请先导入 CSV</td>
          </tr>
          <tr v-for="(it, i) in items" :key="i">
            <td>{{ it.year }}</td>
            <td>{{ it.month }}</td>
            <td>{{ it.region }}</td>
            <td>{{ it.monthly_avg_temp }}</td>
            <td :class="anomalyClass(it.anomaly)">
              {{ it.anomaly > 0 ? '+' : '' }}{{ it.anomaly }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.head h2 {
  margin: 0;
}
.btn {
  padding: 8px 18px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
th,
td {
  padding: 9px 12px;
  border-bottom: 1px solid var(--line);
  text-align: left;
}
th {
  background: #fafbfc;
  color: var(--muted);
  font-weight: 600;
  white-space: nowrap;
}
.pos {
  color: var(--warm);
  font-weight: 600;
}
.neg {
  color: var(--cool);
  font-weight: 600;
}
.zero {
  color: var(--muted);
}
.hint {
  color: var(--muted);
  text-align: center;
}
</style>