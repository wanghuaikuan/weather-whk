import axios from 'axios'

// 统一 axios 实例：baseURL 用相对路径 /api，开发环境由 vite 代理到后端
const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

/**
 * 根据筛选条件构造 anomaly / export 接口所需的查询参数
 * @param {Object} filter { region, year_start, year_end, months }
 */
export function buildAnomalyParams(filter) {
  const params = {}
  if (filter.region) params.region = filter.region
  if (filter.year_start !== null && filter.year_start !== undefined && filter.year_start !== '') {
    params.year_start = filter.year_start
  }
  if (filter.year_end !== null && filter.year_end !== undefined && filter.year_end !== '') {
    params.year_end = filter.year_end
  }
  if (filter.months && filter.months.length) {
    params.months = filter.months.join(',')
  }
  return params
}

// POST /api/import：上传 CSV（multipart/form-data，字段名 file）
export function importCSV(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/import', formData)
}

// GET /api/anomaly：查询距平结果
export function fetchAnomaly(filter) {
  return api.get('/anomaly', { params: buildAnomalyParams(filter) })
}

// GET /api/export/csv：导出 CSV 文件流
export function exportCSV(filter) {
  return api.get('/export/csv', {
    params: buildAnomalyParams(filter),
    responseType: 'blob'
  })
}

export default api