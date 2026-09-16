"""
plotting.py
存放所有跟"画图"相关的函数。
以后分析别的比赛，直接 import 这里的函数，不用重写一遍画图代码。
"""
# 导入 fastf1.plotting 模块，专门用来获取车手颜色
import fastf1.plotting

# 导入 plotly 库，专门用来画交互式图表
import plotly.graph_objects as go

# 导入 plotly.subplots 模块，专门用来创建子图，用来合并图片。
from plotly.subplots import make_subplots

# 形参用车手缩写的原因是：fastf1.plotting.get_driver_color('16', session)：
# 官方文档写得很清楚，这个函数的 identifier 参数要求是"车手缩写，或者车手姓名里能辨认出来的一部分"，不支持车号。
# 如果传车号进去，大概率会报错或者匹配不到颜色。
# 所以改成车手缩写比较好。
def build_telemetry_data_chart(session, driver_codes):
    """
    生成一张"速度对比折线图 + sector 时间对比表格"的组合图。

    参数：
        session：已经 session.load() 过的 session 对象，函数内部不关心这是哪场比赛
        driver_codes：车手代码列表，例如 ['LEC', 'VER']
            - 折线图部分支持任意数量车手（2个、3个都行），内部用循环处理
            - 表格部分算的是"两者之间的 delta"，这个概念天然只能是两两比较，
              所以只有传入正好 2 个车手时才会画表格；传 3 个及以上就只画折线图，
              不报错，但不会有表格

    返回：
        一个 plotly 的 Figure 对象。函数内部不调用 .show()，
        显示/存文件这些决定权留给调用方，函数只负责"画好图"。
    """

# --- 第一步：把每个车手的最快圈 + 遥测数据 + 官方配色，先统一收集好 ---
    # 用一个列表装若干个"小字典"，每个字典对应一个车手的全部信息
    # 这样后面无论循环几次（2个车手还是5个车手），逻辑都一样，不用写死
    driver_data = []
    for code in driver_codes:
        lap = session.laps.pick_drivers(code).pick_fastest()        # 获取最快圈
        tel = lap.get_car_data().add_distance()                     # 获取遥测数据添加一列对应的的距离信息
        color = fastf1.plotting.get_driver_color(code, session)     # 获取官方配色
        
        # 将上面获取的数据添加到列表中
        driver_data.append({
            'code': code,
            'lap': lap,                                              # 最快圈
            'tel': tel,                                              # 遥测数据
            'color': color                                          # 官方配色
        })




# --- 第二步：根据车手数量，决定要不要留出表格的位置 ---
    # len()函数返回列表中元素的个数
    show_table = (len(driver_codes) == 2)   # 如果车手数量是2个，则为True，否则为False
    
    # 如果show_table为True，则画表格
    if show_table:  
        """
        rows = 2, cols = 1：整体分成上下两行，每行一列（把整张图想象成一个大表格，一个图占一格，也就是上下堆叠）
        row_heights：控制两行的高度比例，[0.7, 0.3] 表示上面那行占 70% 高度，下面占 30%
        specs：逐行逐列声明每个格子的类型
             第一行第一列 → {"type": "xy"}      普通折线图
            第二行第一列 → {"type": "table"}   表格
        subplot_titles：给每个子图单独加一个小标题
        """
        fig = make_subplots(    # 创建一个2行1列的子图，也就是上下两部分
            rows = 2, cols = 1,
            row_heights = [0.6, 0.4],
            vertical_spacing=0.20,  # 增大上下子图间距
            specs = [[{"type": "xy"}], [{"type": "table"}]],
            subplot_titles = ("Speed Comparison", "Sector Time Comparison")
        )
    # 车手数量不是2个时，只画一行折线图，没有表格
    else:
        fig = make_subplots(    # 创建一个1行1列的子图，也就是整张图是一个子图
            rows = 1, cols = 1,
            specs = [[{"type": "xy"}]],
            subplot_titles = ("Speed Comparison",)
        )




