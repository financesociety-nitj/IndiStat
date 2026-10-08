import pandas as pd
import pytest
from indicator_library.volatility import bollinger_bands

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

def test_bollinger_bands_basic(dummy_price_data):
    result = bollinger_bands(dummy_price_data, period=20, std_dev=2.0)
    
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
