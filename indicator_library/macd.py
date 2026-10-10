"""
Moving Average Convergence Divergence (MACD) Indicator Implementation.
"""

from typing import Tuple
import pandas as pd


def calculate_macd(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_col: str = "Close",
    adjust: bool = False,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate the Moving Average Convergence Divergence (MACD) line, Signal line,
    and Histogram line.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing at least the `price_col` (e.g. 'Close').
    fast_period : int, default 12
        Lookback window for the fast exponential moving average. Must be > 0.
    slow_period : int, default 26
        Lookback window for the slow exponential moving average. Must be > fast_period.
    signal_period : int, default 9
        Lookback window for the signal exponential moving average. Must be > 0.
    price_col : str, default 'Close'
        The price column to use for calculations.
    adjust : bool, default False
        Whether to calculate EMA using exponentially weighted average (True)
        or recursive formulation (False, standard in technical analysis).

    Returns
    -------
    tuple of (pd.Series, pd.Series, pd.Series)
        Tuple containing (macd_line, signal_line, histogram_line).
    """
    if fast_period <= 0:
        raise ValueError("fast_period must be an integer greater than 0.")

    if slow_period <= 0:
        raise ValueError("slow_period must be an integer greater than 0.")

    if signal_period <= 0:
        raise ValueError("signal_period must be an integer greater than 0.")

    if fast_period >= slow_period:
        raise ValueError("fast_period must be strictly less than slow_period.")

    if price_col not in data.columns:
        raise ValueError(f"Required price column '{price_col}' missing from DataFrame.")

    price_series = data[price_col]

    # Calculate fast and slow EMAs
    fast_ema = price_series.ewm(span=fast_period, adjust=adjust).mean()
    slow_ema = price_series.ewm(span=slow_period, adjust=adjust).mean()

    # Calculate MACD line
    macd_line = fast_ema - slow_ema
    macd_line.name = "MACD"

    # Calculate Signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=adjust).mean()
    signal_line.name = "MACD_Signal"

    # Calculate MACD Histogram
    hist = macd_line - signal_line
    hist.name = "MACD_Hist"

    return macd_line, signal_line, hist


def macd(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_col: str = "Close",
    adjust: bool = False,
) -> pd.DataFrame:
    """
    Calculate the Moving Average Convergence Divergence (MACD) and return a new
    DataFrame with 'MACD', 'MACD_Signal', and 'MACD_Hist' columns.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing at least the `price_col` (e.g. 'Close').
    fast_period : int, default 12
        Lookback window for the fast exponential moving average. Must be > 0.
    slow_period : int, default 26
        Lookback window for the slow exponential moving average. Must be > fast_period.
    signal_period : int, default 9
        Lookback window for the signal exponential moving average. Must be > 0.
    price_col : str, default 'Close'
        The price column to use for calculations.
    adjust : bool, default False
        Whether to calculate EMA using exponentially weighted average (True)
        or recursive formulation (False, standard in technical analysis).

    Returns
    -------
    pd.DataFrame
        Copy of input DataFrame with added 'MACD', 'MACD_Signal', and 'MACD_Hist' columns.
    """
    result = data.copy()
    macd_line, signal_line, hist = calculate_macd(
        data=data,
        fast_period=fast_period,
        slow_period=slow_period,
        signal_period=signal_period,
        price_col=price_col,
        adjust=adjust,
    )

    result["MACD"] = macd_line
    result["MACD_Signal"] = signal_line
    result["MACD_Hist"] = hist

    return result


def moving_average_convergence_divergence(
    data: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_col: str = "Close",
    adjust: bool = False,
) -> pd.DataFrame:
    """
    Alias for macd.
    """
    return macd(
        data=data,
        fast_period=fast_period,
        slow_period=slow_period,
        signal_period=signal_period,
        price_col=price_col,
        adjust=adjust,
    )
