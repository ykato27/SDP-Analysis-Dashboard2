"""
STEP 2: 拠点比較 - 拠点間・ライン別・シフト別のパフォーマンス差異
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_employee, df_production, df_location):
    st.title(f"🏭 STEP 2: 拠点比較分析")
    st.markdown("**目的**: 拠点間および同一拠点内での組織・シフトごとの生産差を把握")
    
    # タブ構成
    tab1, tab2, tab3 = st.tabs(["🌐 拠点間比較", "📊 拠点内ライン分析", "🕐 拠点内シフト分析"])
    
    with tab1:
        render_location_comparison(df_employee, df_production, df_location)
    
    with tab2:
        render_within_location_line_analysis(df_employee, df_production, df_location)
    
    with tab3:
        render_within_location_shift_analysis(df_employee, df_production, df_location)
    
    # ナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: 差異の大きい拠点・ライン・シフトを「STEP 3: スキル構造比較」で詳細分析")

def render_location_comparison(df_employee, df_production, df_location):
    """拠点間比較分析"""
    st.subheader("🌐 拠点間パフォーマンス比較")
    
    # 比較する拠点を選択
    st.markdown("### 比較対象拠点の選択")
    
    all_locations = df_location['拠点'].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        location_a = st.selectbox(
            "拠点A（ベース）", 
            all_locations,
            index=0,
            key='location_a'
        )
    
    with col2:
        # 拠点Aと異なる拠点をデフォルトで選択
        default_b_index = 1 if len(all_locations) > 1 else 0
        location_b = st.selectbox(
            "拠点B（比較対象）",
            all_locations,
            index=default_b_index,
            key='location_b'
        )
    
    if location_a == location_b:
        st.warning("⚠️ 異なる拠点を選択してください")
        return
    
    # 拠点AとBのデータを抽出
    df_prod_a = df_production[df_production['拠点'] == location_a]
    df_prod_b = df_production[df_production['拠点'] == location_b]
    df_emp_a = df_employee[df_employee['拠点'] == location_a]
    df_emp_b = df_employee[df_employee['拠点'] == location_b]
    
    # KPI比較
    st.markdown("### 総合KPI比較")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        eff_a = df_prod_a['生産効率_指数'].mean()
        eff_b = df_prod_b['生産効率_指数'].mean()
        delta = eff_b - eff_a
        st.metric(
            "生産効率指数",
            f"{eff_b:.1f}",
            f"{delta:+.1f} vs {location_a}",
            delta_color="normal"
        )
    
    with col2:
        qual_a = df_prod_a['品質不良率'].mean()
        qual_b = df_prod_b['品質不良率'].mean()
        delta = qual_b - qual_a
        st.metric(
            "品質不良率",
            f"{qual_b:.2f}%",
            f"{delta:+.2f}% vs {location_a}",
            delta_color="inverse"
        )
    
    with col3:
        skill_a = df_emp_a['総合スキルスコア'].mean()
        skill_b = df_emp_b['総合スキルスコア'].mean()
        delta = skill_b - skill_a
        st.metric(
            "平均スキルスコア",
            f"{skill_b:.2f}",
            f"{delta:+.2f} vs {location_a}",
            delta_color="normal"
        )
    
    with col4:
        util_a = df_prod_a['稼働率'].mean()
        util_b = df_prod_b['稼働率'].mean()
        delta = util_b - util_a
        st.metric(
            "稼働率",
            f"{util_b:.1f}%",
            f"{delta:+.1f}% vs {location_a}",
            delta_color="normal"
        )
    
    # ライン別比較
    st.markdown("### ライン別パフォーマンス比較")
    
    # ライン別集計
    line_a = df_prod_a.groupby('ライン').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
    }).reset_index()
    line_a['拠点'] = location_a
    
    line_b = df_prod_b.groupby('ライン').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
    }).reset_index()
    line_b['拠点'] = location_b
    
    line_comparison = pd.concat([line_a, line_b], ignore_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 生産効率比較
        fig = px.bar(
            line_comparison,
            x='ライン',
            y='生産効率_指数',
            color='拠点',
            barmode='group',
            title=f"ライン別生産効率比較: {location_a} vs {location_b}",
            color_discrete_map={location_a: '#1f77b4', location_b: '#ff7f0e'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 品質不良率比較
        fig = px.bar(
            line_comparison,
            x='ライン',
            y='品質不良率',
            color='拠点',
            barmode='group',
            title=f"ライン別品質不良率比較: {location_a} vs {location_b}",
            color_discrete_map={location_a: '#1f77b4', location_b: '#ff7f0e'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # スキル比較
    st.markdown("### スキルプロファイル比較")
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    
    skill_a = df_emp_a[skill_cols].mean()
    skill_b = df_emp_b[skill_cols].mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=skill_a.values,
        theta=skill_cols,
        fill='toself',
        name=location_a,
        line_color='#1f77b4'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=skill_b.values,
        theta=skill_cols,
        fill='toself',
        name=location_b,
        line_color='#ff7f0e'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title=f"スキルプロファイル比較: {location_a} vs {location_b}",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ボックスプロット比較
    st.markdown("### 分布比較（ボックスプロット）")
    
    st.markdown("#### 生産指標の分布比較")
    col1, col2 = st.columns(2)
    
    with col1:
        # 生産効率分布
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=df_prod_a['生産効率_指数'],
            name=location_a,
            marker_color='#1f77b4',
            boxmean='sd'
        ))
        
        fig.add_trace(go.Box(
            y=df_prod_b['生産効率_指数'],
            name=location_b,
            marker_color='#ff7f0e',
            boxmean='sd'
        ))
        
        fig.update_layout(
            title="生産効率指数の分布",
            yaxis_title="生産効率指数",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 品質不良率分布
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=df_prod_a['品質不良率'],
            name=location_a,
            marker_color='#1f77b4',
            boxmean='sd'
        ))
        
        fig.add_trace(go.Box(
            y=df_prod_b['品質不良率'],
            name=location_b,
            marker_color='#ff7f0e',
            boxmean='sd'
        ))
        
        fig.update_layout(
            title="品質不良率の分布",
            yaxis_title="品質不良率 (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # スキルカテゴリ別分布比較
    st.markdown("#### スキルカテゴリ別の分布比較")
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    
    # 3列×2行のレイアウト
    col1, col2, col3 = st.columns(3)
    
    for idx, skill in enumerate(skill_cols):
        col = [col1, col2, col3][idx % 3]
        
        with col:
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=df_emp_a[skill],
                name=location_a,
                marker_color='#1f77b4',
                boxmean='sd'
            ))
            
            fig.add_trace(go.Box(
                y=df_emp_b[skill],
                name=location_b,
                marker_color='#ff7f0e',
                boxmean='sd'
            ))
            
            fig.update_layout(
                title=f"{skill}の分布",
                yaxis_title="スキルレベル",
                yaxis_range=[0, 5.5],
                height=350,
                showlegend=(idx == 0)  # 最初のグラフのみ凡例表示
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_within_location_line_analysis(df_employee, df_production, df_location):
    """拠点内ライン別分析"""
    st.subheader("📊 拠点内ライン別パフォーマンス比較")
    
    # 拠点選択
    selected_location = st.selectbox(
        "分析対象拠点を選択",
        df_location['拠点'].tolist(),
        key='line_location'
    )
    
    df_prod_loc = df_production[df_production['拠点'] == selected_location].copy()
    df_emp_loc = df_employee[df_employee['拠点'] == selected_location].copy()
    
    # ライン別集計
    line_kpi = df_prod_loc.groupby('ライン').agg({
        '生産効率_指数': ['mean', 'std'],
        '品質不良率': ['mean', 'std'],
        '稼働率': 'mean',
        '歩留まり': 'mean',
    }).reset_index()
    
    line_kpi.columns = ['ライン', '生産効率_平均', '生産効率_std', 
                        '品質不良率_平均', '品質不良率_std', '稼働率', '歩留まり']
    
    # スキル平均も追加
    line_skill = df_emp_loc.groupby('ライン')['総合スキルスコア'].mean().reset_index()
    line_kpi = line_kpi.merge(line_skill, on='ライン')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ボックスプロット: 生産効率
        fig = go.Figure()
        for line in df_prod_loc['ライン'].unique():
            df_line = df_prod_loc[df_prod_loc['ライン'] == line]
            fig.add_trace(go.Box(
                y=df_line['生産効率_指数'],
                name=line,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title=f"{selected_location} - ライン別生産効率分布",
            yaxis_title="生産効率指数",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ボックスプロット: 品質不良率
        fig = go.Figure()
        for line in df_prod_loc['ライン'].unique():
            df_line = df_prod_loc[df_prod_loc['ライン'] == line]
            fig.add_trace(go.Box(
                y=df_line['品質不良率'],
                name=line,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title=f"{selected_location} - ライン別品質不良率分布",
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
        title=f"{selected_location} - ライン別パフォーマンスヒートマップ（正規化スコア）",
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

def render_within_location_shift_analysis(df_employee, df_production, df_location):
    """拠点内シフト別分析"""
    st.subheader("🕐 拠点内シフト別パフォーマンス比較")
    
    # 拠点選択
    selected_location = st.selectbox(
        "分析対象拠点を選択",
        df_location['拠点'].tolist(),
        key='shift_location'
    )
    
    df_prod_loc = df_production[df_production['拠点'] == selected_location].copy()
    df_emp_loc = df_employee[df_employee['拠点'] == selected_location].copy()
    
    # ライン選択
    selected_line = st.selectbox(
        "分析対象ラインを選択", 
        df_prod_loc['ライン'].unique(),
        key='shift_line'
    )
    
    df_line = df_prod_loc[df_prod_loc['ライン'] == selected_line]
    
    # シフト別集計
    shift_kpi = df_line.groupby('シフト').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '稼働率': 'mean',
    }).reset_index()
    
    # スキル平均
    df_emp_line = df_emp_loc[df_emp_loc['ライン'] == selected_line]
    shift_skill = df_emp_line.groupby('シフト')['総合スキルスコア'].mean().reset_index()
    shift_kpi = shift_kpi.merge(shift_skill, on='シフト', how='left')
    
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
            title=f"{selected_location} / {selected_line} - シフト別生産効率",
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
            title=f"{selected_location} / {selected_line} - シフト別品質不良率",
            yaxis_title="品質不良率 (%)",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # シフト別スキルとパフォーマンスの相関
    st.subheader("シフト別スキルとパフォーマンスの関係")
    
    # 欠損値を除外
    shift_kpi_clean = shift_kpi.dropna(subset=['総合スキルスコア'])
    
    if len(shift_kpi_clean) > 0:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=shift_kpi_clean['総合スキルスコア'],
            y=shift_kpi_clean['生産効率_指数'],
            mode='markers+text',
            text=shift_kpi_clean['シフト'],
            textposition='top center',
            marker=dict(size=15, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(shift_kpi_clean)]),
            name='シフト'
        ))
        
        fig.update_layout(
            title=f"{selected_location} / {selected_line} - スキルスコア vs 生産効率",
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