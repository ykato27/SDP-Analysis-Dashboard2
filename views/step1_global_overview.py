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
    tab1, tab2, tab3 = st.tabs(["📊 エグゼクティブサマリー", "🔍 拠点比較分析", "📈 詳細指標"])
    
    with tab1:
        render_executive_summary(kpi)
    
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

def render_executive_summary(kpi):
    """エグゼクティブサマリー - 経営者向けダッシュボード"""
    st.subheader("📊 グローバル拠点パフォーマンス サマリー")
    
    # KPIカード（4つの主要指標）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_efficiency = kpi['効率指数'].mean()
        st.metric(
            label="平均効率指数",
            value=f"{avg_efficiency:.1f}",
            delta=f"{avg_efficiency - 100:.1f}" if avg_efficiency != 100 else "0.0",
            help="ベンチマーク拠点（日本）を100とした指数"
        )
    
    with col2:
        avg_quality = kpi['品質指数'].mean()
        st.metric(
            label="平均品質指数",
            value=f"{avg_quality:.1f}",
            delta=f"{avg_quality - 100:.1f}" if avg_quality != 100 else "0.0",
            help="ベンチマーク拠点（日本）を100とした指数"
        )
    
    with col3:
        avg_safety = kpi['安全指数'].mean()
        st.metric(
            label="平均安全指数",
            value=f"{avg_safety:.1f}",
            delta=f"{avg_safety - 100:.1f}" if avg_safety != 100 else "0.0",
            help="労災発生率が低いほど高い指数"
        )
    
    with col4:
        avg_skill = kpi['スキル指数'].mean()
        st.metric(
            label="平均スキル指数",
            value=f"{avg_skill:.1f}",
            delta=f"{avg_skill - 100:.1f}" if avg_skill != 100 else "0.0",
            help="ベンチマーク拠点（日本）を100とした指数"
        )
    
    st.markdown("---")
    
    # 拠点別総合スコアランキング
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### 📈 総合スコア ランキング")
        
        # 上位5拠点
        st.markdown("**🏆 Top 5 拠点**")
        top5 = kpi.nlargest(5, '総合スコア')[['拠点', '総合スコア', '国']].reset_index(drop=True)
        top5.index = top5.index + 1
        
        for idx, row in top5.iterrows():
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else "⭐"
            st.markdown(f"{medal} **{row['拠点']}** ({row['国']}): {row['総合スコア']:.1f}")
        
        st.markdown("---")
        
        # 下位5拠点
        st.markdown("**⚠️ Bottom 5 拠点（要改善）**")
        bottom5 = kpi.nsmallest(5, '総合スコア')[['拠点', '総合スコア', '国']].reset_index(drop=True)
        
        for idx, row in bottom5.iterrows():
            st.markdown(f"🔻 **{row['拠点']}** ({row['国']}): {row['総合スコア']:.1f}")
    
    with col2:
        st.markdown("### 📊 拠点別総合スコア比較")
        
        # 総合スコアの棒グラフ（ベンチマーク拠点を強調）
        fig = go.Figure()
        
        # データを総合スコアでソート
        kpi_sorted = kpi.sort_values('総合スコア', ascending=True)
        
        # ベンチマーク拠点とその他で色分け
        colors = ['#2ca02c' if bench else '#1f77b4' 
                  for bench in kpi_sorted['ベンチマーク拠点']]
        
        fig.add_trace(go.Bar(
            y=kpi_sorted['拠点'],
            x=kpi_sorted['総合スコア'],
            orientation='h',
            marker_color=colors,
            text=kpi_sorted['総合スコア'].round(1),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>総合スコア: %{x:.1f}<extra></extra>'
        ))
        
        # ベンチマーク基準線（100）
        fig.add_vline(x=100, line_dash="dash", line_color="red", 
                      annotation_text="ベンチマーク基準",
                      annotation_position="top right")
        
        fig.update_layout(
            height=400,
            xaxis_title="総合スコア",
            yaxis_title="",
            showlegend=False,
            margin=dict(l=150)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 凡例
        st.caption("🟢 緑: ベンチマーク拠点（日本） | 🔵 青: その他拠点")
    
    st.markdown("---")
    
    # 4指標の相関ヒートマップ
    st.markdown("### 🔥 指標間の相関分析")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # 相関行列
        correlation_cols = ['効率指数', '品質指数', '安全指数', 'スキル指数']
        corr_matrix = kpi[correlation_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=correlation_cols,
            y=correlation_cols,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="相関係数")
        ))
        
        fig.update_layout(
            title="指標間の相関マトリクス",
            height=350,
            xaxis_title="",
            yaxis_title=""
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📌 主要インサイト")
        
        # スキルと効率の相関
        skill_efficiency_corr = kpi['スキル指数'].corr(kpi['効率指数'])
        st.info(f"""
        **スキル ↔ 効率の相関**  
        相関係数: {skill_efficiency_corr:.2f}
        
        {"✅ 強い正の相関" if skill_efficiency_corr > 0.7 else "⚠️ 相関が弱い"}
        """)
        
        # スキルと品質の相関
        skill_quality_corr = kpi['スキル指数'].corr(kpi['品質指数'])
        st.info(f"""
        **スキル ↔ 品質の相関**  
        相関係数: {skill_quality_corr:.2f}
        
        {"✅ 強い正の相関" if skill_quality_corr > 0.7 else "⚠️ 相関が弱い"}
        """)
        
        # 改善余地の計算
        improvement_potential = (100 - kpi['総合スコア'].mean())
        st.warning(f"""
        **グローバル改善余地**  
        平均スコア: {kpi['総合スコア'].mean():.1f}  
        改善ポテンシャル: {improvement_potential:.1f} pt
        """)
    
    st.markdown("---")
    
    # 国別集計
    st.markdown("### 🌏 国別パフォーマンス")
    
    country_kpi = kpi.groupby('国').agg({
        '総合スコア': 'mean',
        '効率指数': 'mean',
        '品質指数': 'mean',
        '安全指数': 'mean',
        'スキル指数': 'mean',
        '拠点': 'count'
    }).round(1).reset_index()
    country_kpi.columns = ['国', '平均総合スコア', '平均効率', '平均品質', '平均安全', '平均スキル', '拠点数']
    country_kpi = country_kpi.sort_values('平均総合スコア', ascending=False)
    
    st.dataframe(
        country_kpi.style.background_gradient(
            subset=['平均総合スコア', '平均効率', '平均品質', '平均安全', '平均スキル'],
            cmap='RdYlGn',
            vmin=60,
            vmax=110
        ),
        use_container_width=True,
        hide_index=True
    )

def render_location_comparison(kpi):
    """拠点比較分析 - 選択式"""
    st.subheader("🔍 拠点比較分析（選択式）")
    
    st.markdown("""
    **使い方**: 比較したい拠点を選択して、4つの指標（効率・品質・安全・スキル）を多角的に比較できます。
    """)
    
    # 拠点選択UI
    st.markdown("### 📍 比較する拠点を選択")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # デフォルトで上位3拠点を選択
        default_selection = kpi.nlargest(3, '総合スコア')['拠点'].tolist()
        selected_locations = st.multiselect(
            "拠点を選択（複数選択可）",
            options=kpi['拠点'].tolist(),
            default=default_selection,
            help="最大10拠点まで選択できます"
        )
    
    with col2:
        # クイック選択ボタン
        st.markdown("**クイック選択:**")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🏆 上位5拠点"):
                selected_locations = kpi.nlargest(5, '総合スコア')['拠点'].tolist()
        
        with col_b:
            if st.button("⚠️ 下位5拠点"):
                selected_locations = kpi.nsmallest(5, '総合スコア')['拠点'].tolist()
        
        with col_c:
            if st.button("🎌 日本拠点のみ"):
                selected_locations = kpi[kpi['ベンチマーク拠点'] == True]['拠点'].tolist()
    
    # 選択された拠点のデータ
    if not selected_locations:
        st.warning("⚠️ 比較する拠点を選択してください")
        return
    
    if len(selected_locations) > 10:
        st.warning("⚠️ 拠点は最大10個まで選択できます")
        selected_locations = selected_locations[:10]
    
    selected_kpi = kpi[kpi['拠点'].isin(selected_locations)].copy()
    selected_kpi = selected_kpi.sort_values('総合スコア', ascending=False)
    
    st.markdown("---")
    
    # レーダーチャート
    st.markdown("### 📊 4軸レーダーチャート比較")
    
    fig = create_radar_chart(selected_kpi, f"{len(selected_locations)}拠点の比較")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 指数比較の棒グラフ（スキル指数を追加）
    st.markdown("### 📊 4指標の詳細比較")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='効率指数',
        x=selected_kpi['拠点'],
        y=selected_kpi['効率指数'],
        marker_color='#1f77b4',
        text=selected_kpi['効率指数'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='品質指数',
        x=selected_kpi['拠点'],
        y=selected_kpi['品質指数'],
        marker_color='#2ca02c',
        text=selected_kpi['品質指数'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='安全指数',
        x=selected_kpi['拠点'],
        y=selected_kpi['安全指数'],
        marker_color='#ff7f0e',
        text=selected_kpi['安全指数'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='スキル指数',
        x=selected_kpi['拠点'],
        y=selected_kpi['スキル指数'],
        marker_color='#9467bd',
        text=selected_kpi['スキル指数'].round(1),
        textposition='outside'
    ))
    
    # ベンチマーク基準線
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="ベンチマーク基準 (100)",
                  annotation_position="right")
    
    fig.update_layout(
        barmode='group',
        height=500,
        xaxis_title="拠点",
        yaxis_title="指数（日本拠点=100）",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, max(selected_kpi[['効率指数', '品質指数', '安全指数', 'スキル指数']].max()) * 1.15])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 詳細比較テーブル
    st.markdown("### 📋 選択拠点の詳細データ")
    
    comparison_df = selected_kpi[[
        '拠点', '国', 'ベンチマーク拠点',
        '総合スコア', '効率指数', '品質指数', '安全指数', 'スキル指数',
        '生産効率_指数', '品質不良率', '労災発生率', '総合スキルスコア'
    ]].copy()
    
    st.dataframe(
        comparison_df.style.background_gradient(
            subset=['総合スコア', '効率指数', '品質指数', '安全指数', 'スキル指数'],
            cmap='RdYlGn',
            vmin=60,
            vmax=110
        ).format({
            '総合スコア': '{:.1f}',
            '効率指数': '{:.1f}',
            '品質指数': '{:.1f}',
            '安全指数': '{:.1f}',
            'スキル指数': '{:.1f}',
            '生産効率_指数': '{:.1f}',
            '品質不良率': '{:.2f}%',
            '労災発生率': '{:.2f}%',
            '総合スキルスコア': '{:.2f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # ギャップ分析
    st.markdown("---")
    st.markdown("### 🎯 ギャップ分析（ベンチマーク拠点との差異）")
    
    # ベンチマーク拠点の平均値
    benchmark_avg = kpi[kpi['ベンチマーク拠点'] == True][
        ['効率指数', '品質指数', '安全指数', 'スキル指数']
    ].mean()
    
    # ギャップ計算
    gap_df = selected_kpi[['拠点', '効率指数', '品質指数', '安全指数', 'スキル指数']].copy()
    gap_df['効率ギャップ'] = gap_df['効率指数'] - benchmark_avg['効率指数']
    gap_df['品質ギャップ'] = gap_df['品質指数'] - benchmark_avg['品質指数']
    gap_df['安全ギャップ'] = gap_df['安全指数'] - benchmark_avg['安全指数']
    gap_df['スキルギャップ'] = gap_df['スキル指数'] - benchmark_avg['スキル指数']
    
    # ヒートマップ
    fig = go.Figure(data=go.Heatmap(
        z=gap_df[['効率ギャップ', '品質ギャップ', '安全ギャップ', 'スキルギャップ']].values.T,
        x=gap_df['拠点'],
        y=['効率', '品質', '安全', 'スキル'],
        colorscale='RdYlGn',
        zmid=0,
        text=gap_df[['効率ギャップ', '品質ギャップ', '安全ギャップ', 'スキルギャップ']].values.T.round(1),
        texttemplate='%{text}',
        textfont={"size": 12},
        colorbar=dict(title="ギャップ<br>(pt)")
    ))
    
    fig.update_layout(
        title="ベンチマーク拠点とのギャップ（正の値は優位、負の値は劣位）",
        height=350,
        xaxis_title="拠点",
        yaxis_title="指標"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # インサイト
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💡 主要インサイト")
        
        # 最も改善が必要な拠点
        total_gap = gap_df[['効率ギャップ', '品質ギャップ', '安全ギャップ', 'スキルギャップ']].sum(axis=1)
        worst_location = gap_df.loc[total_gap.idxmin(), '拠点']
        worst_gap = total_gap.min()
        
        st.warning(f"""
        **最優先改善拠点**  
        {worst_location}  
        総合ギャップ: {worst_gap:.1f} pt
        """)
    
    with col2:
        # 最もパフォーマンスが良い拠点（ベンチマーク除く）
        non_benchmark = gap_df[~gap_df['拠点'].isin(kpi[kpi['ベンチマーク拠点'] == True]['拠点'])]
        if len(non_benchmark) > 0:
            best_location = non_benchmark.loc[total_gap[non_benchmark.index].idxmax(), '拠点']
            best_gap = total_gap[non_benchmark.index].max()
            
            st.success(f"""
            **ベストプラクティス拠点**  
            （ベンチマーク除く）  
            {best_location}  
            総合ギャップ: {best_gap:.1f} pt
            """)

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
    
    styled_df = display_df.style.map(
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