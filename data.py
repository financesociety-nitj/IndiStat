"""
Top-level shortcut module for data extraction API.
"""

from indicator_library.data import (
    OHLCV_COLUMNS,
    get_raw_data,
    get_raw_ohlcv,
    get_stock_data,
    main,
)

__all__ = [
    "OHLCV_COLUMNS",
    "get_raw_data",
    "get_raw_ohlcv",
    "get_stock_data",
    "main",
]

if __name__ == "__main__":
    main()
