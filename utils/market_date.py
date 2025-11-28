import math
import pandas as pd
import pandas_market_calendars as mcal
import pytz
from datetime import timedelta

ET = pytz.timezone("America/New_York")
NASDAQ = mcal.get_calendar("NASDAQ")

def _nasdaq_schedule(now_et: pd.Timestamp):
    """
    拉取 NASDAQ 交易日历（包含节假日/半日市）
    返回的 index 是 tz-naive 的 session dates（午夜时间戳）
    """
    return NASDAQ.schedule(
        start_date=(now_et.date() - timedelta(days=10)).isoformat(),
        end_date=(now_et.date() + timedelta(days=10)).isoformat()
    )


def is_market_open() -> bool:
    """
    NASDAQ 正股常规时段是否开盘中（9:30-16:00 ET，含半日市提前收盘）
    """
    now_et = pd.Timestamp.now(tz=ET)
    schedule = _nasdaq_schedule(now_et)

    today = pd.Timestamp(now_et.date())

    if today not in schedule.index:
        return False

    open_et = schedule.loc[today, "market_open"]
    close_et = schedule.loc[today, "market_close"]

    return open_et <= now_et <= close_et


def hours_from_open() -> int:
    """
    距离 NASDAQ 正股开盘几个小时（int）
    - 负数：还未开盘（到下一次开盘还有 |n| 小时）
    - 正数：已开盘（距离今天开盘已过去 n 小时）
    休市/周末：返回到下一交易日开盘的负数小时
    """
    now_et = pd.Timestamp.now(tz=ET)
    schedule = _nasdaq_schedule(now_et)

    today = pd.Timestamp(now_et.date())

    if today in schedule.index:
        open_et = schedule.loc[today, "market_open"]
    else:
        future = schedule.loc[schedule.index > today]
        open_et = future.iloc[0]["market_open"]

    diff_hours = (now_et - open_et).total_seconds() / 3600.0

    if diff_hours >= 0:
        return math.floor(diff_hours)
    else:
        return min(-1, math.ceil(diff_hours))

def hours_from_close() -> int:
    """
    距离 NASDAQ 正股收盘几个小时（int）
    - 负数：还未收盘（到这次收盘还有 |n| 小时）
    - 正数：已收盘（距离最近一次收盘已过去 n 小时）
    休市/周末：返回到下一交易日收盘的负数小时
    """
    now_et = pd.Timestamp.now(tz=ET)
    schedule = _nasdaq_schedule(now_et)

    today = pd.Timestamp(now_et.date())

    if today in schedule.index:
        close_et = schedule.loc[today, "market_close"]
    else:
        future = schedule.loc[schedule.index > today]
        close_et = future.iloc[0]["market_close"]

    diff_hours = (now_et - close_et).total_seconds() / 3600.0

    if diff_hours >= 0:
        return math.floor(diff_hours)
    else:
        return min(-1, math.ceil(diff_hours))
    
if __name__ == "__main__":
    print("NASDAQ 正股开盘中？", is_market_open())
    print("NASDAQ 距离开盘小时数:", hours_from_open())
    print("NASDAQ 距离收盘小时数:", hours_from_close())