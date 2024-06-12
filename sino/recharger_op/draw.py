import matplotlib.pyplot as plt
import numpy as np

# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 数据
# stations = ["梧侣充电站", "文屏充电站", "石油大厦停车场充电站", "前埔北充电站", "高殿充电站", "新曙路充电站"]
# electricity_fees = [40539.85, 50124.42, 367.09, 40071.76, 14481.47, 8791.39]
# fee_percentage_change = [10, 5, 7, -20, 20, -15]  # 转换百分比字符串为浮点数

def draw_stat_chart(stations, charge_arr, charge_QoQ_arr, chart_config=None ):
    bar_width = 0.3  # 调整此数值来更改柱状图的宽度，默认为0.8
    line_label_x_offset = 0.35  # 调整偏移量，使其与柱状图脱离重叠
    line_label_y_offset = -2  # 设置 y 轴方向的偏移量
    fontsize = 18

    if chart_config is not None:
        bar_width = chart_config.get("bar_width", 0.3)
        line_label_x_offset = chart_config.get("line_label_x_offset", 0.35)
        line_label_y_offset = chart_config.get("line_label_y_offset", -2)
        fontsize = chart_config.get("fontsize", 18)

    # 设置字体大小
    # 设置颜色
    bar_color = (79 / 255, 129 / 255, 189 / 255)
    line_color = (194 / 255, 86 / 255, 83 / 255)
    line_label_color = (255 / 255, 74 / 255, 74 / 255)

    # 绘图
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 电费柱状图
    bars = ax1.bar(stations, charge_arr, width=bar_width, color=bar_color, label=chart_config.get("bar_label", '这是一个默认的xlabel'))
    ax1.set_xlabel(chart_config.get("bar_label", '这是一个默认的bar_label'))
    ax1.set_ylabel(chart_config.get("y1label", '这是一个默认的y1label'), color=bar_color)
    ax1.tick_params(axis='y', labelcolor=bar_color)

    # 在每个柱体上加上电费的值
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom',
                 fontsize=fontsize)

    # 创建第二个y轴用于电费环比折线图
    ax2 = ax1.twinx()
    line, = ax2.plot(stations, charge_QoQ_arr, color=line_color, marker='o', label=chart_config.get("line_lable", '这是一个默认的line_lable'))
    ax2.set_ylabel(chart_config.get("y2label", '这是一个默认的y2_lable'), color=line_color)
    ax2.tick_params(axis='y', labelcolor=line_color)

    # 在每个数据点上加上电费环比的值，修改字体大小为12
    for i, txt in enumerate(charge_QoQ_arr):
        ax2.text(i + line_label_x_offset, charge_QoQ_arr[i] + line_label_y_offset, f'{txt}%', ha='center', va='bottom',
                 color=line_label_color, fontsize=fontsize)

    # 标题和图例
    fig.suptitle(chart_config.get("subtitle", '这是一个默认的title'))
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # plt.show()
    plt.savefig(chart_config.get("export_name", '这是一个默认的导出名称'), format="jpg", dpi=300)

# draw_stat_chart()