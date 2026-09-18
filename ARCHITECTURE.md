# 气象数据分析工具 —— 架构与技术栈

> 用于分析历史气温数据，计算月平均气温距平（某月平均气温与历史同期平均气温的差值），支持气候变化研究。

## 一、技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 后端 | Python 3.9+ / FastAPI / uvicorn / pandas | 轻量异步、自带 Swagger 文档，pandas 做分组聚合最简洁 |
| 前端 | Vue 3 + Vite + ECharts | 组合式 API 快速开发，ECharts 做折线图与图片导出 |
| 存储 | 内存（pandas DataFrame） | 原型阶段数据量小，内存存储即可支持「实时计算」 |

## 二、目录结构

```
气象_whk/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # 入口：CORS、路由注册、静态校验
│   │   ├── schemas.py          # Pydantic 数据模型
│   │   ├── storage.py          # 内存数据存储（加载/追加/清空）
│   │   ├── calculator.py       # 距平计算核心 + 异常值检测
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── anomaly.py      # import / anomaly / export 路由
│   └── requirements.txt
├── frontend/                   # Vue3 + Vite + ECharts
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js          # 含 /api 代理到后端
│   └── src/
│       ├── main.js
│       ├── App.vue             # 页面布局与状态编排
│       ├── api/index.js        # axios 封装，统一调用后端
│       └── components/
│           ├── UploadPanel.vue # CSV 上传 + 校验错误提示
│           ├── FilterBar.vue   # 地区/年份范围/月份筛选
│           ├── DataTable.vue   # 计算结果表格
│           └── TrendChart.vue  # 距平趋势折线图（ECharts，含 PNG 导出）
├── data/
│   └── sample.csv              # 示例数据（含样例与错误行）
├── ARCHITECTURE.md             # 本文档
└── README.md                   # 部署说明
```

## 三、API 契约

前缀统一为 `/api`，所有接口返回 JSON（导出除外）。

| 方法 | 路径 | 入参 | 返回 |
|---|---|---|---|
| POST | `/api/import` | `multipart/form-data`，字段 `file` | `{success, message, row_count, regions, year_min, year_max}` |
| GET | `/api/anomaly` | `region?` `year_start?` `year_end?` `months?`(逗号分隔) | `{items:[{year,month,region,monthly_avg_temp,anomaly}]}` |
| GET | `/api/export/csv` | 同上 | CSV 文件流（`text/csv`） |

## 四、数据格式与计算逻辑

### CSV 格式

```csv
日期,地区,气温
2020-01-15,北京,2.5
2020-02-15,北京,5.2
```

- 日期：`YYYY-MM-DD`
- 地区：字符串
- 气温：数值（单位 ℃）
- 校验规则：列名必须为 `日期/地区/气温`；日期可解析；气温为数值；缺列、缺值、格式错误返回带行号的错误提示

### 距平计算三步

1. **月平均气温**：按 `(年份, 月份, 地区)` 分组求均值
2. **历史同期基准**：按 `(月份, 地区)` 分组，对所有年份求均值
3. **距平值** = 当年月平均 − 历史同期基准

```text
样例验算（北京 1 月）：
  2020-01 平均 = (2.5+3.1)/2 = 2.8
  2021-01 平均 = (1.8+2.4)/2 = 2.1
  基准(1月)   = (2.8+2.1)/2 = 2.45
  距平2020    = 2.8-2.45 = +0.35
  距平2021    = 2.1-2.45 = -0.35
```

## 五、加分项落点

| 加分项 | 实现位置 |
|---|---|
| ECharts 可视化 | 前端 `TrendChart.vue`，多地区对比折线图 |
| 实时计算 | 上传成功后前端自动重新请求 `/api/anomaly` 刷新 |
| 异常值检测 | 后端 `calculator.py` 用 IQR（四分位距）标记，返回异常标记 |
| 响应式设计 | 前端网格布局 + 媒体查询 |
| 完整错误处理 | 后端统一异常返回 `{success:false,message}`，前端展示 |

## 六、多地区对比与图表配色

- 折线图 X 轴 = 时间（年份-月份），Y 轴 = 距平值
- 每条地区一条折线
- 正距平（暖色系如红/橙）、负距平（冷色系如蓝）用 `visualMap` 分段或按数据点符号着色
- 零值线用虚线标注，突出冷暖分界