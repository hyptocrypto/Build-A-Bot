# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# --------------------------------


class BollingerRSI(IStrategy):
    """
    Buy the low end of bollinger band if RSI is oversold
    Short the high end of bollinger band if RSI is overbought
    """

    INTERFACE_VERSION: int = 3
    # Minimal ROI designed for the strategy.
    # adjust based on market conditions. We would recommend to keep it low for quick turn arounds
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {"0": 0.1}

    # Optimal stoploss designed for the strategy
    stoploss = -0.1
    # Optimal timeframe for the strategy
    timeframe = "1h"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(
            qtpylib.typical_price(dataframe), window=20, stds=2
        )
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] <= 35)
                & (dataframe["close"] < dataframe["bb_lowerband"])
            ),
            "enter_long",
        ] = 1

        dataframe.loc[
            (
                (dataframe["rsi"] >= 65)
                & (dataframe["close"] < dataframe["bb_lowerband"])
            ),
            "enter_short",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[((dataframe["rsi"] > 70)), "exit_long"] = 1
        dataframe.loc[((dataframe["rsi"] < 30)), "exit_short"] = 1
        return dataframe
