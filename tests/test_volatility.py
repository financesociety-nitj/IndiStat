import numpy as np
import pandas as pd
import pytest
from indicator_library import average_true_range, bollinger_bands


@pytest.fixture
def dummy_price_data():
    dates = pd.date_range("2024-01-01", periods=25, freq="D")
    df = pd.DataFrame(
        {
            "Open": [100.0] * 25,
            "High": [105.0] * 25,
            "Low": [95.0] * 25,
            # Increasing close prices to give a positive standard deviation
            "Close": [100.0 + i for i in range(25)],
            "Volume": [1000] * 25,
        },
        index=dates,
    )
    return df


@pytest.fixture
def sample_ohlcv_data():
    """Deterministic OHLCV sample dataset for ATR testing."""
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0, 12.0, 11.5, 13.0, 12.0],
            "High": [12.0, 13.0, 14.0, 13.0, 15.0, 14.0],
            "Low": [9.0, 10.0, 11.0, 10.0, 12.0, 11.0],
            "Close": [11.0, 12.0, 11.5, 12.5, 13.5, 12.0],
            "Volume": [100, 150, 200, 180, 220, 210],
        }
    )


# --- Bollinger Bands Tests ---

def test_bollinger_bands_basic(dummy_price_data):
    result = bollinger_bands(dummy_price_data, period=20, multiplier=2.0)

    # 1. Ensure we did not mutate original dataframe
    assert "BB_Middle" not in dummy_price_data.columns

    # 2. Check the columns are successfully added
    assert "BB_Middle" in result.columns
    assert "BB_Upper" in result.columns
    assert "BB_Lower" in result.columns

    # 3. Check for NaNs due to rolling window (first 19 days should be NaN for period=20)
    assert pd.isna(result["BB_Middle"].iloc[18])
    assert not pd.isna(result["BB_Middle"].iloc[19])

    # 4. Check the math logic for a specific point
    assert result["BB_Upper"].iloc[20] > result["BB_Middle"].iloc[20]
    assert result["BB_Lower"].iloc[20] < result["BB_Middle"].iloc[20]


# --- Average True Range (ATR) Tests ---

def test_atr_exact_wilder_values():
    # 3-period ATR with hand-calculated values:
    # Row 0: H=12, L=9,  C=11   -> TR0 = 12 - 9 = 3.0
    # Row 1: H=13, L=10, C=12   -> TR1 = max(13-10=3, |13-11|=2, |10-11|=1) = 3.0
    # Row 2: H=14, L=11, C=11.5 -> TR2 = max(14-11=3, |14-12|=2, |11-12|=1) = 3.0
    # Row 3: H=13, L=10, C=12.5 -> TR3 = max(13-10=3, |13-11.5|=1.5, |10-11.5|=1.5) = 3.0
    df = pd.DataFrame(
        {
            "High": [12.0, 13.0, 14.0, 13.0],
            "Low": [9.0, 10.0, 11.0, 10.0],
            "Close": [11.0, 12.0, 11.5, 12.5],
        }
    )
    res = average_true_range(df, period=3)

    # First 2 values must be NaN
    assert pd.isna(res["ATR"].iloc[0])
    assert pd.isna(res["ATR"].iloc[1])

    # 3rd value (index 2) must be SMA: (3.0 + 3.0 + 3.0) / 3 = 3.0
    assert pytest.approx(res["ATR"].iloc[2], rel=1e-5) == 3.0

    # 4th value (index 3) uses Wilder's recursion: (3.0 * 2 + 3.0) / 3 = 3.0
    assert pytest.approx(res["ATR"].iloc[3], rel=1e-5) == 3.0


def test_atr_period_one(sample_ohlcv_data):
    res = average_true_range(sample_ohlcv_data, period=1)
    # Row 0: H=12, L=9 -> TR = 3.0
    assert pytest.approx(res["ATR"].iloc[0]) == 3.0
    assert not res["ATR"].isna().any()


def test_atr_period_longer_than_input(sample_ohlcv_data):
    res = average_true_range(sample_ohlcv_data, period=20)
    assert res["ATR"].isna().all()
    assert len(res) == len(sample_ohlcv_data)


def test_atr_empty_dataframe():
    empty_df = pd.DataFrame(columns=["High", "Low", "Close"])
    res = average_true_range(empty_df, period=14)
    assert "ATR" in res.columns
    assert len(res) == 0


def test_atr_missing_required_columns():
    df_missing_high = pd.DataFrame({"Low": [10.0], "Close": [11.0]})
    with pytest.raises(ValueError, match="Required column 'High' missing"):
        average_true_range(df_missing_high, period=14)


@pytest.mark.parametrize("invalid_period", [0, -5, 2.5, "14", True, False, None])
def test_atr_invalid_period(sample_ohlcv_data, invalid_period):
    with pytest.raises(ValueError, match="period must be a positive integer"):
        average_true_range(sample_ohlcv_data, period=invalid_period)


def test_atr_accepts_numpy_integer(sample_ohlcv_data):
    res = average_true_range(sample_ohlcv_data, period=np.int64(2))
    assert not pd.isna(res["ATR"].iloc[1])


def test_atr_immutability(sample_ohlcv_data):
    original_cols = list(sample_ohlcv_data.columns)
    _ = average_true_range(sample_ohlcv_data, period=3)
    assert list(sample_ohlcv_data.columns) == original_cols
    assert "ATR" not in sample_ohlcv_data.columns


def test_atr_nan_propagation(sample_ohlcv_data):
    corrupted_data = sample_ohlcv_data.copy()
    corrupted_data.loc[1, "High"] = np.nan
    res = average_true_range(corrupted_data, period=3)
    # The SMA of first 3 values includes NaN at index 1 -> ATR at index 2 must be NaN
    assert pd.isna(res["ATR"].iloc[2])


def test_atr_top_level_import():
    import indicator_library as il
    assert hasattr(il, "average_true_range")

