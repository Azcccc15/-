"""
旱涝急转指数计算工具
包含 LDFAI（长周期）和 SDFAI（短周期）的计算与分级
参考文献：
    LDFAI = (R78 - R56) * (|R56| + |R78|) * 1.8^(-|R56+R78|)
    SDFAI = (Rj - Ri) * (|Ri| + |Rj|) * 3.2^(-|Ri+Rj|)   (j = i+1, i=5,6,7)
分类标准参照表1（对称补充了未列出的区间）
"""

import numpy as np

# -------------------- 核心计算函数 --------------------
def calculate_ldfai(R56, R78):
    """
    计算长周期旱涝急转指数 LDFAI
    :param R56: 5-6月份的标准化降水量（可以是总和或平均值）
    :param R78: 7-8月份的标准化降水量
    :return: LDFAI 值
    """
    term1 = R78 - R56
    term2 = abs(R56) + abs(R78)
    term3 = 1.8 ** (-abs(R56 + R78))
    return term1 * term2 * term3

def calculate_sdfai(Ri, Rj):
    """
    计算短周期旱涝急转指数 SDFAI
    :param Ri: 第 i 月的标准化降水量
    :param Rj: 第 i+1 月的标准化降水量
    :return: SDFAI 值
    """
    term1 = Rj - Ri
    term2 = abs(Ri) + abs(Rj)
    term3 = 3.2 ** (-abs(Ri + Rj))
    return term1 * term2 * term3

# -------------------- 分类函数 --------------------
def classify_dwaa(index, index_type='LDFAI'):
    """
    根据指数值对旱涝急转事件进行分类
    :param index: 指数值
    :param index_type: 'LDFAI' 或 'SDFAI'
    :return: 分类结果字符串
    """
    if index_type == 'LDFAI':
        if index >= 3:
            return "重度旱转涝"
        elif index >= 2:
            return "中度旱转涝"
        elif index >= 1:
            return "轻度旱转涝"
        elif index <= -3:
            return "重度涝转旱"
        elif index <= -2:
            return "中度涝转旱"
        elif index <= -1:
            return "轻度涝转旱"
        else:
            return "正常"
    elif index_type == 'SDFAI':
        if index >= 3:
            return "重度旱转涝"
        elif index >= 2:
            return "中度旱转涝"
        elif index >= 1:
            return "轻度旱转涝"
        elif index <= -3:
            return "重度涝转旱"
        elif index <= -2:
            return "中度涝转旱"
        elif index <= -1:
            return "轻度涝转旱"
        else:
            return "正常"
    else:
        raise ValueError("index_type 必须为 'LDFAI' 或 'SDFAI'")

# -------------------- 数据接入端口示例 --------------------
def interactive_input():
    """交互式命令行输入"""
    print("========== 旱涝急转指数计算 ==========")
    # LDFAI
    print("\n【长周期 LDFAI】需要 5-6月 和 7-8月的标准化降水量")
    R56 = float(input("请输入 R56 (5-6月标准化降水量): "))
    R78 = float(input("请输入 R78 (7-8月标准化降水量): "))
    ldfai = calculate_ldfai(R56, R78)
    print(f"LDFAI = {ldfai:.4f}，分类：{classify_dwaa(ldfai, 'LDFAI')}")

    # SDFAI（三个相邻月份对）
    print("\n【短周期 SDFAI】需要相邻月份的标准化降水量")
    pairs = [(5,6), (6,7), (7,8)]
    for i, j in pairs:
        Ri = float(input(f"请输入 R{i} ({i}月标准化降水量): "))
        Rj = float(input(f"请输入 R{j} ({j}月标准化降水量): "))
        sdfai = calculate_sdfai(Ri, Rj)
        print(f"SDFAI ({i}-{j}月) = {sdfai:.4f}，分类：{classify_dwaa(sdfai, 'SDFAI')}")

def batch_process_from_array(data):
    """
    从数组批量计算（适用于多个年份或站点）
    :param data: 字典或DataFrame，包含各月的标准化降水量
                 例如：{'R5': [...], 'R6': [...], 'R7': [...], 'R8': [...]}
    """
    import pandas as pd
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    else:
        df = data.copy()
    
    # 计算 LDFAI（假设 R56 = (R5+R6)/2 或 R5+R6，根据实际定义调整）
    # 这里取平均值作为示例，用户可根据研究需要修改
    df['R56'] = (df['R5'] + df['R6']) / 2
    df['R78'] = (df['R7'] + df['R8']) / 2
    df['LDFAI'] = df.apply(lambda row: calculate_ldfai(row['R56'], row['R78']), axis=1)
    df['LDFAI_class'] = df['LDFAI'].apply(lambda x: classify_dwaa(x, 'LDFAI'))
    
    # 计算 SDFAI
    df['SDFAI_56'] = df.apply(lambda row: calculate_sdfai(row['R5'], row['R6']), axis=1)
    df['SDFAI_67'] = df.apply(lambda row: calculate_sdfai(row['R6'], row['R7']), axis=1)
    df['SDFAI_78'] = df.apply(lambda row: calculate_sdfai(row['R7'], row['R8']), axis=1)
    df['SDFAI_56_class'] = df['SDFAI_56'].apply(lambda x: classify_dwaa(x, 'SDFAI'))
    df['SDFAI_67_class'] = df['SDFAI_67'].apply(lambda x: classify_dwaa(x, 'SDFAI'))
    df['SDFAI_78_class'] = df['SDFAI_78'].apply(lambda x: classify_dwaa(x, 'SDFAI'))
    
    return df

# -------------------- 使用示例 --------------------
if __name__ == "__main__":
    # 方式1：交互式输入
    interactive_input()
    
    # 方式2：批量处理（示例数据）
    # 假设有5年的每月标准化降水数据
    sample_data = {
        'R5': [0.5, -1.2, 0.8, -0.3, 1.1],
        'R6': [-0.8, 0.6, -0.5, 1.2, -0.7],
        'R7': [1.3, -0.4, -1.1, 0.9, -0.2],
        'R8': [0.2, 0.7, 0.4, -0.6, 1.5]
    }
    result_df = batch_process_from_array(sample_data)
    print("\n批量处理结果（前5行）：")
    print(result_df[['R5','R6','R7','R8','LDFAI','LDFAI_class',
                     'SDFAI_56','SDFAI_56_class']].head())