# --- 第三步：画折线图，循环处理，支持任意数量车手 ---
    for d in driver_data:
        # 添加一条曲线
        fig.add_trace(go.Scatter(   # go.Scatter() 用来画"散点图/折线图"，这里我们用它画速度曲线
            x = d['tel']['Distance'], # 横轴是距离
            y = d['tel']['Speed'],    # 纵轴是速度
            mode = 'lines',
            name = d['code'],
            line = dict(color = d['color']),    # 给曲线指定颜色，用第 1 步拿到的官方配色
            # hovertemplate：手动规定悬浮框里显示的格式，不再让 plotly 自己判断
            # %{y:.0f} 表示"y值，保留0位小数"（速度取整数就够了）
            # <extra></extra> 是用来删掉 plotly 默认多显示的那个"小方框"（本来会重复显示一次车手名字）
            hovertemplate = (
                f"{d['code']}: "
                'X = %{x:.3f} m, '
                'Y = %{y:.0f} km/h'
                '<extra></extra>'
            )
        ), row = 1, col = 1) # 把曲线加到整张图的第一行第一列（整体的话就只有这一张图，上下两部分的话也就是上半部分）




# --- 第三步补充：在速度图上用竖虚线标出每个弯道的位置 ---
    """
    session.get_circuit_info() 返回这条赛道的"赛道信息"对象，
    这个信息只跟赛道有关，跟车手是谁无关（所以不需要放进上面那个车手循环里）。

    circuit_info.corners 是一张表（DataFrame），每一行代表赛道上的一个弯，
    要用到的三列是：
        Distance —— 这个弯距离起跑线多少米，正好能对上速度图横轴的单位
        Number   —— 弯道编号（1、2、3...）
        Letter   —— 有些弯会拆成 7A、7B 这种，这一列就是那个字母；
                    大部分弯这一列是空字符串，拼上去也不影响
    """
    circuit_info = session.get_circuit_info()
    corners = circuit_info.corners

    """
    先给 y 轴（速度）上方留一块空白，专门用来放弯道编号。
    max(...) 里面是一个"生成器表达式，作用是：遍历每个车手的遥测数据，各取出速度的最大值，再从这些最大值里取最大的那个。
    等价于下面这样写：
        speeds = []
        for d in driver_data:
            speeds.append(d['tel']['Speed'].max())
        max_speed = max(speeds)
    乘以 1.12 就是"在最高速度基础上再往上留 12% 的空间"，
    这块空白区域没有曲线，正好用来放编号，不会跟数据打架。
    
    max_speed = max(d['tel']['Speed'].max() for d in driver_data)

    # 设置y轴范围，留出空白区域用来放弯道编号
    fig.update_yaxes(range = [0, max_speed * 1.12], row = 1, col = 1)
    """

    """
    corners.iterrows() 是 pandas 的方法，作用是"一行一行地遍历这张表"。
    它每次返回两个东西：(这一行的索引, 这一行的数据)
    我们只关心"这一行的数据"，不关心索引，
    所以第一个变量写成 _ （下划线），这是 Python 的惯例，表示"这个值我拿到了但用不上"
    """
    for _, corner in corners.iterrows():

        # 把编号和字母拼成显示用的文本，例如 '1'、'7A'
        corner_label = f"T{int(corner['Number'])}{corner['Letter']}"

        """
        fig.add_vline()：在图上画一条"垂直的参考线"（v = vertical）
        它跟 add_trace 不一样——add_trace 是加一条"数据曲线"，
        add_vline 加的是一条"辅助线/标注线"，不会出现在图例里，也不参与 hover 数值显示。

        参数说明：
            x=...               这条竖线画在横轴的哪个位置，用这个弯的 Distance
            line_width=1        线宽
            line_dash           线类型
            line_color'         颜色
            layer               层级
            annotation_text     在这条线旁边写的文字，这里写弯道编号
            annotation_position 文字放的位置
            row = 1, col = 1    关键！告诉 plotly 这条线画在"第一行第一列"那个子图上。
                                因为用了 make_subplots，不指定的话 plotly 不知道该画哪一格
        """
        fig.add_vline(
            x = corner['Distance'],

            # 线样式
            line_width = 1,
            line_dash = 'dot',
            line_color = 'gray',
            layer = 'below',

            # 文字样式
            annotation_text = corner_label,
            annotation_position = 'bottom',
            annotation_yshift = 12,
            annotation_font_size = 10,
            row = 1, col = 1,
        )




