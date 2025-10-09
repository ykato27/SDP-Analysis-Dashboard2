"""
STEP 3: ライン別のスキル構造比較
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_employee, selected_location):
    st.title(f"🎯 STEP 3: スキル構造比較 - {selected_location}")
    st.markdown("**目的**: ライン間の力量分布（スキル構成）の違いを把握")
    
    df_emp_loc = df_employee[df_employee['拠点'] == selected_location].copy()
    
    # タブ構成
    tab1, tab2, tab3 = st.tabs(["📊 ライン別スキル分布", "🎨 力量レベル分析", "📈 スキルギャップ"])
    
    with tab1:
        render_skill_radar(df_emp_loc)
    
    with tab2:
        render_skill_level_distribution(df_emp_loc)
    
    with tab3:
        render_skill_gap_analysis(df_emp_loc)
    
    # ナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: スキル分布の偏りが大きいラインを「STEP 4: 相関分析」で詳細検証")

def render_skill_radar(df_emp):
    """ライン別スキルレーダーチャート"""
    st.subheader("ライン別スキルカテゴリー比較")
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    
    # ライン別平均スキル
    line_skills = df_emp.groupby('ライン')[skill_cols].mean()
    
    # レーダーチャート
    fig = go.Figure()
    
    for line in line_skills.index:
        fig.add_trace(go.Scatterpolar(
            r=line_skills.loc[line].values,
            theta=skill_cols,
            fill='toself',
            name=line
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=True,
        title="ライン別スキルプロファイル",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ヒートマップ
    st.subheader("ライン×スキルカテゴリー ヒートマップ")
    
    fig = go.Figure(data=go.Heatmap(
        z=line_skills.values,
        x=skill_cols,
        y=line_skills.index,
        colorscale='RdYlGn',
        text=np.round(line_skills.values, 2),
        texttemplate='%{text}',
        textfont={"size": 11},
        colorbar=dict(title="スキルレベル")
    ))
    
    fig.update_layout(
        title="ライン×スキルカテゴリー ヒートマップ",
        xaxis_title="スキルカテゴリー",
        yaxis_title="ライン",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_skill_level_distribution(df_emp):
    """力量レベル分布分析"""
    st.subheader("力量レベル（A〜D）分布")
    
    # スキルレベルを A〜D にランク分け
    def skill_rank(score):
        if score >= 4.0:
            return 'A (優秀)'
        elif score >= 3.0:
            return 'B (標準)'
        elif score >= 2.0:
            return 'C (要育成)'
        else:
            return 'D (初級)'
    
    df_emp['スキルランク'] = df_emp['総合スキルスコア'].apply(skill_rank)
    
    # ライン別ランク分布
    rank_dist = pd.crosstab(df_emp['ライン'], df_emp['スキルランク'], normalize='index') * 100
    
    # スタックバーチャート
    fig = go.Figure()
    
    colors = {
        'A (優秀)': '#2ca02c',
        'B (標準)': '#1f77b4',
        'C (要育成)': '#ff7f0e',
        'D (初級)': '#d62728'
    }
    
    for rank in ['A (優秀)', 'B (標準)', 'C (要育成)', 'D (初級)']:
        if rank in rank_dist.columns:
            fig.add_trace(go.Bar(
                name=rank,
                x=rank_dist.index,
                y=rank_dist[rank],
                marker_color=colors[rank],
                text=rank_dist[rank].round(1),
                texttemplate='%{text}%',
                textposition='inside'
            ))
    
    fig.update_layout(
        barmode='stack',
        title="ライン別力量レベル分布（％）",
        xaxis_title="ライン",
        yaxis_title="割合 (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # シフト別でも分析
    st.subheader("シフト別力量レベル分布")
    
    selected_line = st.selectbox("分析対象ライン", df_emp['ライン'].unique(), key='skill_level_line')
    df_line = df_emp[df_emp['ライン'] == selected_line]
    
    rank_dist_shift = pd.crosstab(df_line['シフト'], df_line['スキルランク'], normalize='index') * 100
    
    fig = go.Figure()
    
    for rank in ['A (優秀)', 'B (標準)', 'C (要育成)', 'D (初級)']:
        if rank in rank_dist_shift.columns:
            fig.add_trace(go.Bar(
                name=rank,
                x=rank_dist_shift.index,
                y=rank_dist_shift[rank],
                marker_color=colors[rank],
                text=rank_dist_shift[rank].round(1),
                texttemplate='%{text}%',
                textposition='inside'
            ))
    
    fig.update_layout(
        barmode='stack',
        title=f"{selected_line} - シフト別力量レベル分布（％）",
        xaxis_title="シフト",
        yaxis_title="割合 (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_skill_gap_analysis(df_emp):
    """スキルギャップ分析"""
    st.subheader("ライン間スキルギャップ分析")
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    
    # ライン別平均スキル
    line_skills = df_emp.groupby('ライン')[skill_cols].mean()
    
    # 拠点全体の平均（ベンチマーク）
    location_avg = df_emp[skill_cols].mean()
    
    # ギャップ計算
    skill_gaps = line_skills - location_avg
    
    # ヒートマップ
    fig = go.Figure(data=go.Heatmap(
        z=skill_gaps.values,
        x=skill_cols,
        y=skill_gaps.index,
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(skill_gaps.values, 2),
        texttemplate='%{text}',
        textfont={"size": 11},
        colorbar=dict(title="ギャップ")
    ))
    
    fig.update_layout(
        title="ライン別スキルギャップ（拠点平均との差）",
        xaxis_title="スキルカテゴリー",
        yaxis_title="ライン",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ギャップが大きいライン・スキルを特定
    st.subheader("優先改善対象の特定")
    
    # 絶対値でギャップが大きい上位10
    gaps_flat = []
    for line in skill_gaps.index:
        for skill in skill_gaps.columns:
            gaps_flat.append({
                'ライン': line,
                'スキルカテゴリー': skill,
                'ギャップ': skill_gaps.loc[line, skill],
                '絶対値': abs(skill_gaps.loc[line, skill])
            })
    
    gaps_df = pd.DataFrame(gaps_flat).nlargest(10, '絶対値')
    
    try:
        # matplotlibが利用可能な場合
        st.dataframe(
            gaps_df.style.format({
                'ギャップ': '{:.2f}',
                '絶対値': '{:.2f}'
            }).background_gradient(subset=['ギャップ'], cmap='RdYlGn_r'),
            use_container_width=True
        )
    except ImportError:
        # matplotlibが利用できない場合のフォールバック
        st.dataframe(
            gaps_df.style.format({
                'ギャップ': '{:.2f}',
                '絶対値': '{:.2f}'
            }),
            use_container_width=True
        )
    
    st.warning("⚠️ **優先改善ポイント**: ギャップが大きい（マイナス値）項目は集中的な教育が必要です")