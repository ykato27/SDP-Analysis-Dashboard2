"""
STEP 2: 拠点内比較 - ライン別・シフト別のパフォーマンス差異
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_employee, df_production, selected_location):
    st.title(f"🏭 STEP 2: 拠点内比較 - {selected_location}")
    st.markdown("**目的**: 同一拠点内での組織・シフトごとの生産差を把握")
    
    # 拠点データのフィルタ
    df_prod_loc = df_production[df_production['拠点'] == selected_location].copy()
    df_emp_loc = df_employee[df_employee['拠点'] == selected_location].copy()
    
    # タブ構成
    tab1, tab2, tab3 = st.tabs(["📊 ライン別分析", "🕐 シフト別分析", "📉 時系列トレンド"])
    
    with tab1:
        render_line_analysis(df_prod_loc, df_emp_loc)
    
    with tab2:
        render_shift_analysis(df_prod_loc, df_emp_loc)
    
    with tab3:
        render_time_series(df_prod_loc)
    
    # ナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: 差異の大きいライン・シフトを選択して「STEP 3: スキル構造比較」へ")

def render_line_analysis(df_prod, df_emp):
    """ライン別分析"""
    st.subheader("ライン別パフォーマンス比較")
    
    # ライン別集計
    line_kpi = df_prod.groupby('ライン').agg({
        '生産効率_指数': ['mean', 'std'],
        '品質不良率': ['mean', 'std'],
        '稼働率': 'mean',
        '歩留まり': 'mean',
    }).reset_index()
    
    line_kpi.columns = ['ライン', '生産効率_平均', '生産効率_std', 
                        '品質不良率_平均', '品質不良率_std', '稼働率', '歩留まり']
    
    # スキル平均も追加
    line_skill = df_emp.groupby('ライン')['総合スキルスコア'].mean().reset_index()
    line_kpi = line_kpi.merge(line_skill, on='ライン')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ボックスプロット: 生産効率
        fig = go.Figure()
        for line in df_prod['ライン'].unique():
            df_line = df_prod[df_prod['ライン'] == line]
            fig.add_trace(go.Box(
                y=df_line['生産効率_指数'],
                name=line,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title="ライン別 生産効率分布",
            yaxis_title="生産効率指数",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ボックスプロット: 品質不良率
        fig = go.Figure()
        for line in df_prod['ライン'].unique():
            df_line = df_prod[df_prod['ライン'] == line]
            fig.add_trace(go.Box(
                y=df_line['品質不良率'],
                name=line,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title="ライン別 品質不良率分布",
            yaxis_title="品質不良率 (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ヒートマップ: ライン別KPI
    st.subheader("ライン別KPIヒートマップ")
    
    # 正規化（0-100スケール）
    heatmap_data = line_kpi[['ライン', '生産効率_平均', '品質不良率_平均', '稼働率', '歩留まり', '総合スキルスコア']].copy()
    
    # 品質不良率は逆転（低いほど良い）
    heatmap_data['品質スコア'] = 100 - (heatmap_data['品質不良率_平均'] / heatmap_data['品質不良率_平均'].max() * 100)
    
    # 正規化
    for col in ['生産効率_平均', '稼働率', '歩留まり', '総合スキルスコア']:
        heatmap_data[col] = (heatmap_data[col] / heatmap_data[col].max() * 100)
    
    # ヒートマップ用に整形
    heatmap_values = heatmap_data[['生産効率_平均', '品質スコア', '稼働率', '歩留まり', '総合スキルスコア']].values
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_values.T,
        x=heatmap_data['ライン'],
        y=['生産効率', '品質', '稼働率', '歩留まり', 'スキル'],
        colorscale='RdYlGn',
        text=np.round(heatmap_values.T, 1),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="スコア")
    ))
    
    fig.update_layout(
        title="ライン別パフォーマンスヒートマップ（正規化スコア）",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 詳細テーブル
    st.subheader("ライン別詳細データ")
    st.dataframe(
        line_kpi.style.format({
            '生産効率_平均': '{:.1f}',
            '生産効率_std': '{:.1f}',
            '品質不良率_平均': '{:.2f}%',
            '品質不良率_std': '{:.2f}',
            '稼働率': '{:.1f}%',
            '歩留まり': '{:.1f}%',
            '総合スキルスコア': '{:.2f}'
        }),
        use_container_width=True
    )

def render_shift_analysis(df_prod, df_emp):
    """シフト別分析"""
    st.subheader("シフト別パフォーマンス比較")
    
    # ライン選択
    selected_line = st.selectbox("分析対象ラインを選択", df_prod['ライン'].unique())
    
    df_line = df_prod[df_prod['ライン'] == selected_line]
    
    # シフト別集計
    shift_kpi = df_line.groupby('シフト').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '稼働率': 'mean',
    }).reset_index()
    
    # スキル平均
    df_emp_line = df_emp[df_emp['ライン'] == selected_line]
    shift_skill = df_emp_line.groupby('シフト')['総合スキルスコア'].mean().reset_index()
    shift_kpi = shift_kpi.merge(shift_skill, on='シフト')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # シフト別バーチャート: 生産効率
        fig = go.Figure(data=[
            go.Bar(
                x=shift_kpi['シフト'],
                y=shift_kpi['生産効率_指数'],
                text=shift_kpi['生産効率_指数'].round(1),
                textposition='auto',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        ])
        
        fig.update_layout(
            title=f"{selected_line} - シフト別生産効率",
            yaxis_title="生産効率指数",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # シフト別バーチャート: 品質不良率
        fig = go.Figure(data=[
            go.Bar(
                x=shift_kpi['シフト'],
                y=shift_kpi['品質不良率'],
                text=shift_kpi['品質不良率'].round(2),
                textposition='auto',
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            )
        ])
        
        fig.update_layout(
            title=f"{selected_line} - シフト別品質不良率",
            yaxis_title="品質不良率 (%)",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # シフト別スキルとパフォーマンスの相関
    st.subheader("シフト別スキルとパフォーマンスの関係")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=shift_kpi['総合スキルスコア'],
        y=shift_kpi['生産効率_指数'],
        mode='markers+text',
        text=shift_kpi['シフト'],
        textposition='top center',
        marker=dict(size=15, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
        name='シフト'
    ))
    
    fig.update_layout(
        title="スキルスコア vs 生産効率（シフト別）",
        xaxis_title="総合スキルスコア",
        yaxis_title="生産効率指数",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 詳細テーブル
    st.dataframe(
        shift_kpi.style.format({
            '生産効率_指数': '{:.1f}',
            '品質不良率': '{:.2f}%',
            '稼働率': '{:.1f}%',
            '総合スキルスコア': '{:.2f}'
        }),
        use_container_width=True
    )

def render_time_series(df_prod):
    """時系列トレンド分析"""
    st.subheader("時系列トレンド分析")
    
    # 月次集計
    df_prod['年月'] = pd.to_datetime(df_prod['日付']).dt.to_period('M')
    
    monthly = df_prod.groupby(['年月', 'ライン']).agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
    }).reset_index()
    
    monthly['年月'] = monthly['年月'].astype(str)
    
    # 生産効率トレンド
    fig = px.line(
        monthly, 
        x='年月', 
        y='生産効率_指数', 
        color='ライン',
        title="月次生産効率トレンド（ライン別）",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="年月",
        yaxis_title="生産効率指数",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 品質不良率トレンド
    fig = px.line(
        monthly, 
        x='年月', 
        y='品質不良率', 
        color='ライン',
        title="月次品質不良率トレンド（ライン別）",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="年月",
        yaxis_title="品質不良率 (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
