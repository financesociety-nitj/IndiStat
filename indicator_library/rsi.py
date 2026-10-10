"""
Relative Strength Index (RSI) Indicator Implementation.
"""

import pandas as pd


def calculate_rsi(
    data: pd.DataFrame,
    period: int = 14,
    price_col: str = "Close",
) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a given OHLCV DataFrame.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing at least the `price_col` (e.g. 'Close').
    period : int, default 14
        The lookback window for RSI calculation. Must be greater than 0.
    price_col : str, default 'Close'
        The price column to use for calculations.

    Returns
    -------
    pd.Series
        Series containing the RSI values oscillating between 0 and 100.
    """
    if period <= 0:
        raise ValueError("period must be an integer greater than 0.")

    if price_col not in data.columns:
        raise ValueError(f"Required price column '{price_col}' missing from DataFrame.")

    # Calculate price change
    delta = data[price_col].diff()

    # Separate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Use Wilder's smoothing (exponential moving average with alpha = 1 / period)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    # Calculate Relative Strength (RS)
    rs = avg_gain / avg_loss

    # Calculate RSI: 100 - (100 / (1 + RS))
    rsi = 100.0 - (100.0 / (1.0 + rs))

    # Where avg_loss == 0, RSI is 100
    rsi = rsi.where(avg_loss != 0, 100.0)

    # Where both avg_gain == 0 and avg_loss == 0 (flat prices), RSI is 50
    rsi = rsi.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)

    rsi.name = "RSI"
    return rsi


def relative_strength_index(
    data: pd.DataFrame,
    period: int = 14,
    price_col: str = "Close",
) -> pd.DataFrame:
    """
    Calculate the Relative Strength Index (RSI) and return a new DataFrame with the 'RSI' column.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing at least the `price_col` (e.g. 'Close').
    period : int, default 14
        The lookback window for RSI calculation. Must be greater than 0.
    price_col : str, default 'Close'
        The price column to use for calculations.

    Returns
    -------
    pd.DataFrame
        Copy of input DataFrame with an added 'RSI' column.
    """
    if period <= 0:
        raise ValueError("period must be an integer greater than 0.")

    if price_col not in data.columns:
        raise ValueError(f"Required price column '{price_col}' missing from DataFrame.")

    result = data.copy()
    result["RSI"] = calculate_rsi(data, period=period, price_col=price_col)
    return result
