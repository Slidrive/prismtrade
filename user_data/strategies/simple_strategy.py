import talib
from freqtrade.strategy import IStrategy
from pandas import DataFrame

class SimpleStrategy(IStrategy):
    STAKE_CURRENCY = "USDT"
    TIMEFRAME = "15m"
    CAN_SHORT = False

    minimal_roi = {"0": 0.10}
    stoploss = -0.10
    trailing_stop = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = talib.RSI(dataframe["close"], timeperiod=14)
        dataframe["sma_20"] = talib.SMA(dataframe["close"], timeperiod=20)
        dataframe["sma_50"] = talib.SMA(dataframe["close"], timeperiod=50)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] < 30) &
                (dataframe["sma_20"] > dataframe["sma_50"]) &
                (dataframe["volume"] > 0)
            ),
            "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > 70) |
                (dataframe["sma_20"] < dataframe["sma_50"])
            ),
            "exit_long"] = 1
        return dataframe