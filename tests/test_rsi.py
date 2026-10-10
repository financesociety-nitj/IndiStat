
import pandas as pd
import pytest

from indicator_library.rsi import calculate_rsi, relative_strength_index


@pytest.fixture
def dummy_price_data():
    dates = pd.date_range("2024-01-01", periods=25, freq="D")
    return pd.DataFrame(
        {
            "Open": [100.0] * 25,
            "High": [105.0] * 25,
            "Low": [95.0] * 25,
            "Close": [100.0 + i for i in range(25)],
            "Volume": [1000] * 25,
        },
        index=dates,
    )


def test_rsi_basic(dummy_price_data):
    result = relative_strength_index(dummy_price_data, period=14)

    assert "RSI" not in dummy_price_data.columns
    assert "RSI" in result.columns
    assert pd.isna(result["RSI"].iloc[13])
    assert not pd.isna(result["RSI"].iloc[14])
    assert result["RSI"].dropna().between(0, 100).all()


def test_rsi_rising_prices():
    df = pd.DataFrame({"Close": list(range(100, 130))})

    result = relative_strength_index(df, period=14)

    assert result["RSI"].dropna().iloc[-1] == pytest.approx(100.0)


def test_rsi_falling_prices():
    df = pd.DataFrame({"Close": list(range(130, 100, -1))})

    result = relative_strength_index(df, period=14)

    assert result["RSI"].dropna().iloc[-1] == pytest.approx(0.0)


def test_rsi_flat_prices():
    df = pd.DataFrame({"Close": [100.0] * 25})

    result = relative_strength_index(df, period=14)

    assert (result["RSI"].dropna() == 50.0).all()


def test_invalid_period():
    df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]})

    with pytest.raises(ValueError):
        relative_strength_index(df, period=0)


def test_missing_close_column():
    df = pd.DataFrame({"Open": [100.0, 101.0, 102.0]})

    with pytest.raises(ValueError, match="Close"):
        relative_strength_index(df)


def test_calculate_rsi_series(dummy_price_data):
    rsi_series = calculate_rsi(dummy_price_data, period=14)

    assert isinstance(rsi_series, pd.Series)
    assert pd.isna(rsi_series.iloc[13])
    assert not pd.isna(rsi_series.iloc[14])
    assert rsi_series.dropna().between(0, 100).all()

