"""接口路由：导入 / 距平计算 / 导出 CSV。"""
import csv
import io
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from .. import calculator, storage
from ..schemas import AnomalyResponse, ImportErrorItem, ImportResult

router = APIRouter(prefix="/api", tags=["anomaly"])


def _decode(content: bytes) -> Optional[str]:
    """尝试常见编码解码，失败返回 None。"""
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def _parse_months(months: Optional[str]) -> Optional[List[int]]:
    """解析 months 逗号分隔参数，如 "1,2,3"。"""
    if not months:
        return None
    try:
        return [int(m.strip()) for m in months.split(",") if m.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="months 参数格式错误，应为逗号分隔的整数")


@router.post("/import", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...)):
    """上传 CSV，校验并导入有效行到内存（容错：记录错误行）。"""
    try:
        content = await file.read()
    except Exception as exc:  # noqa: BLE001
        return ImportResult(success=False, message=f"读取文件失败: {exc}")

    text = _decode(content)
    if text is None:
        return ImportResult(success=False, message="无法解析文件编码（仅支持 UTF-8 / GBK）")

    rows: List[dict] = []
    errors: List[ImportErrorItem] = []
    reader = csv.reader(io.StringIO(text))
    header = None

    for line_no, row in enumerate(reader, start=1):
        # 跳过空行
        if not row or all(c.strip() == "" for c in row):
            continue

        if header is None:
            header = [c.strip() for c in row]
            if set(header) != {"日期", "地区", "气温"}:
                return ImportResult(
                    success=False,
                    message=f"表头应为「日期,地区,气温」，实际为「{','.join(header)}」",
                    errors=errors,
                )
            continue

        if len(row) < 3:
            errors.append(ImportErrorItem(line=line_no, reason="列数不足 3 列"))
            continue

        date_str, region, temp_str = row[0].strip(), row[1].strip(), row[2].strip()

        try:
            parsed_date = pd.to_datetime(date_str, errors="raise")
        except Exception:  # noqa: BLE001
            errors.append(ImportErrorItem(line=line_no, reason=f"日期格式错误: {date_str!r}"))
            continue

        try:
            temp = float(temp_str)
        except ValueError:
            errors.append(ImportErrorItem(line=line_no, reason=f"气温不是数值: {temp_str!r}"))
            continue

        if not region:
            errors.append(ImportErrorItem(line=line_no, reason="地区为空"))
            continue

        rows.append({"date": parsed_date, "region": region, "temp": temp})

    if not rows:
        return ImportResult(
            success=False, message="没有可导入的有效数据", errors=errors
        )

    df = pd.DataFrame(rows)
    storage.load(df)

    years = df["date"].dt.year
    regions = sorted(df["region"].unique().tolist())
    return ImportResult(
        success=True,
        message=f"成功导入 {len(rows)} 条数据"
        + (f"，另有 {len(errors)} 行格式错误被跳过" if errors else ""),
        row_count=len(rows),
        regions=regions,
        year_min=int(years.min()),
        year_max=int(years.max()),
        errors=errors,
    )


@router.get("/anomaly", response_model=AnomalyResponse)
def get_anomaly(
    region: Optional[str] = Query(None),
    year_start: Optional[int] = Query(None),
    year_end: Optional[int] = Query(None),
    months: Optional[str] = Query(None),
):
    """计算月平均气温距平，支持地区/年份范围/月份筛选。"""
    df = storage.dataframe()
    if df is None or df.empty:
        return AnomalyResponse(items=[])

    month_list = _parse_months(months)
    items = calculator.compute_anomaly(df, region, year_start, year_end, month_list)
    return AnomalyResponse(items=items)


@router.get("/export/csv")
def export_csv(
    region: Optional[str] = Query(None),
    year_start: Optional[int] = Query(None),
    year_end: Optional[int] = Query(None),
    months: Optional[str] = Query(None),
):
    """导出计算结果为 CSV 文件流。"""
    df = storage.dataframe()
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="暂无数据，请先导入 CSV")

    month_list = _parse_months(months)
    items = calculator.compute_anomaly(df, region, year_start, year_end, month_list)

    buf = io.StringIO()
    buf.write("年份,月份,地区,月平均气温,距平值\n")
    for it in items:
        buf.write(
            f"{it['year']},{it['month']},{it['region']},"
            f"{it['monthly_avg_temp']},{it['anomaly']}\n"
        )
    data = buf.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=anomaly.csv"},
    )