# --- 第四步：只有正好2个车手时，才计算 sector delta 并画表格 ---
    """
    计算每个sector的时间差值，该值本身就在lap数据中。
    A_fastest 和 B_fastest 这两个 Lap 对象，本身就带有
    Sector1Time / Sector2Time / Sector3Time 三个字段
    类型是 pandas 的 Timedelta，也就是"一段时间"，不是普通数字）
    """
    if show_table:
        lap_a = driver_data[0]['lap']   # 参见第一部分的参数表。
        lap_b = driver_data[1]['lap']
        code_a = driver_data[0]['code']
        code_b = driver_data[1]['code']

        sector_deltas = []    # 创建新的列表，用来装三个计时段时间差
        for i in [1, 2, 3]:
            sec_name = f'Sector{i}Time'    # 格式化字符串动态取出三个计时段时间。
            diff = (lap_a[sec_name] - lap_b[sec_name]).total_seconds()    # 计算计时段时间差，相减后转换成秒数表示
            sector_deltas.append(diff)    # 把计时段时间差添加到列表中

        fig.add_trace(go.Table(
            # header 是表头那一行
            header = dict(
                values = ['Sector', f'{code_a} (s)', f'{code_b} (s)', 'Delta (s)'],
                fill_color = 'lightgrey',
                height = 30,
                align = 'center'
            ),
            # cells 是表格主体内容，每一个 values 里的列表对应一"列"
            cells = dict(
                values = [
                    ['Sector 1', 'Sector 2', 'Sector 3'],    # 第一列
                    [lap_a['Sector1Time'].total_seconds(),
                     lap_a['Sector2Time'].total_seconds(),
                     lap_a['Sector3Time'].total_seconds()],    # 第二列
                    [lap_b['Sector1Time'].total_seconds(),
                     lap_b['Sector2Time'].total_seconds(),
                     lap_b['Sector3Time'].total_seconds()],    # 第三列
                    [f"{d:+.3f}" for d in sector_deltas]    # 第四列，每个delta前面带上正负号
                ],
                align = 'center', # 表格内容居中对齐
                height = 30  # 表格单元格高度
            )
        ), row = 2, col = 1) # 把表格加到第二行第一列（有表格的话一定在下半）




# --- 第五步：坐标轴标题、整体布局 ---
    """
    因为这张图现在可能有多组坐标轴（虽然这里只有一组，但用了 make_subplots 之后 Plotly 统一按"多子图"的逻辑处理），
    所以横纵轴标题不能直接写在 fig.update_layout(xaxis_title=...) 里了（那样只对没有 subplot 的图有效），
    要换成 update_xaxes / update_yaxes，并指定是哪个格子：
    """
    fig.update_xaxes(
        title_text = 'Distance (m)',
        showgrid=False,                 # 关闭竖向网格，避免和弯道线重复
        row = 1, col = 1
    )

    fig.update_yaxes(
        title_text = 'Speed (km/h)',
        row = 1, col = 1
    )

    fig.update_layout(
        title = f"{session.event['EventName']} {session.name} - Speed Comparison",    # 根据传进来的实参来确定标题
        hovermode = 'x unified',
        height = 1200 if show_table else 800,  # 三元运算符表达式，如果show_table为True，则高度为1200，否则为800
    )

    return fig




"""
get_car_data()：从这一圈里取出详细的遥测表格
跟之前 session.laps 那张"每圈一行"的表不一样，这张表是"这一圈里每个采样时刻一行"（采样率很高，一圈能有几百行）
列包括 Speed（速度）、Throttle（油门开度0-100）、Brake（刹车，开/关）、RPM、nGear（挡位）等。
"""
# tel_a = A_fastest.get_car_data().add_distance()
# tel_b = B_fastest.get_car_data().add_distance()

"""
拿到两个车手对应的官方配色
fastf1.plotting.get_driver_color() 需要两个参数：
   1）车手的三字母代码，比如 'LEC'、'VER'（也可以用车号，看你装的 fastf1 版本）
   2）session 对象，因为同一个车手在不同年份/车队颜色可能不一样，所以要告诉函数"是哪一场比赛"
"""
# color_a = fastf1.plotting.get_driver_color(A_fastest['Driver'], session)
# color_b = fastf1.plotting.get_driver_color(B_fastest['Driver'], session)

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
设置标题、坐标轴名字、鼠标悬停效果
fig.update_layout() 是用来统一调整这张图"外观"的函数
title：整张图的标题
xaxis_title / yaxis_title：横轴、纵轴的名字（对应原来的 plt.xlabel / plt.ylabel）
hovermode='x unified'：
  鼠标移到图上时，会把"同一个横坐标位置"上所有线的数值
  一起显示在一个提示框里，方便同时对比两位车手在同一位置的速度

fig.update_layout(
    title='2024 Monaco GP Q - Speed Comparison',
    xaxis_title = 'Distance (m)',
    yaxis_title = 'Speed (km/h)',
    hovermode = 'x unified'
)

# 显示图
fig.show()
"""