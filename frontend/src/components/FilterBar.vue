<script setup>
import { computed } from 'vue'

const props = defineProps({
  regions: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false }
})

const region = defineModel('region', { default: '' })
const yearStart = defineModel('year_start')
const yearEnd = defineModel('year_end')
const months = defineModel('months', { type: Array, default: () => [] })

const allMonths = Array.from({ length: 12 }, (_, i) => i + 1)
const monthsSet = computed(() => new Set(months.value || []))

function toggleMonth(m) {
  const cur = months.value || []
  months.value = monthsSet.value.has(m) ? cur.filter((x) => x !== m) : [...cur, m]
}
</script>

<template>
  <section class="card">
    <h2>2. 数据筛选</h2>
    <div class="filters" :class="{ disabled: disabled }">
      <label class="field">
        <span>地区</span>
        <select v-model="region" :disabled="disabled">
          <option value="">全部地区</option>
          <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
        </select>
      </label>

      <label class="field">
        <span>起始年份</span>
        <input v-model.number="yearStart" type="number" min="1900" max="2100" :disabled="disabled" />
      </label>

      <label class="field">
        <span>结束年份</span>
        <input v-model.number="yearEnd" type="number" min="1900" max="2100" :disabled="disabled" />
      </label>

      <div class="field months">
        <span>月份</span>
        <div class="month-pills">
          <button
            v-for="m in allMonths"
            :key="m"
            type="button"
            class="pill"
            :class="{ active: monthsSet.has(m) }"
            :disabled="disabled"
            @click="toggleMonth(m)"
          >
            {{ m }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}
.filters.disabled {
  opacity: 0.5;
  pointer-events: none;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field > span {
  font-size: 12px;
  color: var(--muted);
}
select,
input {
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 14px;
}
.months {
  grid-column: 1 / -1;
}
.month-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  width: 34px;
  height: 30px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}
.pill.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.pill:disabled {
  cursor: not-allowed;
}
</style>