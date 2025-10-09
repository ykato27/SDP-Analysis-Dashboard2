"""
STEP 5: 工程別スキルボトルネック分析
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render(df_bottleneck, selected_location):
    st.title(f"🔍 STEP 5: 工程別スキルボトルネック分析 - {selected_location}")
    st.markdown("**目的**: どの工程・職種のスキル不足が課題を生んでいるか特定")
    
    df_loc = df_bottleneck[df_bottleneck['拠点'] == selected_location].copy()
    
    # タブ構成
    tab1, tab2, tab3 = st.tabs(["🎯 ボトルネック特定", "📊 工程別分析", "🔥 優先順位マトリクス"])
    
    with tab1:
        render_bottleneck_identification(df_loc)
    
    with tab2:
        render_process_analysis(df_loc)
    
    with tab3:
        render_priority_matrix(df_loc)
    
    # ナビゲーション
    st.markdown("---")
    st.info("💡 **次のステップ**: ボトルネック工程の担当者を「STEP 6: 個人・チーム分析」で確認")

def render_bottleneck_identification(df):
    """ボトルネック特定"""
    st.subheader("スキルギャップ上位ランキング")
    
    # ギャップが大きい順にソート
    df_sorted = df.sort_values('スキルギャップ', ascending=False).head(20)
    
    # 棒グラフ
    fig = go.Figure()
    
    # ラベル作成
    df_sorted['ラベル'] = df_sorted['工程'] + ' - ' + df_sorted['スキルカテゴリ']
    
    # 色分け（ギャップが正=要求レベル高い、負=現在レベル高い）
    colors = ['#d62728' if x > 0 else '#2ca02c' for x in df_sorted['スキルギャップ']]
    
    fig.add_trace(go.Bar(
        y=df_sorted['ラベル'],
        x=df_sorted['スキルギャップ'],
        orientation='h',
        marker_color=colors,
        text=df_sorted['スキルギャップ'].round(2),
        textposition='auto'
    ))
    
    fig.update_layout(
        title="スキルギャップ上位20（工程×スキルカテゴリ）",
        xaxis_title="スキルギャップ（要求レベル - 現在レベル）",
        yaxis_title="",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.warning("⚠️ **赤色（正の値）**: 要求レベルに対してスキルが不足している項目 → 優先的に教育・訓練が必要")
    
    # 詳細テーブル
    st.subheader("ボトルネック詳細データ")
    
    try:
        # matplotlibが利用可能な場合
        st.dataframe(
            df_sorted[['工程', 'スキルカテゴリ', '要求レベル', '現在レベル', 'スキルギャップ', 
                      '影響度_生産', '影響度_品質', '影響度_安全']].style.format({
                '要求レベル': '{:.1f}',
                '現在レベル': '{:.1f}',
                'スキルギャップ': '{:.2f}',
                '影響度_生産': '{:.2f}',
                '影響度_品質': '{:.2f}',
                '影響度_安全': '{:.2f}'
            }).background_gradient(subset=['スキルギャップ'], cmap='RdYlGn_r'),
            use_container_width=True,
            height=400
        )
    except ImportError:
        # matplotlibが利用できない場合のフォールバック
        st.dataframe(
            df_sorted[['工程', 'スキルカテゴリ', '要求レベル', '現在レベル', 'スキルギャップ', 
                      '影響度_生産', '影響度_品質', '影響度_安全']].style.format({
                '要求レベル': '{:.1f}',
                '現在レベル': '{:.1f}',
                'スキルギャップ': '{:.2f}',
                '影響度_生産': '{:.2f}',
                '影響度_品質': '{:.2f}',
                '影響度_安全': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )

def render_process_analysis(df):
    """工程別分析"""
    st.subheader("工程別スキルギャップ分析")
    
    # 工程別集計
    process_gap = df.groupby('工程').agg({
        'スキルギャップ': ['mean', 'max', 'count'],
        '影響度_生産': 'mean',
        '影響度_品質': 'mean',
        '影響度_安全': 'mean'
    }).reset_index()
    
    process_gap.columns = ['工程', 'ギャップ平均', 'ギャップ最大', 'スキル項目数', 
                           '生産影響度', '品質影響度', '安全影響度']
    
    # バーチャート: 工程別平均ギャップ
    fig = go.Figure(data=[
        go.Bar(
            x=process_gap['工程'],
            y=process_gap['ギャップ平均'],
            marker_color=['#d62728' if x > 0.3 else '#ff7f0e' if x > 0 else '#2ca02c' 
                         for x in process_gap['ギャップ平均']],
            text=process_gap['ギャップ平均'].round(2),
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="工程別 平均スキルギャップ",
        xaxis_title="工程",
        yaxis_title="平均スキルギャップ",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ヒートマップ: 工程×スキルカテゴリ
    st.subheader("工程×スキルカテゴリ ギャップヒートマップ")
    
    pivot = df.pivot_table(
        values='スキルギャップ',
        index='工程',
        columns='スキルカテゴリ',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn_r',
        zmid=0,
        text=np.round(pivot.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="ギャップ")
    ))
    
    fig.update_layout(
        title="工程×スキルカテゴリ ギャップマトリクス",
        xaxis_title="スキルカテゴリ",
        yaxis_title="工程",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 工程別詳細テーブル
    try:
        # matplotlibが利用可能な場合
        st.dataframe(
            process_gap.style.background_gradient(subset=['ギャップ平均', 'ギャップ最大'], cmap='RdYlGn_r')
                            .format({
                                'ギャップ平均': '{:.2f}',
                                'ギャップ最大': '{:.2f}',
                                '生産影響度': '{:.2f}',
                                '品質影響度': '{:.2f}',
                                '安全影響度': '{:.2f}'
                            }),
            use_container_width=True
        )
    except ImportError:
        # matplotlibが利用できない場合のフォールバック
        st.dataframe(
            process_gap.style.format({
                'ギャップ平均': '{:.2f}',
                'ギャップ最大': '{:.2f}',
                '生産影響度': '{:.2f}',
                '品質影響度': '{:.2f}',
                '安全影響度': '{:.2f}'
            }),
            use_container_width=True
        )

def render_priority_matrix(df):
    """優先順位マトリクス"""
    st.subheader("優先順位マトリクス（ギャップ × 影響度）")
    
    st.markdown("""
    **優先度の考え方**: スキルギャップが大きく、かつ影響度が高い項目を優先的に改善すべき
    """)
    
    # 総合影響度を計算（生産・品質・安全の平均）
    df['総合影響度'] = (df['影響度_生産'] + df['影響度_品質'] + df['影響度_安全']) / 3
    
    # 散布図
    fig = px.scatter(
        df,
        x='スキルギャップ',
        y='総合影響度',
        color='工程',
        size=abs(df['スキルギャップ']) * 10,
        hover_data=['スキルカテゴリ', '要求レベル', '現在レベル'],
        title="スキルギャップ × 影響度 マトリクス"
    )
    
    # 優先度エリアを色分け
    # 高優先度（ギャップ大 & 影響度高）
    fig.add_shape(
        type="rect",
        x0=0.5, x1=df['スキルギャップ'].max(),
        y0=0.2, y1=df['総合影響度'].max(),
        fillcolor="red",
        opacity=0.1,
        layer="below",
        line_width=0,
    )
    
    fig.add_annotation(
        x=0.75, y=0.35,
        text="高優先度",
        showarrow=False,
        font=dict(size=14, color="red")
    )
    
    fig.update_layout(
        xaxis_title="スキルギャップ（要求 - 現在）",
        yaxis_title="総合影響度",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 優先度別分類
    st.subheader("優先度別アクション項目")
    
    def priority_level(row):
        if row['スキルギャップ'] > 0.5 and row['総合影響度'] > 0.2:
            return '🔴 最優先'
        elif row['スキルギャップ'] > 0.3 and row['総合影響度'] > 0.15:
            return '🟡 優先'
        elif row['スキルギャップ'] > 0:
            return '🟢 中期対応'
        else:
            return '⚪ 現状維持'
    
    df['優先度'] = df.apply(priority_level, axis=1)
    
    # 優先度別カウント
    priority_count = df['優先度'].value_counts()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("🔴 最優先項目", priority_count.get('🔴 最優先', 0))
        st.metric("🟡 優先項目", priority_count.get('🟡 優先', 0))
        st.metric("🟢 中期対応項目", priority_count.get('🟢 中期対応', 0))
    
    with col2:
        # 優先度別リスト
        high_priority = df[df['優先度'] == '🔴 最優先'].sort_values('スキルギャップ', ascending=False)
        
        if len(high_priority) > 0:
            st.dataframe(
                high_priority[['工程', 'スキルカテゴリ', 'スキルギャップ', '総合影響度', '優先度']].head(10).style.format({
                    'スキルギャップ': '{:.2f}',
                    '総合影響度': '{:.2f}'
                }),
                use_container_width=True
            )
        else:
            st.success("✅ 最優先項目なし（スキルレベル良好）")