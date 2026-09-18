<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  items: { type: Array, default: () => [] }
})

const chartRef = ref(null)
let chart = null

const WARM = '#e74c3c'
const COOL = '#3498db'
const PALETTE = ['#2c3e50', '#8e44ad', '#e67e22', '#16a085', '#c0392b', '#2980b9']

function timeLabel(item) {
  return `${item.year}-${String(item.month).padStart(2, '0')}`
}

function render() {
  if (!chart) return
  const items = props.items
  if (!items.length) {
    chart.clear()
    return
  }

  const regions = [...new Set(items.map((i) => i.region))]
  const times = [...new Set(items.map(timeLabel))].sort()

  const series = regions.map((region) => {
    const valueByTime = new Map()
    items
      .filter((i) => i.region === region)
      .forEach((i) => valueByTime.set(timeLabel(i), i.anomaly))

    const data = times.map((t) => {
      const v = valueByTime.get(t)
      if (v === undefined) return null
      return { value: v, itemStyle: { color: v >= 0 ? WARM : COOL } }
    })

    return {
      name: region,
      type: 'line',
      smooth: true,
      symbolSize: 7,
      connectNulls: false,
      data,
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: '#999', type: 'dashed' },
        data: [{ yAxis: 0 }]
      }
    }
  })

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: regions, top: 0 },
    grid: { left: 50, right: 24, top: 40, bottom: 44 },
    xAxis: { type: 'category', data: times, name: '时间' },
    yAxis: { type: 'value', name: '距平值 (℃)', scale: true },
    series
  })
}

function handleResize() {
  chart && chart.resize()
}

function downloadPNG() {
  if (!chart) return
  const url = chart.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#ffffff'
  })
  const a = document.createElement('a')
  a.href = url
  a.download = 'anomaly_chart.png'
  a.click()
}

onMounted(() => {
  chart = echarts.init(chartRef.value)
  render()
  window.addEventListener('resize', handleResize)
})

watch(() => props.items, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart && chart.dispose()
})
</script>

<template>
  <section class="card">
    <div class="head">
      <h2>3. 距平趋势图（多地区对比）</h2>
      <button class="btn" :disabled="!items.length" @click="downloadPNG">导出 PNG</button>
    </div>
    <div ref="chartRef" class="chart"></div>
    <div class="legend-hint">
      <span class="dot warm"></span> 正距平（暖）<span class="dot cool"></span> 负距平（冷）
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
.chart {
  width: 100%;
  height: 380px;
}
.legend-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.dot.warm {
  background: var(--warm);
}
.dot.cool {
  background: var(--cool);
}
</style>