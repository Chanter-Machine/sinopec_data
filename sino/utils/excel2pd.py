import pandas as pd


def read_sino_excel_to_df(excel_file_path):
    dfs = pd.read_excel(excel_file_path, sheet_name=['Export'], header=None)
    df = dfs['Export']
    df = df.drop(df.index[0])
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df
