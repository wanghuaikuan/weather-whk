# 气象气温距平分析工具

用于分析历史气温数据，计算月平均气温距平（某月平均气温与历史同期平均气温的差值）。核心价值在于将零散的逐日气温记录归一化为可横向对比的距平指标，帮助研究人员直观识别冷暖异常年、区域差异与长期趋势，支撑气候变化研究。

## 功能特性

- 数据导入与校验：上传 CSV，逐行校验列名、日期、气温格式并给出带行号的错误提示
- 月平均气温距平计算：按「年份 × 月份 × 地区」聚合后与历史同期基准求差
- 筛选能力：按地区、起止年份、月份（可多选）组合筛选
- 结果表格展示：分页/列表展示各年月地区对应的月均气温与距平值
- 距平趋势图：多地区同图对比折线图（X 轴时间、Y 轴距平），正距平暖色、负距平冷色、零线虚线
- 导出 CSV：将筛选后的计算结果导出为 CSV 文件
- 导出图表 PNG：折线图一键导出 PNG 图片
- 异常值检测：基于 IQR（四分位距）标记异常数据
- 实时计算：上传成功后自动触发重新计算并刷新界面
- 响应式设计：适配不同屏幕尺寸

## 技术栈

| 层次 | 选型 | 说明 |
|---|---|---|
| 后端 | Python 3.9+ / FastAPI / uvicorn / pandas | 轻量异步、自带 Swagger 文档，pandas 分组聚合简洁 |
| 前端 | Vue 3 + Vite + ECharts + axios | 组合式 API 快速开发，ECharts 折线图与图片导出 |
| 存储 | 内存（pandas DataFrame） | 数据量小，内存存储即可支持实时计算 |

## 目录结构

```
气象_whk/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 入口：CORS、路由注册
│   │   └── routers/
│   │       └── anomaly.py      # import / anomaly / export 路由
│   └── requirements.txt        # Python 依赖
├── frontend/                   # Vue 3 + Vite + ECharts
│   ├── vite.config.js          # /api 代理到 http://localhost:8000
│   └── src/                    # 页面与组件
├── data/
│   └── sample.csv              # 示例数据
├── ARCHITECTURE.md             # 架构文档
└── README.md                   # 本文档
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+

### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端启动后，Swagger 接口文档见 http://localhost:8000/docs 。

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:5173 （开发服务器默认端口）。

## API 接口说明

| 方法 | 路径 | 参数 | 说明 |
|---|---|---|---|
| POST | `/api/import` | multipart 字段 `file` | 上传 CSV，返回 `{success, message, row_count, regions, year_min, year_max}` |
| GET | `/api/anomaly` | `region` / `year_start` / `year_end` / `months` | 返回 `{items:[{year, month, region, monthly_avg_temp, anomaly}]}` |
| GET | `/api/export/csv` | 同 `/api/anomaly` | 下载计算结果为 CSV 文件 |

`months` 参数为逗号分隔的月份列表，`region` 可留空表示全地区。完整接口说明与在线调试见 Swagger：http://localhost:8000/docs 。

## CSV 数据格式说明

列名固定为 `日期,地区,气温`，日期格式 `YYYY-MM-DD`，气温为数值（单位 ℃）。

```csv
日期,地区,气温
2020-01-15,北京,2.5
2020-02-15,北京,5.2
```

校验规则：列名必须为 `日期,地区,气温`；日期可解析为有效日期；气温必须为数值；缺列、缺值或格式错误时返回带行号的错误提示。

## 距平计算公式

1. **月平均气温**：按 `(年份, 月份, 地区)` 分组求均值。
2. **历史同期基准**：按 `(月份, 地区)` 分组，对该组所有年份再求均值。
3. **距平值** = 当年月平均气温 − 历史同期基准。

样例验算（北京 1 月）：

```text
2020-01 平均 = (2.5 + 3.1) / 2 = 2.8
2021-01 平均 = (1.8 + 2.4) / 2 = 2.1
基准(1月)   = (2.8 + 2.1) / 2 = 2.45
距平 2020   = 2.8 - 2.45 = +0.35
距平 2021   = 2.1 - 2.45 = -0.35
```

## 使用示例

1. 确保后端（:8000）与前端（:5173）均已启动。
2. 浏览器打开 http://localhost:5173 。
3. 在页面上传区选择 `data/sample.csv` 并上传。
4. 上传成功后系统自动解析并重新计算，页面展示结果表格与距平趋势折线图。
5. 通过筛选栏选择地区、起止年份、月份查看对应距平结果。
6. 点击「导出 CSV」下载计算结果，点击「导出 PNG」保存折线图。