"""
SDP (Skill Driven Production) ダッシュボード用ダミーデータ生成スクリプト v2
日次出勤データを考慮したリアルなデータセット生成
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
            shift_modifier = {'A班': 0.2, 'B班': 0.3, 'C班': -0.1, 'D班': -0.3}[shift]
            line_modifier = np.random.uniform(-0.2, 0.2)
            
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
            })
            employee_id += 1
    
    return pd.DataFrame(data)

def generate_attendance_data(df_employee, days=30):
    """日次出勤データ生成（欠勤を考慮）"""
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for _, emp in df_employee.iterrows():
        for day in range(days):
            date = (start_date + timedelta(days=day)).date()
            
            # 出勤確率（ベース90%）
            # スキルが高い人ほど出勤率が高い傾向
            attendance_prob = 0.85 + (emp['総合スキルスコア'] - 3.0) * 0.03
            attendance_prob = np.clip(attendance_prob, 0.75, 0.98)
            
            is_attended = np.random.random() < attendance_prob
            
            data.append({
                '従業員ID': emp['従業員ID'],
                '拠点': emp['拠点'],
                'ライン': emp['ライン'],
                'シフト': emp['シフト'],
                '日付': date,
                '出勤': is_attended,
                '総合スキルスコア': emp['総合スキルスコア'],
            })
    
    return pd.DataFrame(data)

def calculate_daily_shift_skills(df_attendance):
    """日次・シフト別の平均スキル計算（出勤者のみ）"""
    # 出勤者のみをフィルタ
    df_attended = df_attendance[df_attendance['出勤'] == True].copy()
    
    # 日付・拠点・ライン・シフト単位で平均スキルを計算
    daily_skills = df_attended.groupby(['日付', '拠点', 'ライン', 'シフト']).agg({
        '総合スキルスコア': 'mean',
        '従業員ID': 'count'  # 出勤人数
    }).reset_index()
    
    daily_skills.columns = ['日付', '拠点', 'ライン', 'シフト', '平均スキルスコア', '出勤人数']
    
    return daily_skills

def generate_production_data_with_skills(df_daily_skills):
    """日次生産データ生成（スキルと連動）"""
    data = []
    
    for _, row in df_daily_skills.iterrows():
        date = row['日付']
        location = row['拠点']
        line = row['ライン']
        shift = row['シフト']
        skill = row['平均スキルスコア']
        n_workers = row['出勤人数']
        
        loc_info = LOCATIONS[location]
        
        # スキルと出勤人数による生産効率への影響
        base_efficiency = loc_info['efficiency_base']
        
        # スキル影響（相関を強くする）
        skill_impact = (skill - 3.0) * 10  # スキル1上昇で+10ポイント
        
        # 出勤人数の影響（少なすぎると効率低下）
        worker_impact = 0
        if n_workers < 3:
            worker_impact = -5 * (3 - n_workers)
        
        # ランダムノイズ（日々の変動）
        daily_noise = np.random.normal(0, 2)
        
        efficiency = base_efficiency + skill_impact + worker_impact + daily_noise
        efficiency = np.clip(efficiency, 50, 120)
        
        # 品質不良率（スキルが高いほど低い、負の相関）
        base_quality = loc_info['quality_base']
        quality_impact = (5.0 - skill) * 0.5  # スキル1上昇で-0.5%
        quality_noise = abs(np.random.normal(0, 0.3))
        
        quality_defect = base_quality + quality_impact + quality_noise
        quality_defect = np.clip(quality_defect, 0.1, 10.0)
        
        # 稼働率・歩留まり
        utilization = 85 + np.random.uniform(-10, 15)
        yield_rate = 92 + np.random.uniform(-5, 8)
        
        data.append({
            '日付': date,
            '拠点': location,
            'ライン': line,
            'シフト': shift,
            '生産効率_指数': round(efficiency, 1),
            '品質不良率': round(quality_defect, 2),
            '稼働率': round(utilization, 1),
            '歩留まり': round(yield_rate, 1),
            '出勤人数': n_workers,
        })
    
    return pd.DataFrame(data)

def generate_location_data():
    """拠点マスタデータ生成"""
    data = []
    for location, info in LOCATIONS.items():
        data.append({
            '拠点': location,
            '国': info['country'],
            '緯度': info['lat'],
            '経度': info['lon'],
            'ベンチマーク拠点': info['benchmark'],
            '設立年': random.randint(1960, 2010),
        })
    return pd.DataFrame(data)

def main():
    """メインデータ生成"""
    print("📊 SDP ダミーデータ生成開始 (v2 - 日次出勤対応)")
    
    # 1. 従業員データ生成
    print("1️⃣ 従業員データ生成中...")
    df_employee = generate_employee_data(n_employees=2000)
    print(f"   ✅ 従業員数: {len(df_employee)}")
    
    # 2. 日次出勤データ生成
    print("2️⃣ 日次出勤データ生成中（30日分）...")
    df_attendance = generate_attendance_data(df_employee, days=30)
    print(f"   ✅ 出勤レコード数: {len(df_attendance)}")
    attendance_rate = df_attendance['出勤'].mean() * 100
    print(f"   📈 平均出勤率: {attendance_rate:.1f}%")
    
    # 3. 日次・シフト別平均スキル計算
    print("3️⃣ 日次シフト別スキル計算中...")
    df_daily_skills = calculate_daily_shift_skills(df_attendance)
    print(f"   ✅ 日次シフトレコード数: {len(df_daily_skills)}")
    
    # 4. 生産データ生成（スキルと連動）
    print("4️⃣ 生産データ生成中...")
    df_production = generate_production_data_with_skills(df_daily_skills)
    print(f"   ✅ 生産レコード数: {len(df_production)}")
    
    # 5. 拠点マスタ生成
    print("5️⃣ 拠点マスタ生成中...")
    df_location = generate_location_data()
    print(f"   ✅ 拠点数: {len(df_location)}")
    
    # データ保存
    print("\n💾 データ保存中...")
    df_employee.to_csv('data/employee_master.csv', index=False, encoding='utf-8-sig')
    df_attendance.to_csv('data/attendance_daily.csv', index=False, encoding='utf-8-sig')
    df_daily_skills.to_csv('data/daily_shift_skills.csv', index=False, encoding='utf-8-sig')
    df_production.to_csv('data/production_daily.csv', index=False, encoding='utf-8-sig')
    df_location.to_csv('data/location_master.csv', index=False, encoding='utf-8-sig')
    
    print("✅ データ生成完了！")
    print("\n📁 生成されたファイル:")
    print("   - data/employee_master.csv (従業員マスタ)")
    print("   - data/attendance_daily.csv (日次出勤データ)")
    print("   - data/daily_shift_skills.csv (日次シフト別平均スキル)")
    print("   - data/production_daily.csv (日次生産データ)")
    print("   - data/location_master.csv (拠点マスタ)")
    
    # データサマリ表示
    print("\n📊 データサマリ:")
    print(f"   従業員総数: {len(df_employee)}")
    print(f"   拠点数: {len(df_location)}")
    print(f"   日数: 30日")
    print(f"   平均出勤率: {attendance_rate:.1f}%")
    print(f"   生産レコード数: {len(df_production)}")
    
    # 相関確認
    corr_eff = df_production[['生産効率_指数']].merge(
        df_daily_skills[['日付', '拠点', 'ライン', 'シフト', '平均スキルスコア']], 
        on=['日付', '拠点', 'ライン', 'シフト']
    )
    corr_value = corr_eff['平均スキルスコア'].corr(corr_eff['生産効率_指数'])
    print(f"\n📈 スキルと生産効率の相関係数: {corr_value:.3f}")

if __name__ == "__main__":
    main()