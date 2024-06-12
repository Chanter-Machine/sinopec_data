import pandas as pd
import numpy as np
import yaml

from sino.recharger_op.draw import draw_stat_chart


def read_sino_report_excel_to_df(excel_file_path, sheet_name: str):
    dfs = pd.read_excel(excel_file_path, sheet_name=[sheet_name], header=None)
    df = dfs[sheet_name]
    df = df.drop(df.index[0])
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df

def read_raw_excel_to_df(excel_file_path, sheet_name: str):
    dfs = pd.read_excel(excel_file_path, sheet_name=[sheet_name], header=None)
    df = dfs[sheet_name]
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df

def QoQ_calc(current_df: pd.DataFrame, previous_report: str ) -> pd.DataFrame:
    previous_df = read_raw_excel_to_df(previous_report, 'Sheet1')
    # 处理 previous_df
    previous_df = previous_df[['站点', '充电量KW.h']].rename(columns={'充电量KW.h': '上周期充电量KW.h'})

    # 合并 current_df 和 previous_df
    current_df = current_df.merge(previous_df, on='站点', how='left')

    # 计算充电量环比
    current_df['充电量环比'] = (current_df['充电量KW.h'] - current_df['上周期充电量KW.h']) / current_df[
        '上周期充电量KW.h']
    current_df['充电量环比'] = current_df['充电量环比'] * 100
    # 格式化充电量环比
    current_df['充电量环比'] = current_df['充电量环比'].apply(lambda x: '{:.2f}%'.format(x))

    return current_df

pd.set_option('display.max_columns', None)

with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

days_span = config['days_span']
daily_charger_station_path = config['daily_charger_station_path']
daily_charger_path = config['daily_charger_path']
excel_output_path = config['excel_output_path']
station_charger_count = config['recharge_station']
need_QoQ = config['need_QoQ']
QoQ_file = config.get('QoQ_file', '')
specify_cols_order = config['specify_cols_order']
need_draw_chart = config['need_draw_chart']
chart_config = config['chart_config']

daily_recharge_station = read_sino_report_excel_to_df(daily_charger_station_path, 'Export')
daily_charger = read_sino_report_excel_to_df(daily_charger_path, 'Export')

# print(daily_report_df)

groupby_column = '站点'  # 根据站点编码进行分组
sum_columns = ['充电量KW.h', '电费', '服务费', '实收金额']  # 对这些列进行求和

# 进行groupby操作并求和
grouped_df = daily_recharge_station.groupby(groupby_column, as_index=False)[sum_columns].sum()
result_df = grouped_df.reset_index()
# 将结果存储在新的DataFrame中
result_df = pd.DataFrame(grouped_df)
result_df['在用抢数'] = 0
result_df['快充枪数'] = 0
result_df['慢充枪数'] = 0
result_df['充电量(万度)'] = result_df['充电量KW.h']/10000
result_df['电费(万元)'] = result_df['电费']/10000
result_df['服务费(万元)'] = result_df['服务费']/10000
result_df['实收金额(万元)'] = result_df['实收金额']/10000
result_df['度电服务费(元)'] = result_df['服务费']/result_df['充电量KW.h']
result_df['度电营业额(元)'] = result_df['实收金额']/result_df['充电量KW.h']

fast_chargers = []
slow_chargers = []
for _, row in result_df.iterrows():
    fast_chargers.append(station_charger_count[row['站点']][0])
    slow_chargers.append(station_charger_count[row['站点']][1])
result_df['快充枪数'] = pd.Series(fast_chargers, name='快充枪数')
result_df['慢充枪数'] = pd.Series(slow_chargers, name='慢充枪数')
result_df['在用抢数'] = result_df['快充枪数'] + result_df['慢充枪数']
# 打印结果

result_df['慢充电量（度）'] = None
result_df['快充电量（度）'] = None


# 定义函数来根据'充电桩名称'的值生成新的'快慢冲'列
def get_charging_speed(row):
    if '交流' in row['充电桩名称']:
        return 'slow'
    else:
        return 'fast'

