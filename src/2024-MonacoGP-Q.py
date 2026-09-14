# 导入 FastF1 这个 Python 库
# FastF1 是专门用来获取和分析 F1 比赛数据的库
from typing import Any


import fastf1

# 导入 fastf1.plotting 模块，专门用来获取车手颜色
import fastf1.plotting 

# 从 Python 自带的 pathlib 模块中导入 Path
# Path 专门用来处理文件夹、文件路径
from pathlib import Path

# 导入 matplotlib 库，专门用来画图
import matplotlib.pyplot as plt

# 导入 plotly 库，专门用来画交互式图表
import plotly.graph_objects as go


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

"""
计算每个sector的时间差值，该值本身就在lap数据中。
A_fastest 和 B_fastest 这两个 Lap 对象，本身就带有
Sector1Time / Sector2Time / Sector3Time 三个字段
类型是 pandas 的 Timedelta，也就是"一段时间"，不是普通数字）
"""
sector_deltas = []

for i in [1,2,3]:
    # 用字符串拼接方式，动态取出三个计时段时间。
    col_name = f'Sector{i}Time'

    time_a = A_fastest[col_name]
    time_b = B_fastest[col_name]

    # 相减后转换成秒数表示
    diff = (time_a - time_b).total_seconds()

    # 把计时段时间差添加到列表中
    sector_deltas.append(diff)

# 打印每个sector的时间差值
# enumerate(列表, start=1)：这是 Python 内置函数，作用是"一边遍历列表，一边自动给你数第几个"。
# 正常 enumerate 是从 0 开始数（0,1,2...），加了 start=1 就告诉它"从 1 开始数"
for i, d in enumerate(sector_deltas, start=1):
    print(f"Sector {i} delta: {d:+.3f} s") # +.3f显示正负号，保留三位小数的浮点数
    print()



"""
get_car_data()：从这一圈里取出详细的遥测表格
跟之前 session.laps 那张"每圈一行"的表不一样，这张表是"这一圈里每个采样时刻一行"（采样率很高，一圈能有几百行）
列包括 Speed（速度）、Throttle（油门开度0-100）、Brake（刹车，开/关）、RPM、nGear（挡位）等。
"""
tel_a = A_fastest.get_car_data().add_distance()
tel_b = B_fastest.get_car_data().add_distance()


"""
# 画图，横轴是距离，纵轴是当前速度，标签是车手字母代码。
plt.plot(
    tel_a['Distance'],
    tel_a['Speed'],
    label= {A_fastest['Driver']}
    )
plt.plot(
    tel_b['Distance'],
    tel_b['Speed'],
    label= {B_fastest['Driver']}
    )

# 设置图的标题、横轴、纵轴、图例。
plt.xlabel('Distance (m)')
plt.ylabel('Speed (km/h)')
plt.title('2024 Monaco GP Q - Speed Comparison')
plt.legend()

# 显示图。
plt.show()
"""

"""
拿到两个车手对应的官方配色
fastf1.plotting.get_driver_color() 需要两个参数：
   1）车手的三字母代码，比如 'LEC'、'VER'（也可以用车号，看你装的 fastf1 版本）
   2）session 对象，因为同一个车手在不同年份/车队颜色可能不一样，所以要告诉函数"是哪一场比赛"
"""
color_a = fastf1.plotting.get_driver_color(A_fastest['Driver'], session)
color_b = fastf1.plotting.get_driver_color(B_fastest['Driver'], session)

"""
创建一个空白的 Plotly 图形对象
这个 fig 就相当于 matplotlib 里那块"画布"
之后所有的线、标题、坐标轴都往这个 fig 上面加
"""
fig = go.Figure()

"""
往 fig 里加两条线（每个车手一条）
go.Scatter() 用来画"散点图/折线图"，这里我们用它画速度曲线
参数说明：
    x=...       横轴数据，用刚才算好的距离（Distance）
    y=...       纵轴数据，用速度（Speed）
    mode='lines'  表示画成"线"，而不是一个个散点
    name=...    这条线在图例（legend）里显示的名字，用车手缩写
    line=dict(color=...)  给这条线指定颜色，用第 1 步拿到的官方配色
"""
fig.add_trace(go.Scatter(
    x=tel_a['Distance'],
    y=tel_a['Speed'],
    mode='lines',
    name=A_fastest['Driver'],
    line=dict(color=color_a),
    # hovertemplate：手动规定悬浮框里显示的格式，不再让 plotly 自己判断
    # %{y:.0f} 表示"y值，保留0位小数"（速度取整数就够了）
    # <extra></extra> 是用来删掉 plotly 默认多显示的那个"小方框"（本来会重复显示一次车手名字）
    hovertemplate=(
        f'{A_fastest["Driver"]}: '
        'X=%{x:.3f} m, '
        'Y=%{y:.0f} km/h'
        '<extra></extra>'
        )
))
fig.add_trace(go.Scatter(
    x=tel_b['Distance'],
    y=tel_b['Speed'],
    mode='lines',
    name=B_fastest['Driver'],
    line=dict(color=color_b),
    hovertemplate=(
        f'{B_fastest["Driver"]}: '
        'X=%{x:.3f} m, '
        'Y=%{y:.0f} km/h'
        '<extra></extra>'
        )
))

"""
设置标题、坐标轴名字、鼠标悬停效果
fig.update_layout() 是用来统一调整这张图"外观"的函数
title：整张图的标题
xaxis_title / yaxis_title：横轴、纵轴的名字（对应原来的 plt.xlabel / plt.ylabel）
hovermode='x unified'：
  鼠标移到图上时，会把"同一个横坐标位置"上所有线的数值
  一起显示在一个提示框里，方便同时对比两位车手在同一位置的速度
"""
fig.update_layout(
    title='2024 Monaco GP Q - Speed Comparison',
    xaxis_title='Distance (m)',
    yaxis_title='Speed (km/h)',
    hovermode='x unified'
)

# 显示图
fig.show()


# 用 Plotly 的 go.Table 把这三个差值做成一张表格图
# go.Table 是专门用来画"表格"的组件
table_fig = go.Figure(data=[go.Table(
    # header 是表头那一行
    header=dict(
        values=['Sector', f"{A_fastest['Driver']} (s)", f"{B_fastest['Driver']} (s)", 'Delta (s)'],
        fill_color='lightgrey',   # 表头背景色
        align='center'  # 表头内容居中对齐
    ),
    # cells 是表格主体内容，每一个 values 里的列表对应一"列"
    cells=dict(
        values=[
            ['Sector 1', 'Sector 2', 'Sector 3'],   # 第一列
            [A_fastest['Sector1Time'].total_seconds(),
             A_fastest['Sector2Time'].total_seconds(),
             A_fastest['Sector3Time'].total_seconds()], # 第二列
            [B_fastest['Sector1Time'].total_seconds(),
             B_fastest['Sector2Time'].total_seconds(),
             B_fastest['Sector3Time'].total_seconds()], # 第三列
            [f"{d:+.3f}" for d in sector_deltas]  # 第四列，每个delta前面带上正负号
        ],
        align='center'
    )
)])

table_fig.update_layout(title='Sector Time Comparison')
table_fig.show()  # 会单独弹出一个网页显示这张表