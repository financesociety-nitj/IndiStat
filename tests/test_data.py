"""Unit tests for the OHLCV stock data fetching API."""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from indicator_library.data import (
    OHLCV_COLUMNS,
    _format_date,
    get_raw_data,
    get_raw_ohlcv,
    get_stock_data,
)


@pytest.fixture
def mock_history_df():
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    df = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [105.0, 106.0, 107.0, 108.0, 109.0],
            "Low": [95.0, 96.0, 97.0, 98.0, 99.0],
            "Close": [102.0, 103.0, 104.0, 105.0, 106.0],
            "Adj Close": [101.5, 102.5, 103.5, 104.5, 105.5],
            "Volume": [1000, 1100, 1200, 1300, 1400],
            "Dividends": [0.0, 0.0, 0.0, 0.0, 0.0],
            "Stock Splits": [0.0, 0.0, 0.0, 0.0, 0.0],
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


def test_format_date():
    assert _format_date(None, "param") is None
    assert _format_date("2024-01-15", "param") == "2024-01-15"
    assert _format_date(date(2024, 1, 15), "param") == "2024-01-15"
    assert _format_date(datetime(2024, 1, 15, 10, 30), "param") == "2024-01-15"
    assert _format_date(pd.Timestamp("2024-01-15"), "param") == "2024-01-15"

    with pytest.raises(ValueError):
        _format_date("invalid-date-string", "param")

    with pytest.raises(TypeError):
        _format_date(12345, "param")


@patch("yfinance.Ticker")
def test_get_raw_ohlcv_columns_only(mock_ticker_cls, mock_history_df):
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_history_df
    mock_ticker_cls.return_value = mock_instance

    result = get_raw_ohlcv("AAPL", start_date="2024-01-01", end_date="2024-01-05")

    # Verify only OHLCV columns exist
    assert list(result.columns) == OHLCV_COLUMNS
    assert "Dividends" not in result.columns
    assert "Stock Splits" not in result.columns
    assert "Adj Close" not in result.columns
    assert len(result) == 5

    mock_ticker_cls.assert_called_once_with("AAPL")
    mock_instance.history.assert_called_once_with(
        start="2024-01-01",
        end="2024-01-05",
        interval="1d",
        auto_adjust=False,
    )


@patch("yfinance.Ticker")
def test_get_raw_ohlcv_date_range_tuple(mock_ticker_cls, mock_history_df):
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_history_df
    mock_ticker_cls.return_value = mock_instance

    result = get_stock_data("msft", date_range=("2024-01-01", "2024-01-05"))
    assert list(result.columns) == OHLCV_COLUMNS
    mock_ticker_cls.assert_called_once_with("MSFT")


@patch("yfinance.Ticker")
def test_get_raw_ohlcv_date_objects(mock_ticker_cls, mock_history_df):
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_history_df
    mock_ticker_cls.return_value = mock_instance

    d_start = date(2024, 1, 1)
    d_end = datetime(2024, 1, 5)
    result = get_raw_data("GOOGL", start=d_start, end=d_end)
    assert list(result.columns) == OHLCV_COLUMNS
    mock_instance.history.assert_called_once_with(
        start="2024-01-01",
        end="2024-01-05",
        interval="1d",
        auto_adjust=False,
    )


def test_invalid_stock_input():
    with pytest.raises(ValueError, match="valid non-empty stock symbol"):
        get_raw_ohlcv("")
    with pytest.raises(ValueError, match="valid non-empty stock symbol"):
        get_raw_ohlcv("   ")
    with pytest.raises(ValueError, match="valid non-empty stock symbol"):
        get_raw_ohlcv(None)


def test_invalid_date_ordering():
    with pytest.raises(ValueError, match="cannot be later than end date"):
        get_raw_ohlcv("AAPL", start_date="2024-02-01", end_date="2024-01-01")


@patch("yfinance.Ticker")
def test_empty_data_raises_or_returns(mock_ticker_cls):
    mock_instance = MagicMock()
    mock_instance.history.return_value = pd.DataFrame()
    mock_ticker_cls.return_value = mock_instance

    with pytest.raises(ValueError, match="No OHLCV data found"):
        get_raw_ohlcv("INVALIDTICKER123", raise_if_empty=True)

    empty_res = get_raw_ohlcv("INVALIDTICKER123", raise_if_empty=False)
    assert isinstance(empty_res, pd.DataFrame)
    assert list(empty_res.columns) == OHLCV_COLUMNS
    assert len(empty_res) == 0


@patch("yfinance.Ticker")
def test_output_formats(mock_ticker_cls, mock_history_df):
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_history_df
    mock_ticker_cls.return_value = mock_instance

    # records format
    records = get_raw_ohlcv("AAPL", as_format="records")
    assert isinstance(records, list)
    assert len(records) == 5
    assert "Open" in records[0]
    assert "Close" in records[0]

    # dict format
    d = get_raw_ohlcv("AAPL", as_format="dict")
    assert isinstance(d, dict)

    # json format
    j = get_raw_ohlcv("AAPL", as_format="json")
    assert isinstance(j, str)
    assert "Open" in j


def test_top_level_imports():
    from indicator_library import OHLCV_COLUMNS as IL_COLS
    from indicator_library import get_raw_data as il_get_raw
    from indicator_library import get_raw_ohlcv as il_get_ohlcv
    from indicator_library import get_stock_data as il_get_stock

    assert IL_COLS == OHLCV_COLUMNS
    assert il_get_raw is get_raw_data
    assert il_get_ohlcv is get_raw_ohlcv
    assert il_get_stock is get_stock_data
