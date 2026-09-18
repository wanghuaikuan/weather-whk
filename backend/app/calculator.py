"""距平计算核心逻辑 + 异常值检测。"""
from typing import Any, Dict, List, Optional

import pandas as pd

# 内部 DataFrame 列名约定
COL_DATE = "date"
COL_REGION = "region"
COL_TEMP = "temp"


def mark_outliers(df: pd.DataFrame) -> pd.Series:
    """用 IQR（四分位距）检测 (月份, 地区) 组内的原始日值异常。

    低于 Q1-1.5*IQR 或高于 Q3+1.5*IQR 视为异常。
    返回与 df 索引对齐的布尔 Series。
    """
    flags = pd.Series(False, index=df.index)
    if df is None or df.empty:
        return flags

    d = df.copy()
    d["year"] = d[COL_DATE].dt.year
    d["month"] = d[COL_DATE].dt.month

    for (_, _region), grp in d.groupby(["month", COL_REGION]):
        vals = grp[COL_TEMP]
        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (vals < lower) | (vals > upper)
        flags.loc[mask[mask].index] = True

    return flags


def compute_anomaly(
    df: pd.DataFrame,
    region: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    months: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """计算月平均气温距平。

    步骤：
      1. 月平均气温：按 (年份, 月份, 地区) 分组求均值；
      2. 历史同期基准：按 (月份, 地区) 分组，对所有年份求均值；
      3. 距平值 = 月平均 − 历史同期基准。

    地区/月份筛选同时作用于基准与输出；年份范围仅作用于输出
    （基准恒为全部年份的同期均值）。
    """
    if df is None or df.empty:
        return []

    d = df.copy()
    d["year"] = d[COL_DATE].dt.year
    d["month"] = d[COL_DATE].dt.month

    if region:
        d = d[d[COL_REGION] == region]
    if d.empty:
        return []

    # 历史同期基准（不受年份范围筛选影响）
    if months:
        base_source = d[d["month"].isin(months)]
    else:
        base_source = d
    if base_source.empty:
        return []

    baseline = (
        base_source.groupby(["month", COL_REGION], as_index=False)[COL_TEMP]
        .mean()
        .rename(columns={COL_TEMP: "baseline"})
    )

    # 年份/月份筛选作用于输出
    if year_start is not None:
        d = d[d["year"] >= year_start]
    if year_end is not None:
        d = d[d["year"] <= year_end]
    if months:
        d = d[d["month"].isin(months)]
    if d.empty:
        return []

    # 标记日值异常（按 (月份, 地区) 分组 IQR）
    d["is_outlier"] = mark_outliers(d[[COL_DATE, COL_REGION, COL_TEMP]])

    monthly = (
        d.groupby(["year", "month", COL_REGION], as_index=False)
        .agg(monthly_avg_temp=(COL_TEMP, "mean"), has_outlier=("is_outlier", "any"))
    )

    merged = monthly.merge(baseline, on=["month", COL_REGION], how="left")
    merged["anomaly"] = merged["monthly_avg_temp"] - merged["baseline"]

    items: List[Dict[str, Any]] = []
    for _, row in merged.iterrows():
        items.append(
            {
                "year": int(row["year"]),
                "month": int(row["month"]),
                "region": str(row[COL_REGION]),
                "monthly_avg_temp": round(float(row["monthly_avg_temp"]), 2),
                "anomaly": round(float(row["anomaly"]), 3),
                "is_anomaly": bool(row["has_outlier"]),
            }
        )

    items.sort(key=lambda x: (x["year"], x["month"], x["region"]))
    return items