<script setup>
import { ref } from 'vue'
import { importCSV } from '../api'

const emit = defineEmits(['imported'])

const file = ref(null)
const uploading = ref(false)
const message = ref('')
const errors = ref([])
const success = ref(false)

function onFileChange(e) {
  file.value = e.target.files[0] || null
  errors.value = []
  message.value = ''
}

async function upload() {
  if (!file.value) {
    message.value = '请先选择 CSV 文件'
    success.value = false
    return
  }
  uploading.value = true
  message.value = ''
  errors.value = []
  success.value = false
  try {
    const res = await importCSV(file.value)
    const data = res.data
    success.value = data.success
    message.value = data.message
    errors.value = data.errors || []
    if (data.success) {
      emit('imported', data)
    }
  } catch (e) {
    success.value = false
    message.value = '上传失败: ' + (e.response?.data?.detail || e.message)
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <section class="card">
    <h2>1. 数据导入</h2>
    <div class="upload-row">
      <input type="file" accept=".csv,text/csv" @change="onFileChange" />
      <button class="btn" :disabled="uploading" @click="upload">
        {{ uploading ? '导入中…' : '上传并导入' }}
      </button>
    </div>
    <p v-if="message" :class="success ? 'msg ok' : 'msg err'">{{ message }}</p>
    <ul v-if="errors.length" class="errors">
      <li v-for="(e, i) in errors" :key="i">第 {{ e.line }} 行：{{ e.reason }}</li>
    </ul>
  </section>
</template>

<style scoped>
.upload-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
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
.msg {
  margin: 10px 0 0;
  font-size: 14px;
}
.msg.ok {
  color: #27ae60;
}
.msg.err {
  color: var(--warm);
}
.errors {
  margin: 10px 0 0;
  padding-left: 18px;
  color: var(--warm);
  font-size: 13px;
  max-height: 120px;
  overflow-y: auto;
}
</style>