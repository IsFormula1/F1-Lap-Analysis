# 导入 FastF1 这个 Python 库
# FastF1 是专门用来获取和分析 F1 比赛数据的库
import fastf1


# 从 Python 自带的 pathlib 模块中导入 Path
# Path 专门用来处理文件夹、文件路径
from pathlib import Path

"""
============================================================
第 1 部分：确定数据缓存（cache）放在哪里
============================================================
__file__ 表示“当前正在运行的这个 Python 文件”
那么：
Path(__file__)
     ↓
当前文件的路径

.resolve()
     ↓
把它变成完整的绝对路径

.parent
     ↓
当前文件所在的文件夹，也就是 src

.parent
     ↓
再往上一层，也就是项目根目录

所以 PROJECT_ROOT 最后就是：
F1-Lap-Analysis/
"""
PROJECT_ROOT = Path(__file__).resolve().parent.parent

"""
在项目根目录下面，再指定一个叫 cache 的文件夹
如果 PROJECT_ROOT 是：
D:\IsF1\F1-Lap-Analysis
那么：
CACHE_DIR 就是：
D:\IsF1\F1-Lap-Analysis\cache
"""
CACHE_DIR = PROJECT_ROOT / 'cache'

"""
创建 cache 文件夹
exist_ok=True 的意思是：
如果 cache 已经存在 → 什么也不做，不报错
如果 cache 不存在 → 自动创建
"""
CACHE_DIR.mkdir(exist_ok=True)

"""
告诉 FastF1：
“以后你下载的数据，都缓存到这个 cache 文件夹里面。”
str(CACHE_DIR)
是把 Path 对象转换成字符串路径
"""
fastf1.Cache.enable_cache(str(CACHE_DIR))


"""
============================================================
第 2 部分：告诉 FastF1，我想要哪一场比赛
============================================================
获取 2024 年摩纳哥大奖赛（Monaco）的排位赛
这里得到的 session 可以理解成：
“2024 摩纳哥大奖赛排位赛”这场比赛数据的一个对象/入口
注意：
这一行主要是在“指定我要哪场比赛”
并不意味着所有遥测数据已经下载下来了。
"""
session = fastf1.get_session(2024, 'Monaco', 'Q')


"""
============================================================
第 3 部分：真正加载这场比赛的数据
============================================================


真正开始加载数据

 FastF1 会根据刚才指定的比赛：
 2024
 ↓
 Monaco
 ↓
 Qualifying
 去获取这场排位赛的数据。
 如果 cache 里面已经有数据：
     → 优先使用缓存，速度比较快
 如果 cache 里面没有：
     → FastF1 会从数据源下载
 加载完成以后，session.laps 等数据才可以使用。
"""
session.load()
print()


"""
session.laps 是那张大表，['DriverNumber'] 取出车号这一列，
.unique() 是pandas的方法，作用是"去重":
一场比赛一个车手跑几十圈，车号会重复很多次，
.unique() 帮你只留下不重复的那几个值，方便你看这场比赛一共有哪些车参赛
"""
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

"""
打印比赛名称
session.event
    → 这场比赛的赛事信息
['EventName']
    → 从赛事信息里面拿出比赛名称
session.name
    → 当前 session 的名字
所以最终可能打印类似：
已加载：Monaco Grand Prix Qualifying
"""
# print(f"已加载：{session.event['EventName']} {session.name}")


"""
打印圈速数据的前 5 行
session.laps
    → 这场排位赛的所有圈速数据
.head()
    → 只看前 5 行
所以这里相当于：
“把刚才加载出来的圈速数据，先给我看看前五条。”
"""
# print(session.laps.head())