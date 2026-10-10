import pandas as pd
import pytest

from indicator_library.macd import (
    calculate_macd,
    macd,
    moving_average_convergence_divergence,
)


@pytest.fixture
def dummy_price_data():
    dates = pd.date_range("2024-01-01", periods=50, freq="D")
    return pd.DataFrame(
        {
            "Open": [100.0] * 50,
            "High": [105.0] * 50,
            "Low": [95.0] * 50,
            "Close": [100.0 + i for i in range(50)],
            "Volume": [1000] * 50,
        },
        index=dates,
    )


def test_macd_basic(dummy_price_data):
    result = macd(dummy_price_data, fast_period=12, slow_period=26, signal_period=9)

    # 1. Ensure input DataFrame is not mutated
    assert "MACD" not in dummy_price_data.columns
    assert "MACD_Signal" not in dummy_price_data.columns
    assert "MACD_Hist" not in dummy_price_data.columns

    # 2. Ensure new columns are present
    assert "MACD" in result.columns
    assert "MACD_Signal" in result.columns
    assert "MACD_Hist" in result.columns

    # 3. Check mathematical identity: Hist = MACD - Signal
    expected_hist = result["MACD"] - result["MACD_Signal"]
    pd.testing.assert_series_equal(
        result["MACD_Hist"], expected_hist, check_names=False
    )


def test_macd_flat_prices():
    df = pd.DataFrame({"Close": [100.0] * 35})
    result = macd(df, fast_period=12, slow_period=26, signal_period=9)

    assert (result["MACD"] == 0.0).all()
    assert (result["MACD_Signal"] == 0.0).all()
    assert (result["MACD_Hist"] == 0.0).all()


def test_macd_rising_prices():
    df = pd.DataFrame({"Close": [100.0 + i for i in range(40)]})
    result = macd(df, fast_period=12, slow_period=26, signal_period=9)

    # In a steady uptrend, fast EMA > slow EMA after initial step, so MACD > 0
    assert (result["MACD"].iloc[1:] > 0.0).all()


def test_macd_falling_prices():
    df = pd.DataFrame({"Close": [100.0 - i for i in range(40)]})
    result = macd(df, fast_period=12, slow_period=26, signal_period=9)

    # In a steady downtrend, fast EMA < slow EMA after initial step, so MACD < 0
    assert (result["MACD"].iloc[1:] < 0.0).all()


def test_macd_invalid_periods():
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})

    with pytest.raises(ValueError, match="fast_period"):
        macd(df, fast_period=0)

    with pytest.raises(ValueError, match="slow_period"):
        macd(df, slow_period=0)

    with pytest.raises(ValueError, match="signal_period"):
        macd(df, signal_period=0)

    with pytest.raises(ValueError, match="fast_period must be strictly less"):
        macd(df, fast_period=26, slow_period=12)

    with pytest.raises(ValueError, match="fast_period must be strictly less"):
        macd(df, fast_period=20, slow_period=20)


def test_macd_missing_close_column():
    df = pd.DataFrame({"Open": [100.0, 101.0, 102.0]})

    with pytest.raises(ValueError, match="Close"):
        macd(df)


def test_calculate_macd_series_tuple(dummy_price_data):
    macd_line, signal_line, hist = calculate_macd(
        dummy_price_data, fast_period=12, slow_period=26, signal_period=9
    )

    assert isinstance(macd_line, pd.Series)
    assert isinstance(signal_line, pd.Series)
    assert isinstance(hist, pd.Series)
    assert macd_line.name == "MACD"
    assert signal_line.name == "MACD_Signal"
    assert hist.name == "MACD_Hist"
    pd.testing.assert_series_equal(hist, macd_line - signal_line, check_names=False)


def test_moving_average_convergence_divergence_alias(dummy_price_data):
    res_macd = macd(dummy_price_data)
    res_alias = moving_average_convergence_divergence(dummy_price_data)

    pd.testing.assert_frame_equal(res_macd, res_alias)


def test_custom_price_column():
    df = pd.DataFrame(
        {
            "Open": [100.0 + i for i in range(30)],
            "Close": [50.0] * 30,
        }
    )

    result = macd(df, price_col="Open")
    assert (result["MACD"].iloc[1:] > 0.0).all()
