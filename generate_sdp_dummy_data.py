"""
SDP (Skill Driven Production) ダッシュボード用ダミーデータ生成スクリプト
高炉メーカーのグローバル拠点データを生成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ランダムシードの固定
np.random.seed(42)
random.seed(42)

# 拠点定義（グローバル展開）
LOCATIONS = {
    '日本_千葉': {'country': '日本', 'lat': 35.6, 'lon': 140.1, 'benchmark': True, 'efficiency_base': 100, 'quality_base': 0.5, 'safety_base': 0.2},
    '日本_君津': {'country': '日本', 'lat': 35.3, 'lon': 139.9, 'benchmark': True, 'efficiency_base': 98, 'quality_base': 0.6, 'safety_base': 0.3},
    '中国_上海': {'country': '中国', 'lat': 31.2, 'lon': 121.5, 'benchmark': False, 'efficiency_base': 85, 'quality_base': 2.5, 'safety_base': 1.5},
    '中国_大連': {'country': '中国', 'lat': 38.9, 'lon': 121.6, 'benchmark': False, 'efficiency_base': 82, 'quality_base': 2.8, 'safety_base': 1.8},
    'インド_ムンバイ': {'country': 'インド', 'lat': 19.1, 'lon': 72.9, 'benchmark': False, 'efficiency_base': 75, 'quality_base': 4.2, 'safety_base': 3.5},
    'インドネシア_ジャカルタ': {'country': 'インドネシア', 'lat': -6.2, 'lon': 106.8, 'benchmark': False, 'efficiency_base': 70, 'quality_base': 5.0, 'safety_base': 4.2},
    'タイ_バンコク': {'country': 'タイ', 'lat': 13.8, 'lon': 100.5, 'benchmark': False, 'efficiency_base': 78, 'quality_base': 3.5, 'safety_base': 2.8},
    'ベトナム_ホーチミン': {'country': 'ベトナム', 'lat': 10.8, 'lon': 106.7, 'benchmark': False, 'efficiency_base': 72, 'quality_base': 4.5, 'safety_base': 3.8},
    'ブラジル_サンパウロ': {'country': 'ブラジル', 'lat': -23.6, 'lon': -46.7, 'benchmark': False, 'efficiency_base': 80, 'quality_base': 3.0, 'safety_base': 2.5},
    'メキシコ_モンテレイ': {'country': 'メキシコ', 'lat': 25.7, 'lon': -100.3, 'benchmark': False, 'efficiency_base': 77, 'quality_base': 3.8, 'safety_base': 3.0},
}

# ライン・シフト定義
LINES = ['高炉1号', '高炉2号', '転炉A', '転炉B', '圧延1', '圧延2']
SHIFTS = ['A班', 'B班', 'C班', 'D班']

# スキルカテゴリ定義（高炉メーカー特有）
SKILL_CATEGORIES = {
    '操炉技術': {'weight': 0.25, 'impact_efficiency': 0.30, 'impact_quality': 0.25, 'impact_safety': 0.20},
    '成分制御': {'weight': 0.20, 'impact_efficiency': 0.20, 'impact_quality': 0.35, 'impact_safety': 0.15},
    '異常対応': {'weight': 0.20, 'impact_efficiency': 0.25, 'impact_quality': 0.20, 'impact_safety': 0.35},
    '設備保全': {'weight': 0.15, 'impact_efficiency': 0.15, 'impact_quality': 0.10, 'impact_safety': 0.20},
    '品質検査': {'weight': 0.10, 'impact_efficiency': 0.05, 'impact_quality': 0.30, 'impact_safety': 0.05},
    '安全管理': {'weight': 0.10, 'impact_efficiency': 0.05, 'impact_quality': 0.00, 'impact_safety': 0.35},
}

# 工程定義
PROCESSES = ['原料準備', '高炉操業', '転炉精錬', 'スラグ制御', '連続鋳造', '熱間圧延', '冷間圧延', '検査']

def generate_employee_data(n_employees=2000):
    """従業員スキルデータ生成"""
    data = []
    employee_id = 1000
    
    for location, loc_info in LOCATIONS.items():
        # 拠点ごとのベーススキルレベル（日本拠点が高い）
        if loc_info['benchmark']:
            base_skill = 4.0
            skill_std = 0.6
        else:
            # 海外拠点はベース効率に応じてスキルレベルを調整
            base_skill = 2.5 + (loc_info['efficiency_base'] - 70) / 30 * 1.5
            skill_std = 0.9
        
        # 各拠点の従業員数（拠点規模に応じて調整）
        n_per_location = int(n_employees / len(LOCATIONS) * random.uniform(0.8, 1.2))
        
        for _ in range(n_per_location):
            line = random.choice(LINES)
            shift = random.choice(SHIFTS)
            
            # シフト・ラインによるスキル差異
            shift_modifier = {'A班': 0.2, 'B班': 0.1, 'C班': -0.1, 'D班': -0.2}[shift]
            line_modifier = np.random.uniform(-0.3, 0.3)
            
            # 各スキルカテゴリのレベル生成
            skills = {}
            for skill_name in SKILL_CATEGORIES.keys():
                skill_level = base_skill + shift_modifier + line_modifier
                skill_level += np.random.normal(0, skill_std)
                skill_level = np.clip(skill_level, 1.0, 5.0)
                skills[skill_name] = round(skill_level, 1)
            
            # 総合スキルスコア計算
            total_skill = sum(skills[k] * SKILL_CATEGORIES[k]['weight'] 
                            for k in SKILL_CATEGORIES.keys())
            
            # 経験年数（スキルレベルと相関）
            experience_years = max(1, int(np.random.gamma(total_skill, 2)))
            
            # 生産効率・品質への影響
            efficiency = loc_info['efficiency_base'] + (total_skill - 3.0) * 8 + np.random.normal(0, 3)
            quality_defect = loc_info['quality_base'] + (5.0 - total_skill) * 0.8 + abs(np.random.normal(0, 0.5))
            
            data.append({
                '従業員ID': f'EMP{employee_id:05d}',
                '拠点': location,
                '国': loc_info['country'],
                'ライン': line,
                'シフト': shift,
                '経験年数': experience_years,
                '評価日': datetime.now().date(),
                **skills,
                '総合スキルスコア': round(total_skill, 2),
                '生産効率_個人': round(efficiency, 1),
                '品質不良率_個人': round(quality_defect, 2),
            })
            employee_id += 1
    
    return pd.DataFrame(data)

def generate_production_data(days=180):
    """日次生産データ生成"""
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for location, loc_info in LOCATIONS.items():
        for day in range(days):
            date = start_date + timedelta(days=day)
            
            for line in LINES:
                for shift in SHIFTS:
                    # ベース生産性
                    base_efficiency = loc_info['efficiency_base']
                    base_quality = loc_info['quality_base']
                    base_safety = loc_info['safety_base']
                    
                    # 時系列トレンド（改善傾向）
                    trend = day / days * 5 if not loc_info['benchmark'] else 0
                    
                    # ランダム変動
                    daily_var = np.random.normal(0, 3)
                    
                    # 生産効率（t/h換算）
                    efficiency = base_efficiency + trend + daily_var
                    efficiency = np.clip(efficiency, 50, 120)
                    
                    # 品質不良率
                    quality_defect = base_quality - trend * 0.1 + abs(np.random.normal(0, 0.3))
                    quality_defect = max(0.1, quality_defect)
                    
                    # 労災発生（確率的）
                    accident = 1 if np.random.random() < base_safety / 100 else 0
                    
                    # 生産量
                    production_volume = efficiency * 24 * random.uniform(0.9, 1.0)
                    
                    data.append({
                        '日付': date.date(),
                        '拠点': location,
                        '国': loc_info['country'],
                        'ライン': line,
                        'シフト': shift,
                        '生産量_ton': round(production_volume, 1),
                        '生産効率_指数': round(efficiency, 1),
                        '品質不良率': round(quality_defect, 2),
                        '労災発生': accident,
                        '稼働率': round(random.uniform(85, 98), 1),
                        '歩留まり': round(random.uniform(94, 99.5), 1),
                    })
    
    return pd.DataFrame(data)

def generate_training_data(n_records=500):
    """教育・訓練履歴データ生成"""
    data = []
    training_programs = [
        '高炉操業基礎', '成分制御実践', '異常対応訓練', '設備保全コース',
        '品質管理手法', '安全作業手順', '5S活動', 'トラブルシューティング'
    ]
    
    for _ in range(n_records):
        training_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        data.append({
            '受講日': training_date.date(),
            '従業員ID': f'EMP{random.randint(1000, 3000):05d}',
            '研修プログラム': random.choice(training_programs),
            '受講時間': random.choice([8, 16, 24, 40]),
            '理解度テスト': round(random.uniform(60, 100), 1),
            '実技評価': round(random.uniform(1, 5), 1),
            'コスト_円': random.choice([50000, 100000, 150000, 200000]),
        })
    
    return pd.DataFrame(data)

def generate_process_bottleneck_data():
    """工程別スキルボトルネックデータ生成"""
    data = []
    
    for location in LOCATIONS.keys():
        for process in PROCESSES:
            for skill in SKILL_CATEGORIES.keys():
                # 要求スキルレベル
                required_skill = random.uniform(3.5, 4.5)
                
                # 現在の保有スキルレベル
                current_skill = required_skill - random.uniform(-0.5, 1.5)
                current_skill = max(1.0, current_skill)
                
                # ギャップ
                gap = required_skill - current_skill
                
                data.append({
                    '拠点': location,
                    '工程': process,
                    'スキルカテゴリ': skill,
                    '要求レベル': round(required_skill, 1),
                    '現在レベル': round(current_skill, 1),
                    'スキルギャップ': round(gap, 1),
                    '影響度_生産': SKILL_CATEGORIES[skill]['impact_efficiency'],
                    '影響度_品質': SKILL_CATEGORIES[skill]['impact_quality'],
                    '影響度_安全': SKILL_CATEGORIES[skill]['impact_safety'],
                })
    
    return pd.DataFrame(data)

def generate_location_master():
    """拠点マスタデータ生成"""
    data = []
    
    for location, info in LOCATIONS.items():
        data.append({
            '拠点': location,
            '国': info['country'],
            '緯度': info['lat'],
            '経度': info['lon'],
            'ベンチマーク拠点': info['benchmark'],
            '稼働開始年': random.randint(1970, 2020),
            '従業員数': random.randint(200, 500),
            '高炉数': random.randint(1, 3),
        })
    
    return pd.DataFrame(data)

if __name__ == '__main__':
    print("SDP ダミーデータ生成開始...")
    
    # データ生成
    df_employee = generate_employee_data(2000)
    df_production = generate_production_data(180)
    df_training = generate_training_data(500)
    df_bottleneck = generate_process_bottleneck_data()
    df_location = generate_location_master()
    
    # CSV保存
    df_employee.to_csv('data/employee_skill_data.csv', index=False, encoding='utf-8-sig')
    df_production.to_csv('data/daily_production_data.csv', index=False, encoding='utf-8-sig')
    df_training.to_csv('data/training_history_data.csv', index=False, encoding='utf-8-sig')
    df_bottleneck.to_csv('data/process_bottleneck_data.csv', index=False, encoding='utf-8-sig')
    df_location.to_csv('data/location_master_data.csv', index=False, encoding='utf-8-sig')
    
    print(f"✅ 従業員データ: {len(df_employee)} 件")
    print(f"✅ 生産データ: {len(df_production)} 件")
    print(f"✅ 研修データ: {len(df_training)} 件")
    print(f"✅ ボトルネックデータ: {len(df_bottleneck)} 件")
    print(f"✅ 拠点マスタ: {len(df_location)} 件")
    print("\nデータ生成完了！")