# 使用 apply() 函数应用自定义函数到每一行，生成新的列'快慢冲'
daily_charger['快慢冲'] = daily_charger.apply(get_charging_speed, axis=1)

# 打印结果
# print(daily_charger)

daily_charger_group_result = daily_charger.groupby(['归属电站', '快慢冲']).agg({
    '充电桩名称': 'count',
    '电量（度）': 'sum'
}).reset_index()
# print(daily_charger_group_result)


daily_charger_group_result.rename(columns={'充电桩名称': '充电桩数量', '电量（度）': '快慢冲度数'}, inplace=True)
daily_charger_group_result = daily_charger_group_result[daily_charger_group_result['快慢冲'] == 'slow']
print(daily_charger_group_result)


# print(merged_df)
current_week_df = pd.merge(result_df, daily_charger_group_result,
                           left_on='站点',
                           right_on='归属电站',
                           how='left')
current_week_df['慢充电量（度）'] = current_week_df['快慢冲度数']
current_week_df['慢充电量（度）'] = current_week_df['慢充电量（度）'].apply(lambda x: x if x is not np.nan else 0)
current_week_df['快充电量（度）'] = current_week_df['充电量KW.h'] - current_week_df['慢充电量（度）']
current_week_df.loc[current_week_df['快充枪数'] == 0, '快充电量（度）'] = 0
current_week_df.drop(columns=['归属电站', '快慢冲', '充电桩数量', '快慢冲度数'], inplace=True)
# print(merged_df)
def safe_divide(x, y):
    if y == 0:
        return np.nan
    else:
        return x / y

current_week_df['单枪日均充电度数'] = current_week_df.apply(lambda row: safe_divide(row['充电量KW.h'] / days_span, row['在用抢数']), axis=1)
current_week_df['单枪日均快充度数'] = current_week_df.apply(lambda row: safe_divide(row['快充电量（度）'] / days_span, row['快充枪数']), axis=1)
current_week_df['单枪日均慢充度数'] = current_week_df.apply(lambda row: safe_divide(row['慢充电量（度）'] / days_span, row['慢充枪数']), axis=1)
# 选择数值类型的列
numeric_columns = current_week_df.select_dtypes(include=[np.number])

current_week_df['充电量(万度)'] = current_week_df['充电量(万度)'].apply(lambda x: round(x, 2))
current_week_df['电费(万元)'] = current_week_df['电费(万元)'].apply(lambda x: round(x, 2))
current_week_df['服务费(万元)'] = current_week_df['服务费(万元)'].apply(lambda x: round(x, 2))
current_week_df['实收金额(万元)'] = current_week_df['实收金额(万元)'].apply(lambda x: round(x, 2))
current_week_df['度电服务费(元)'] = current_week_df['度电服务费(元)'].apply(lambda x: round(x, 2))
current_week_df['度电营业额(元)'] = current_week_df['度电营业额(元)'].apply(lambda x: round(x, 2))

# 对数值类型的列应用 round 函数
current_week_df[numeric_columns.columns] = numeric_columns.map(lambda x: round(x, 2))

def format_station_name(x):
    split_list = x.split('-')
    # 返回分割后的数组中的最后一个值
    return split_list[-1]
current_week_df['站点'] = current_week_df['站点'].apply(format_station_name)
print(current_week_df)


if need_QoQ:
    current_week_df = QoQ_calc(current_week_df, QoQ_file)


current_week_df = current_week_df[specify_cols_order]
current_week_df.to_excel(excel_output_path, index=False)

#需要画图
if need_draw_chart and need_QoQ:
    # 抽取为数组
    site_arr = current_week_df["站点"].values
    charge_arr = current_week_df["充电量(万度)"].values
    charge_QoQ_arr = current_week_df["上周期充电量KW.h"].values
    draw_stat_chart(site_arr, charge_arr, charge_QoQ_arr, chart_config)

