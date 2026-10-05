"""
Data module for fetching raw OHLCV market data using yfinance.

Exposes APIs to fetch historical stock data filtered strictly
to Open, High, Low, Close, and Volume (OHLCV) values.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd
import yfinance as yf

OHLCV_COLUMNS: list[str] = ["Open", "High", "Low", "Close", "Volume"]

DateLike = Union[str, date, datetime, pd.Timestamp]


def _format_date(d: Optional[DateLike], param_name: str) -> Optional[str]:
    """Normalize supported date inputs into YYYY-MM-DD string format."""
    if d is None:
        return None

    if isinstance(d, (datetime, date, pd.Timestamp)):
        return d.strftime("%Y-%m-%d")

    if isinstance(d, str):
        cleaned = d.strip()
        if not cleaned:
            return None
        try:
            parsed = pd.to_datetime(cleaned)
            return parsed.strftime("%Y-%m-%d")
        except Exception as exc:
            raise ValueError(
                f"Invalid date format for '{param_name}': '{d}'. "
                "Expected YYYY-MM-DD, ISO format, or a datetime object."
            ) from exc

    raise TypeError(
        f"Unsupported type for '{param_name}': {type(d).__name__}. "
        "Expected str, datetime.date, datetime.datetime, or pandas.Timestamp."
    )


def get_raw_ohlcv(
    stock: str,
    start_date: Optional[DateLike] = None,
    end_date: Optional[DateLike] = None,
    *,
    start: Optional[DateLike] = None,
    end: Optional[DateLike] = None,
    date_range: Optional[Union[Tuple[DateLike, DateLike], Sequence[DateLike]]] = None,
    interval: str = "1d",
    auto_adjust: bool = False,
    raise_if_empty: bool = True,
    as_format: str = "dataframe",
    **kwargs: Any,
) -> Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Fetch raw OHLCV (Open, High, Low, Close, Volume) data for any stock ticker using yfinance.

    Parameters
    ----------
    stock : str
        Stock ticker symbol (e.g. 'AAPL', 'MSFT', 'RELIANCE.NS', 'TCS.BO').
    start_date : str, date, datetime, or Timestamp, optional
        Start date of the requested range (inclusive).
    end_date : str, date, datetime, or Timestamp, optional
        End date of the requested range (inclusive/exclusive per Yahoo Finance API).
    start : str, date, datetime, or Timestamp, optional
        Alias for start_date.
    end : str, date, datetime, or Timestamp, optional
        Alias for end_date.
    date_range : tuple or sequence of 2 elements, optional
        Convenience parameter accepting (start_date, end_date).
    interval : str, default '1d'
        Data frequency. Supported values include:
        '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'.
    auto_adjust : bool, default False
        Whether to adjust OHLC prices for corporate splits/dividends.
        Defaults to False to ensure 100% raw unadjusted market prices.
    raise_if_empty : bool, default True
        If True, raises a ValueError if no data is returned for the given ticker and date range.
        If False, returns an empty DataFrame with OHLCV columns.
    as_format : {'dataframe', 'dict', 'records', 'json'}, default 'dataframe'
        Return data structure:
        - 'dataframe': pandas DataFrame with Date index and OHLCV columns.
        - 'dict': dictionary keyed by timestamp string.
        - 'records': list of record dictionaries with 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'.
        - 'json': JSON string representation.
    **kwargs : Any
        Additional keyword arguments forwarded to `yfinance.Ticker.history`.

    Returns
    -------
    pandas.DataFrame, dict, list of dicts, or str
        The requested raw OHLCV market data.

    Raises
    ------
    ValueError
        If stock symbol is missing/invalid, date range is inverted, or no data was retrieved.
    TypeError
        If date types cannot be parsed.
    """
    if not stock or not isinstance(stock, str) or not stock.strip():
        raise ValueError("A valid non-empty stock symbol string must be provided (e.g. 'AAPL', 'RELIANCE.NS').")

    ticker_symbol = stock.strip().upper()

    # Resolve date parameters
    resolved_start = start if start is not None else start_date
    resolved_end = end if end is not None else end_date

    if date_range is not None:
        if len(date_range) != 2:
            raise ValueError("date_range must be a tuple or sequence containing exactly 2 items: (start_date, end_date).")
        resolved_start = resolved_start if resolved_start is not None else date_range[0]
        resolved_end = resolved_end if resolved_end is not None else date_range[1]

    start_str = _format_date(resolved_start, "start_date")
    end_str = _format_date(resolved_end, "end_date")

    if start_str and end_str and start_str > end_str:
        raise ValueError(f"Start date ({start_str}) cannot be later than end date ({end_str}).")

    ticker = yf.Ticker(ticker_symbol)
    history_kwargs: Dict[str, Any] = {
        "interval": interval,
        "auto_adjust": auto_adjust,
        **kwargs,
    }
    if start_str is not None:
        history_kwargs["start"] = start_str
    if end_str is not None:
        history_kwargs["end"] = end_str

    # Fetch data
    df = ticker.history(**history_kwargs)

    # Flatten MultiIndex columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Validate returned data
    if df.empty:
        if raise_if_empty:
            range_info = f" between {start_str} and {end_str}" if start_str or end_str else ""
            raise ValueError(
                f"No OHLCV data found for stock '{ticker_symbol}'{range_info}. "
                "Verify ticker symbol and date range."
            )
        empty_df = pd.DataFrame(columns=OHLCV_COLUMNS)
        empty_df.index.name = "Date"
        return _format_output(empty_df, as_format)

    # Verify OHLCV columns exist
    missing_cols = [col for col in OHLCV_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required OHLCV columns from yfinance response for '{ticker_symbol}': {missing_cols}"
        )

    # Filter strictly to raw OHLCV columns
    df_ohlcv = df[OHLCV_COLUMNS].copy()

    # Clean index name
    if df_ohlcv.index.name is None:
        df_ohlcv.index.name = "Date"

    return _format_output(df_ohlcv, as_format)


