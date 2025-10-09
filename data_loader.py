"""
SDP Dashboard データローダー v2
日次出勤データ・日次スキルデータ対応版
"""

import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_all_data():
    """全データをロード"""
    data_dir = Path('data')
    
    # 従業員スキルデータ
    df_employee = pd.read_csv(data_dir / 'employee_skill_data.csv', encoding='utf-8-sig')
    df_employee['評価日'] = pd.to_datetime(df_employee['評価日'])
    
    # 日次生産データ
    df_production = pd.read_csv(data_dir / 'daily_production_data.csv', encoding='utf-8-sig')
    df_production['日付'] = pd.to_datetime(df_production['日付'])
    
    # 研修履歴データ
    df_training = pd.read_csv(data_dir / 'training_history_data.csv', encoding='utf-8-sig')
    df_training['受講日'] = pd.to_datetime(df_training['受講日'])
    
    # ボトルネックデータ
    df_bottleneck = pd.read_csv(data_dir / 'process_bottleneck_data.csv', encoding='utf-8-sig')
    
    # 拠点マスタ
    df_location = pd.read_csv(data_dir / 'location_master_data.csv', encoding='utf-8-sig')
    
    return df_employee, df_production, df_training, df_bottleneck, df_location

def get_skill_categories():
    """スキルカテゴリ定義を取得"""
    return {
        '操炉技術': {'weight': 0.25, 'impact_efficiency': 0.30, 'impact_quality': 0.25, 'impact_safety': 0.20},
        '成分制御': {'weight': 0.20, 'impact_efficiency': 0.20, 'impact_quality': 0.35, 'impact_safety': 0.15},
        '異常対応': {'weight': 0.20, 'impact_efficiency': 0.25, 'impact_quality': 0.20, 'impact_safety': 0.35},
        '設備保全': {'weight': 0.15, 'impact_efficiency': 0.15, 'impact_quality': 0.10, 'impact_safety': 0.20},
        '品質検査': {'weight': 0.10, 'impact_efficiency': 0.05, 'impact_quality': 0.30, 'impact_safety': 0.05},
        '安全管理': {'weight': 0.10, 'impact_efficiency': 0.05, 'impact_quality': 0.00, 'impact_safety': 0.35},
    }

def get_benchmark_locations():
    """ベンチマーク拠点のリストを取得"""
    return ['日本_千葉', '日本_君津']

def calculate_location_kpi(df_production, df_employee):
    """拠点別KPI計算"""
    # 生産データの集計
    prod_agg = df_production.groupby('拠点').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '稼働率': 'mean',
        '歩留まり': 'mean',
    }).reset_index()
    
    # スキルデータの集計
    skill_agg = df_employee.groupby('拠点').agg({
        '総合スキルスコア': 'mean',
        '従業員ID': 'count',
    }).reset_index()
    skill_agg.columns = ['拠点', '平均スキルスコア', '従業員数']
    
    # 結合
    kpi = prod_agg.merge(skill_agg, on='拠点')
    
    return kpi

def calculate_line_kpi(df_production, location):
    """ライン別KPI計算"""
    df_loc = df_production[df_production['拠点'] == location]
    
    line_kpi = df_loc.groupby('ライン').agg({
        '生産効率_指数': ['mean', 'std'],
        '品質不良率': ['mean', 'std'],
        '稼働率': 'mean',
        '歩留まり': 'mean',
    }).reset_index()
    
    line_kpi.columns = ['ライン', '生産効率_平均', '生産効率_std', 
                        '品質不良率_平均', '品質不良率_std', '稼働率', '歩留まり']
    
    return line_kpi

def calculate_shift_kpi(df_production, location, line):
    """シフト別KPI計算"""
    df_loc = df_production[(df_production['拠点'] == location) & (df_production['ライン'] == line)]
    
    shift_kpi = df_loc.groupby('シフト').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '稼働率': 'mean',
    }).reset_index()
    
    return shift_kpi

def get_skill_distribution(df_employee, location, line=None):
    """スキル分布取得"""
    df_loc = df_employee[df_employee['拠点'] == location]
    if line:
        df_loc = df_loc[df_loc['ライン'] == line]
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    skill_dist = df_loc[skill_cols].mean()
    
    return skill_dist

def calculate_skill_production_correlation(df_employee, df_production):
    """スキルと生産性の相関分析"""
    # 従業員スキルの平均を計算
    skill_by_group = df_employee.groupby(['拠点', 'ライン', 'シフト']).agg({
        '総合スキルスコア': 'mean',
        '操炉技術': 'mean',
        '成分制御': 'mean',
        '異常対応': 'mean',
        '設備保全': 'mean',
        '品質検査': 'mean',
        '安全管理': 'mean',
    }).reset_index()
    
    # 生産データと結合
    merged = df_production.merge(skill_by_group, on=['拠点', 'ライン', 'シフト'], how='left')
    
    return merged

def get_training_effectiveness(df_training, df_employee):
    """研修効果分析"""
    # 従業員IDごとの研修受講回数
    training_count = df_training.groupby('従業員ID').size().reset_index(name='研修回数')
    
    # 従業員スキルデータと結合
    emp_with_training = df_employee.merge(training_count, on='従業員ID', how='left')
    emp_with_training['研修回数'] = emp_with_training['研修回数'].fillna(0)
    
    return emp_with_training