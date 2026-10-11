import numpy as np
import pandas as pd


def bollinger_bands(
    data: pd.DataFrame, period: int = 20, multiplier: float = 2.0
) -> pd.DataFrame:
    """Calculates Bollinger Bands (Middle, Upper, and Lower bands).

    Bollinger Bands consist of a Simple Moving Average (SMA) and upper/lower bands
    that are standard deviations away from the SMA.

    Args:
        data (pd.DataFrame): A pandas DataFrame containing at least a 'Close' column.
        period (int, optional): The lookback period for the SMA and standard deviation. Defaults to 20.
        multiplier (float, optional): The number of standard deviations for the upper/lower bands. Defaults to 2.0.

    Returns:
        pd.DataFrame: A new DataFrame with 'BB_Middle', 'BB_Upper', and 'BB_Lower' columns appended.
    """
    result = data.copy()

    result["BB_Middle"] = (
        result["Close"].rolling(window=period, min_periods=period).mean()
    )

    rolling_std = (
        result["Close"].rolling(window=period, min_periods=period).std()
    )

    result["BB_Upper"] = result["BB_Middle"] + (multiplier * rolling_std)
    result["BB_Lower"] = result["BB_Middle"] - (multiplier * rolling_std)

    return result


def average_true_range(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate the Average True Range (ATR) using textbook Wilder's smoothing.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV DataFrame containing 'High', 'Low', and 'Close' columns.
    period : int, default 14
        Smoothing lookback period. Must be a positive integer.

    Returns
    -------
    pd.DataFrame
        Copy of input DataFrame with an added 'ATR' column.
    """
    if (
        not isinstance(period, (int, np.integer))
        or isinstance(period, bool)
        or period <= 0
    ):
        raise ValueError("period must be a positive integer greater than 0.")

    for col in ["High", "Low", "Close"]:
        if col not in data.columns:
            raise ValueError(f"Required column '{col}' missing from DataFrame.")

    result = data.copy()

    if len(result) == 0:
        result["ATR"] = pd.Series(dtype=float)
        return result

    # 1. True Range calculation
    high = result["High"]
    low = result["Low"]
    prev_close = result["Close"].shift(1)

    hl = high - low
    hc = (high - prev_close).abs()
    lc = (low - prev_close).abs()

    # For bar >= 1, if any component is NaN, TR is NaN (skipna=False)
    # For the first bar (index 0), prev_close is NaN by definition, so TR is simply high - low
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = hl.iloc[0]

    # 2. Textbook Wilder's smoothing with SMA initialization
    tr_vals = tr.to_numpy(dtype=float)
    atr_vals = np.full(len(tr_vals), np.nan)

    if len(tr_vals) >= period:
        # First ATR value is arithmetic mean of first `period` True Ranges
        atr_vals[period - 1] = np.mean(tr_vals[:period])

        # Subsequent values use Wilder's recursive formula
        for i in range(period, len(tr_vals)):
            atr_vals[i] = (atr_vals[i - 1] * (period - 1) + tr_vals[i]) / period

    result["ATR"] = atr_vals
    return result

