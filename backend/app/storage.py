"""内存数据存储：用一个模块级变量保存 pandas DataFrame。"""
import threading
from typing import Optional

import pandas as pd

_lock = threading.Lock()
_dataframe: Optional[pd.DataFrame] = None


def load(df: pd.DataFrame) -> None:
    """载入（替换）内存中的数据。"""
    global _dataframe
    with _lock:
        _dataframe = df


def dataframe() -> Optional[pd.DataFrame]:
    """返回内存中的数据。"""
    with _lock:
        return _dataframe


def clear() -> None:
    """清空内存数据。"""
    global _dataframe
    with _lock:
        _dataframe = None