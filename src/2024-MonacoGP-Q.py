from typing import Any

# 导入 FastF1 这个 Python 库
# FastF1 是专门用来获取和分析 F1 比赛数据的库
import fastf1

# 从 Python 自带的 pathlib 模块中导入 Path
# Path 专门用来处理文件夹、文件路径
from pathlib import Path

from plotting import build_telemetry_data_chart


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CACHE_DIR = PROJECT_ROOT / 'cache'

CACHE_DIR.mkdir(exist_ok=True)

fastf1.Cache.enable_cache(str(CACHE_DIR))


session = fastf1.get_session(2024, 'Monaco', 'Q')

session.load()
print()

# print(session.laps['DriverNumber'].unique())

# 找出勒克莱尔的最快圈，包含各种参数的，比如每一个计时段。
A_fastest = session.laps.pick_drivers('16').pick_fastest()

# 找出维斯塔潘的最快圈，包含各种参数的，比如每一个计时段。
B_fastest = session.laps.pick_drivers('1').pick_fastest()

"""
print(A_fastest)
print()
print(B_fastest)
"""

# 将两个人的最快整圈速提取出来。
lap_time_a = A_fastest['LapTime']
lap_time_b = B_fastest['LapTime']

# 计算delta差值。
delta = lap_time_a - lap_time_b
print(f"{A_fastest['Driver']} - {B_fastest['Driver']} = {delta.total_seconds()}")
# print(delta)

# print(f"已加载：{session.event['EventName']} {session.name}")

# print(session.laps.head())

fig = build_telemetry_data_chart(session, ['LEC', 'VER'])
fig.show()