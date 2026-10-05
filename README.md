# Indicator-Library

Open Source Library of Indicators for Technical Dept., Finance Society, NITJ.

---

## 📈 Raw Stock Market Data API (`yfinance`)

This module provides a clean, standardized Python API for retrieving **pure, unadjusted OHLCV (Open, High, Low, Close, Volume)** historical stock market data using `yfinance`. It filters out non-OHLCV fields (such as dividends, splits, and capital gains) and returns structured data formatted for financial analysis and technical indicators.

---

## 🚀 Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/financesociety-nitj/Indicator-Library.git
cd Indicator-Library
pip install -r requirements.txt
```

---

## 📖 Quickstart

You can import either from `indicator_library` or directly from `data`:

```python
from indicator_library import get_stock_data

# Fetch raw OHLCV data for Apple
df = get_stock_data(
    stock="AAPL",
    start_date="2024-01-01",
    end_date="2024-01-15"
)

print(df)
```

**Output:**
```
                                 Open        High         Low       Close    Volume
Date
2024-01-02 00:00:00-05:00  187.149994  188.440002  183.889999  185.639999  82488700
2024-01-03 00:00:00-05:00  184.220001  185.880005  183.429993  184.250000  58414500
...
```

---

## 🛠️ API Reference

### `get_stock_data` / `get_raw_ohlcv` / `get_raw_data`

```python
get_stock_data(
    stock: str,
    start_date: str | date | datetime | pd.Timestamp | None = None,
    end_date: str | date | datetime | pd.Timestamp | None = None,
    *,
    start: str | date | datetime | pd.Timestamp | None = None,
    end: str | date | datetime | pd.Timestamp | None = None,
    date_range: tuple | list | None = None,
    interval: str = "1d",
    auto_adjust: bool = False,
    raise_if_empty: bool = True,
    as_format: str = "dataframe",
    **kwargs
) -> pd.DataFrame | dict | list | str
```

### Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `stock` | `str` | *required* | Stock ticker symbol (e.g. `'AAPL'`, `'MSFT'`, `'RELIANCE.NS'`, `'TCS.BO'`). |
| `start_date` / `start` | `DateLike` | `None` | Start date (inclusive). |
| `end_date` / `end` | `DateLike` | `None` | End date. |
| `date_range` | `tuple` / `list` | `None` | Convenience 2-element tuple: `(start_date, end_date)`. |
| `interval` | `str` | `'1d'` | Frequency (`'1m'`, `'2m'`, `'5m'`, `'15m'`, `'30m'`, `'60m'`, `'90m'`, `'1h'`, `'1d'`, `'5d'`, `'1wk'`, `'1mo'`, `'3mo'`). |
| `auto_adjust` | `bool` | `False` | When `False` (default), preserves 100% raw unadjusted market prices. |
| `raise_if_empty` | `bool` | `True` | Raise `ValueError` if ticker is invalid or returns no data for the date range. |
| `as_format` | `str` | `'dataframe'` | Output format: `'dataframe'`, `'records'`, `'dict'`, or `'json'`. |

### Returned Columns

The output strictly contains only OHLCV columns:
- `Open` (float)
- `High` (float)
- `Low` (float)
- `Close` (float)
- `Volume` (int / float)

---

## 💡 Examples & Date Range Formats

### 1. Standard String Dates (`YYYY-MM-DD`)

```python
from indicator_library import get_stock_data

df = get_stock_data("RELIANCE.NS", start_date="2024-01-01", end_date="2024-01-10")
```

### 2. Using `date_range` Tuple

```python
from indicator_library import get_stock_data

df = get_stock_data("MSFT", date_range=("2024-01-01", "2024-01-10"))
```

### 3. Using Python `datetime.date` or `datetime.datetime`

```python
from datetime import date, timedelta
from indicator_library import get_stock_data

end = date.today()
start = end - timedelta(days=30)

df = get_stock_data("GOOGL", start_date=start, end_date=end)
```

### 4. Custom Intervals (e.g., Hourly Data)

```python
from indicator_library import get_stock_data

df = get_stock_data("TSLA", start_date="2024-01-01", end_date="2024-01-05", interval="1h")
```

### 5. API-Ready Formats (`records`, `dict`, `json`)

```python
from indicator_library import get_stock_data

# List of dict records suitable for REST APIs or JSON responses
records = get_stock_data(
    "AAPL",
    start_date="2024-01-01",
    end_date="2024-01-05",
    as_format="records"
)
```

---

## 🖥️ Command-Line Interface (CLI)

You can also fetch OHLCV data directly from your terminal:

```bash
# Using data.py
python data.py AAPL --start 2024-01-01 --end 2024-01-10

# Or via package execution
python -m indicator_library RELIANCE.NS --start 2024-01-01 --end 2024-01-10 --interval 1d

# Output as JSON records
python -m indicator_library TSLA --start 2024-01-01 --end 2024-01-05 --format records
```

---

## 🧪 Running Tests

Run the test suite using `pytest`:

```bash
pytest
```
