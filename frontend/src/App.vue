<script setup>
import { reactive, ref, watch } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import FilterBar from './components/FilterBar.vue'
import DataTable from './components/DataTable.vue'
import TrendChart from './components/TrendChart.vue'
import { fetchAnomaly } from './api'

const regions = ref([])
const filter = reactive({
  region: '',
  year_start: null,
  year_end: null,
  months: []
})
const items = ref([])
const loading = ref(false)
const hasData = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const res = await fetchAnomaly(filter)
    items.value = res.data.items || []
  } catch (e) {
    console.error('获取距平数据失败', e)
  } finally {
    loading.value = false
  }
}

// 上传成功后：初始化筛选元数据并自动刷新（实时计算）
function handleImported(result) {
  if (result.success) {
    regions.value = result.regions || []
    hasData.value = true
    filter.region = ''
    filter.months = []
    filter.year_start = null
    filter.year_end = null
    fetchData()
  }
}

// 筛选条件变化 -> 实时重新计算
watch(
  () => [filter.region, filter.year_start, filter.year_end, filter.months.length],
  () => {
    if (hasData.value) fetchData()
  }
)
</script>

<template>
  <div class="app">
    <header class="header">
      <h1>气象气温距平分析工具</h1>
      <p class="subtitle">月平均气温距平计算 · 气候变化研究</p>
    </header>

    <main class="main">
      <UploadPanel @imported="handleImported" />
      <FilterBar
        v-model:region="filter.region"
        v-model:year_start="filter.year_start"
        v-model:year_end="filter.year_end"
        v-model:months="filter.months"
        :regions="regions"
        :disabled="!hasData"
      />
      <TrendChart :items="items" />
      <DataTable :items="items" :filter="filter" :loading="loading" />
    </main>
  </div>
</template>

<style>
:root {
  --bg: #f5f7fa;
  --card: #ffffff;
  --line: #e5e9f0;
  --text: #2c3e50;
  --muted: #7f8c8d;
  --accent: #3a7bd5;
  --warm: #e74c3c;
  --cool: #3498db;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  color: var(--text);
}
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.header {
  margin-bottom: 20px;
}
.header h1 {
  margin: 0 0 4px;
  font-size: 24px;
}
.subtitle {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}
.main {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 18px;
}
.card h2 {
  margin: 0 0 14px;
  font-size: 16px;
}
/* 响应式：宽屏下图表占满、其余自适应 */
@media (min-width: 900px) {
  .main {
    grid-template-columns: 1fr 1fr;
  }
  .main > :first-child {
    grid-column: 1 / -1;
  }
  .main > :last-child {
    grid-column: 1 / -1;
  }
}
</style>