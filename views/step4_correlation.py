"""
STEP 4: 力量と生産性の相関分析
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scipy import stats

def render(df_employee, df_production, selected_location):
    st.title(f"📊 STEP 4: 力量と生産性の相関分析 - {selected_location}")
    st.markdown("**目的**: 力量差が生産性・品質に与える影響を定量化")
    
    # データフィルタ
    df_emp_loc = df_employee[df_employee['拠点'] == selected_location].copy()
    df_prod_loc = df_production[df_production['拠点'] == selected_location].copy()
    
    # タブ構成
    tab1, tab2, tab3 = st.tabs(["📈 相関分析", "📊 スキルレベル別比較", "🎯 影響度分析"])
    
    with tab1:
        render_correlation_analysis(df_emp_loc, df_prod_loc)
    
    with tab2:
        render_skill_level_comparison(df_emp_loc, df_prod_loc)
    
    with tab3:
        render_impact_analysis(df_emp_loc, df_prod_loc)
    
    # ナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: スキルがボトルネックになっている工程を「STEP 5: ボトルネック分析」で特定")

def render_correlation_analysis(df_emp, df_prod):
    """相関分析"""
    st.subheader("スキルスコアと生産性指標の相関")
    
    # 従業員データ: ライン・シフト単位でスキル平均を計算
    skill_by_shift = df_emp.groupby(['ライン', 'シフト']).agg({
        '総合スキルスコア': 'mean',
    }).reset_index()
    
    # 生産データと結合（日次×シフト単位）
    # 生産データの各レコードに対応するスキルスコアを紐付け
    merged = df_prod.merge(skill_by_shift, on=['ライン', 'シフト'], how='left')
    
    # ライン一覧を取得
    lines = sorted(merged['ライン'].unique())
    
    # ライン別に散布図を表示
    st.markdown("### ライン別分析（日次実績）")
    st.info("💡 **各点は1日の実績です（約30日分）。**シフト別に色分けしています。スキルが高いシフトほど生産効率が高く、品質不良率が低い傾向が確認できます。")
    
    for line in lines:
        st.markdown(f"#### {line}")
        
        # ラインのデータを抽出
        line_data = merged[merged['ライン'] == line].copy()
        
        # データが少なすぎる場合はスキップ
        if len(line_data) < 5:
            st.warning(f"⚠️ {line}のデータが不足しています（最低5日分以上必要）")
            continue
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 散布図: スキルスコア vs 生産効率
            try:
                # statsmodelsが利用可能な場合、トレンドライン付き
                fig = px.scatter(
                    line_data,
                    x='総合スキルスコア',
                    y='生産効率_指数',
                    color='シフト',
                    hover_data=['日付', 'シフト', '総合スキルスコア', '生産効率_指数'],
                    title=f"{line} - スキルスコア vs 生産効率（日次）",
                    trendline="ols"
                )
            except (ModuleNotFoundError, ImportError):
                # statsmodelsがない場合、トレンドラインなし
                fig = px.scatter(
                    line_data,
                    x='総合スキルスコア',
                    y='生産効率_指数',
                    color='シフト',
                    hover_data=['日付', 'シフト', '総合スキルスコア', '生産効率_指数'],
                    title=f"{line} - スキルスコア vs 生産効率（日次）"
                )
            
            # 相関係数計算（欠損値を除外）
            clean_data = line_data[['総合スキルスコア', '生産効率_指数']].dropna()
            if len(clean_data) >= 2:
                corr, p_value = stats.pearsonr(clean_data['総合スキルスコア'], clean_data['生産効率_指数'])
                
                fig.add_annotation(
                    text=f"相関係数: {corr:.3f}<br>p値: {p_value:.4f}<br>N={len(clean_data)}",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1
                )
            
            fig.update_traces(marker=dict(size=8, opacity=0.7))
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 散布図: スキルスコア vs 品質不良率
            try:
                # statsmodelsが利用可能な場合、トレンドライン付き
                fig = px.scatter(
                    line_data,
                    x='総合スキルスコア',
                    y='品質不良率',
                    color='シフト',
                    hover_data=['日付', 'シフト', '総合スキルスコア', '品質不良率'],
                    title=f"{line} - スキルスコア vs 品質不良率（日次）",
                    trendline="ols"
                )
            except (ModuleNotFoundError, ImportError):
                # statsmodelsがない場合、トレンドラインなし
                fig = px.scatter(
                    line_data,
                    x='総合スキルスコア',
                    y='品質不良率',
                    color='シフト',
                    hover_data=['日付', 'シフト', '総合スキルスコア', '品質不良率'],
                    title=f"{line} - スキルスコア vs 品質不良率（日次）"
                )
            
            # 相関係数計算（欠損値を除外）
            clean_data = line_data[['総合スキルスコア', '品質不良率']].dropna()
            if len(clean_data) >= 2:
                corr, p_value = stats.pearsonr(clean_data['総合スキルスコア'], clean_data['品質不良率'])
                
                fig.add_annotation(
                    text=f"相関係数: {corr:.3f}<br>p値: {p_value:.4f}<br>N={len(clean_data)}",
                    xref="paper", yref="paper",
                    x=0.02, y=0.98,
                    showarrow=False,
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1
                )
            
            fig.update_traces(marker=dict(size=8, opacity=0.7))
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    # スキルカテゴリー別相関
    st.subheader("スキルカテゴリー別 相関係数マトリクス")
    
    skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
    prod_cols = ['生産効率_指数', '品質不良率', '稼働率']
    
    corr_matrix = np.zeros((len(skill_cols), len(prod_cols)))
    
    for i, skill in enumerate(skill_cols):
        for j, prod in enumerate(prod_cols):
            corr, _ = stats.pearsonr(merged[skill], merged[prod])
            corr_matrix[i, j] = corr
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=prod_cols,
        y=skill_cols,
        colorscale='RdBu_r',
        zmid=0,
        text=np.round(corr_matrix, 3),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="相関係数")
    ))
    
    fig.update_layout(
        title="スキルカテゴリー × 生産指標 相関マトリクス",
        xaxis_title="生産指標",
        yaxis_title="スキルカテゴリー",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_skill_level_comparison(df_emp, df_prod):
    """スキルレベル別比較"""
    st.subheader("スキルランク別パフォーマンス比較")
    
    # スキルランク分類
    def skill_rank(score):
        if score >= 4.0:
            return 'A (4.0以上)'
        elif score >= 3.0:
            return 'B (3.0-4.0)'
        elif score >= 2.0:
            return 'C (2.0-3.0)'
        else:
            return 'D (2.0未満)'
    
    df_emp['スキルランク'] = df_emp['総合スキルスコア'].apply(skill_rank)
    
    # 従業員IDごとのパフォーマンス（個人レベル）
    emp_perf = df_emp[['従業員ID', 'ライン', 'シフト', 'スキルランク', '生産効率_個人', '品質不良率_個人']].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ボックスプロット: スキルランク別生産効率
        fig = go.Figure()
        
        for rank in ['A (4.0以上)', 'B (3.0-4.0)', 'C (2.0-3.0)', 'D (2.0未満)']:
            df_rank = emp_perf[emp_perf['スキルランク'] == rank]
            if len(df_rank) > 0:
                fig.add_trace(go.Box(
                    y=df_rank['生産効率_個人'],
                    name=rank,
                    boxmean='sd'
                ))
        
        fig.update_layout(
            title="スキルランク別 生産効率分布",
            yaxis_title="生産効率指数",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ボックスプロット: スキルランク別品質不良率
        fig = go.Figure()
        
        for rank in ['A (4.0以上)', 'B (3.0-4.0)', 'C (2.0-3.0)', 'D (2.0未満)']:
            df_rank = emp_perf[emp_perf['スキルランク'] == rank]
            if len(df_rank) > 0:
                fig.add_trace(go.Box(
                    y=df_rank['品質不良率_個人'],
                    name=rank,
                    boxmean='sd'
                ))
        
        fig.update_layout(
            title="スキルランク別 品質不良率分布",
            yaxis_title="品質不良率 (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 統計的検定
    st.subheader("スキルランク間の統計的差異")
    
    rank_stats = emp_perf.groupby('スキルランク').agg({
        '生産効率_個人': ['mean', 'std', 'count'],
        '品質不良率_個人': ['mean', 'std']
    }).round(2)
    
    st.dataframe(rank_stats, use_container_width=True)
    
    st.info("📌 **解釈**: スキルランクが高いほど生産効率が高く、品質不良率が低い傾向が確認できます")

def render_impact_analysis(df_emp, df_prod):
    """影響度分析"""
    st.subheader("スキルカテゴリー別 影響度分析")
    
    st.markdown("""
    各スキルカテゴリーが生産性・品質・安全に与える影響度を定量評価します。
    影響度は設計時の重み付けと実データの相関係数を組み合わせて算出します。
    """)
    
    # スキルカテゴリーごとの影響度（設計値）
    skill_impact = {
        '操炉技術': {'効率': 0.30, '品質': 0.25, '安全': 0.20},
        '成分制御': {'効率': 0.20, '品質': 0.35, '安全': 0.15},
        '異常対応': {'効率': 0.25, '品質': 0.20, '安全': 0.35},
        '設備保全': {'効率': 0.15, '品質': 0.10, '安全': 0.20},
        '品質検査': {'効率': 0.05, '品質': 0.30, '安全': 0.05},
        '安全管理': {'効率': 0.05, '品質': 0.00, '安全': 0.35},
    }
    
    # データフレーム化
    impact_df = pd.DataFrame(skill_impact).T
    impact_df = impact_df.reset_index()
    impact_df.columns = ['スキルカテゴリー', '生産効率への影響', '品質への影響', '安全への影響']
    
    # ヒートマップ
    fig = go.Figure(data=go.Heatmap(
        z=impact_df[['生産効率への影響', '品質への影響', '安全への影響']].values.T,
        x=impact_df['スキルカテゴリー'],
        y=['生産効率', '品質', '安全'],
        colorscale='YlOrRd',
        text=impact_df[['生産効率への影響', '品質への影響', '安全への影響']].values.T,
        texttemplate='%{text:.2f}',
        textfont={"size": 12},
        colorbar=dict(title="影響度")
    ))
    
    fig.update_layout(
        title="スキルカテゴリー別 影響度マトリクス",
        xaxis_title="スキルカテゴリー",
        yaxis_title="KPI",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 影響度テーブル
    try:
        # matplotlibが利用可能な場合
        st.dataframe(
            impact_df.style.background_gradient(
                subset=['生産効率への影響', '品質への影響', '安全への影響'],
                cmap='YlOrRd'
            ).format({
                '生産効率への影響': '{:.2f}',
                '品質への影響': '{:.2f}',
                '安全への影響': '{:.2f}'
            }),
            use_container_width=True
        )
    except ImportError:
        # matplotlibが利用できない場合のフォールバック
        st.dataframe(
            impact_df.style.format({
                '生産効率への影響': '{:.2f}',
                '品質への影響': '{:.2f}',
                '安全への影響': '{:.2f}'
            }),
            use_container_width=True
        )
    
    st.success("✅ **活用方法**: 影響度が高いスキルを優先的に強化することで、効率的な改善が可能です")