import pandas as pd
def bollinger_bands(data:pd.DataFrame, period: int =20, std_dev: float=2) -> pd.DataFrame:
    result=data.copy()

    result['BB_Middle'] = result['Close'].rolling(
        window=period,
        min_periods=period
    ).mean()

    rolling_std = result['Close'].rolling(
        window=period,
        min_periods=period
    ).std()

    result['BB_Upper'] = result['BB_Middle'] + (std_dev * rolling_std)

    result['BB_Lower'] = result['BB_Middle'] - (std_dev * rolling_std)

    return result