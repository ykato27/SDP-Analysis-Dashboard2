"""
STEP 1: 全社俯瞰 - 拠点別 生産性×品質×安全の比較
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_employee, df_production, df_location):
    st.title("🌍 STEP 1: 全社俯瞰 - グローバル拠点パフォーマンス")
    st.markdown("**目的**: グローバル拠点ごとの「成果指標の差異」を定量的に把握")
    
    # 拠点別KPI計算
    kpi = calculate_global_kpi(df_production, df_employee, df_location)
    
    # 3つのタブ
    tab1, tab2, tab3 = st.tabs(["🗺️ 世界地図", "📊 拠点比較", "📈 詳細指標"])
    
    with tab1:
        render_world_map(kpi, df_location)
    
    with tab2:
        render_location_comparison(kpi)
    
    with tab3:
        render_detailed_metrics(kpi)
    
    # 次のステップへのナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: 乖離の大きい拠点を選択して「STEP 2: 拠点内比較」で詳細分析を行います")
    
    # 問題拠点の特定
    bottom_locations = kpi.nsmallest(3, '総合スコア')['拠点'].tolist()
    st.warning(f"⚠️ **要注意拠点**: {', '.join(bottom_locations)}")

def calculate_global_kpi(df_production, df_employee, df_location):
    """グローバルKPI計算"""
    # 生産データ集計
    prod_kpi = df_production.groupby('拠点').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '労災発生': 'sum',
        '稼働率': 'mean',
    }).reset_index()
    
    # スキルデータ集計
    skill_kpi = df_employee.groupby('拠点').agg({
        '総合スキルスコア': 'mean',
    }).reset_index()
    
    # 拠点マスタと結合
    kpi = df_location.merge(prod_kpi, on='拠点').merge(skill_kpi, on='拠点')
    
    # ベンチマーク拠点（日本）の平均値
    benchmark = kpi[kpi['ベンチマーク拠点'] == True]
    benchmark_efficiency = benchmark['生産効率_指数'].mean()
    benchmark_quality = benchmark['品質不良率'].mean()
    benchmark_skill = benchmark['総合スキルスコア'].mean()
    
    # 日本拠点を100とした指数化
    kpi['効率指数'] = (kpi['生産効率_指数'] / benchmark_efficiency * 100).round(1)
    kpi['品質指数'] = (benchmark_quality / kpi['品質不良率'] * 100).round(1)  # 逆数
    kpi['スキル指数'] = (kpi['総合スキルスコア'] / benchmark_skill * 100).round(1)
    
    # 労災発生率（年間・人数あたり）
    days_in_data = (df_production['日付'].max() - df_production['日付'].min()).days
    kpi['労災発生率'] = (kpi['労災発生'] / (days_in_data / 365) / kpi['従業員数'] * 100).round(2)
    
    # 安全指数（労災が少ないほど高い）
    max_accident_rate = kpi['労災発生率'].max()
    kpi['安全指数'] = ((max_accident_rate - kpi['労災発生率']) / max_accident_rate * 100).round(1)
    
    # 総合スコア（3指標の平均）
    kpi['総合スコア'] = ((kpi['効率指数'] + kpi['品質指数'] + kpi['安全指数']) / 3).round(1)
    
    return kpi

def render_world_map(kpi, df_location):
    """世界地図でのヒートマップ表示"""
    st.subheader("拠点別総合スコア - 世界地図")
    
    # Plotly Scattergeo
    fig = go.Figure(data=go.Scattergeo(
        lon=kpi['経度'],
        lat=kpi['緯度'],
        text=kpi['拠点'] + '<br>総合スコア: ' + kpi['総合スコア'].astype(str),
        mode='markers+text',
        marker=dict(
            size=kpi['総合スコア'] / 5,
            color=kpi['総合スコア'],
            colorscale='RdYlGn',
            cmin=50,
            cmax=100,
            colorbar=dict(title="総合スコア"),
            line=dict(width=1, color='white')
        ),
        textposition="top center",
        textfont=dict(size=10)
    ))
    
    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showlakes=True,
            lakecolor='rgb(200, 230, 255)',
        ),
        height=500,
        title="グローバル拠点パフォーマンスマップ"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_location_comparison(kpi):
    """拠点比較グラフ"""
    st.subheader("拠点別 3軸比較（効率・品質・安全）")
    
    # レーダーチャート
    col1, col2 = st.columns(2)
    
    with col1:
        # 上位3拠点
        top3 = kpi.nlargest(3, '総合スコア')
        fig = create_radar_chart(top3, "上位3拠点")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 下位3拠点
        bottom3 = kpi.nsmallest(3, '総合スコア')
        fig = create_radar_chart(bottom3, "下位3拠点（要改善）")
        st.plotly_chart(fig, use_container_width=True)
    
    # バーチャート（全拠点）
    st.subheader("全拠点の指数比較")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='効率指数',
        x=kpi['拠点'],
        y=kpi['効率指数'],
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='品質指数',
        x=kpi['拠点'],
        y=kpi['品質指数'],
        marker_color='#2ca02c'
    ))
    
    fig.add_trace(go.Bar(
        name='安全指数',
        x=kpi['拠点'],
        y=kpi['安全指数'],
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        barmode='group',
        height=400,
        xaxis_title="拠点",
        yaxis_title="指数（日本拠点=100）",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_radar_chart(df, title):
    """レーダーチャート作成"""
    categories = ['効率指数', '品質指数', '安全指数', 'スキル指数']
    
    fig = go.Figure()
    
    for _, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row['効率指数'], row['品質指数'], row['安全指数'], row['スキル指数']],
            theta=categories,
            fill='toself',
            name=row['拠点']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 120])
        ),
        showlegend=True,
        title=title,
        height=400
    )
    
    return fig

def render_detailed_metrics(kpi):
    """詳細指標テーブル"""
    st.subheader("拠点別詳細指標")
    
    # 表示用に整形
    display_df = kpi[[
        '拠点', '国', 'ベンチマーク拠点',
        '総合スコア', '効率指数', '品質指数', '安全指数', 'スキル指数',
        '生産効率_指数', '品質不良率', '労災発生率', '総合スキルスコア',
        '稼働率', '従業員数'
    ]].copy()
    
    # スタイリング
    def highlight_score(val):
        if isinstance(val, (int, float)):
            if val >= 90:
                return 'background-color: #d4edda'
            elif val >= 70:
                return 'background-color: #fff3cd'
            elif val < 70:
                return 'background-color: #f8d7da'
        return ''
    
    styled_df = display_df.style.applymap(
        highlight_score,
        subset=['総合スコア', '効率指数', '品質指数', '安全指数']
    ).format({
        '総合スコア': '{:.1f}',
        '効率指数': '{:.1f}',
        '品質指数': '{:.1f}',
        '安全指数': '{:.1f}',
        'スキル指数': '{:.1f}',
        '生産効率_指数': '{:.1f}',
        '品質不良率': '{:.2f}%',
        '労災発生率': '{:.2f}%',
        '総合スキルスコア': '{:.2f}',
        '稼働率': '{:.1f}%',
    })
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # ダウンロードボタン
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSVダウンロード",
        data=csv,
        file_name="global_kpi.csv",
        mime="text/csv"
    )