def _format_output(
    df: pd.DataFrame, as_format: str
) -> Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]], str]:
    """Convert OHLCV DataFrame into desired output representation."""
    fmt = as_format.lower().strip()
    if fmt in ("dataframe", "df"):
        return df
    if fmt == "dict":
        return df.to_dict(orient="index")
    if fmt == "records":
        reset_df = df.reset_index()
        # Convert Timestamp to string ISO format if applicable
        if pd.api.types.is_datetime64_any_dtype(reset_df["Date"]):
            reset_df["Date"] = reset_df["Date"].astype(str)
        return reset_df.to_dict(orient="records")
    if fmt == "json":
        return df.to_json(orient="split", date_format="iso")
    raise ValueError(
        f"Unsupported as_format: '{as_format}'. Supported formats: 'dataframe', 'dict', 'records', 'json'."
    )


# API aliases for flexibility and ergonomic imports
get_stock_data = get_raw_ohlcv
get_raw_data = get_raw_ohlcv


def main() -> None:
    """CLI entry point for testing and quick data retrieval."""
    parser = argparse.ArgumentParser(description="Fetch raw OHLCV stock data using yfinance.")
    parser.add_argument("stock", type=str, help="Stock ticker symbol (e.g. AAPL, RELIANCE.NS)")
    parser.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=str, default="1d", help="Interval (default: 1d)")
    parser.add_argument(
        "--format",
        type=str,
        default="dataframe",
        choices=["dataframe", "dict", "records", "json"],
        help="Output format (default: dataframe)",
    )
    args = parser.parse_args()

    data = get_raw_ohlcv(
        stock=args.stock,
        start=args.start,
        end=args.end,
        interval=args.interval,
        as_format=args.format,
    )
    print(data)


if __name__ == "__main__":
    main()
