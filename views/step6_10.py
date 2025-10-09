"""
STEP 6-10: 簡略版実装（プレースホルダー）
実際のプロジェクトではこれらを完全実装します
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def render_step6(df_employee, selected_location, selected_line):
    """STEP 6: 個人・チーム力量の詳細分析"""
    st.title(f"👥 STEP 6: 個人・チーム力量分析 - {selected_location} / {selected_line}")
    st.markdown("**目的**: 対象工程のメンバー力量を把握し、育成ターゲットを特定")
    
    # 基本フィルタリング
    df_loc = df_employee[(df_employee['拠点'] == selected_location) & 
                         (df_employee['ライン'] == selected_line)].copy()
    
    if len(df_loc) == 0:
        st.warning("⚠️ 該当する従業員がいません。")
        return
    
    # メイン画面にフィルタセクションを配置
    st.markdown("---")
    st.subheader("🔍 組織・条件フィルタ")
    
    # フィルタを2列で配置
    col1, col2 = st.columns(2)
    
    with col1:
        # シフトフィルタ
        st.markdown("**🔄 シフト選択**")
        available_shifts = sorted(df_loc['シフト'].unique().tolist())
        
        # プリセットボタン（横並び）
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("全選択", key="all_shifts", use_container_width=True):
                st.session_state.shift_preset = "all"
        with btn_col2:
            if st.button("昼勤", key="day_shifts", use_container_width=True):
                st.session_state.shift_preset = "day"
        with btn_col3:
            if st.button("夜勤", key="night_shifts", use_container_width=True):
                st.session_state.shift_preset = "night"
        
        # プリセットに基づいてデフォルト値を設定
        if 'shift_preset' not in st.session_state:
            st.session_state.shift_preset = "all"
        
        if st.session_state.shift_preset == "all":
            default_shifts = available_shifts
        elif st.session_state.shift_preset == "day":
            default_shifts = [s for s in available_shifts if s in ['A班', 'B班']]
        elif st.session_state.shift_preset == "night":
            default_shifts = [s for s in available_shifts if s in ['C班', 'D班']]
        else:
            default_shifts = available_shifts
        
        selected_shifts = st.multiselect(
            "対象シフト",
            available_shifts,
            default=default_shifts,
            key="step6_shift_filter",
            help="分析対象のシフトを選択（複数選択可）"
        )
        
        st.caption(f"✓ 選択中: {len(selected_shifts)}/{len(available_shifts)} シフト")
    
    with col2:
        # 経験年数とスキルスコアのフィルタ
        st.markdown("**📊 条件フィルタ**")
        
        min_exp, max_exp = int(df_loc['経験年数'].min()), int(df_loc['経験年数'].max())
        exp_range = st.slider(
            "📅 経験年数範囲",
            min_value=min_exp,
            max_value=max_exp,
            value=(min_exp, max_exp),
            key="step6_exp_filter",
            help="分析対象の経験年数範囲を指定"
        )
        
        min_skill, max_skill = float(df_loc['総合スキルスコア'].min()), float(df_loc['総合スキルスコア'].max())
        skill_range = st.slider(
            "⭐ 総合スキルスコア範囲",
            min_value=min_skill,
            max_value=max_skill,
            value=(min_skill, max_skill),
            step=0.1,
            key="step6_skill_filter",
            help="分析対象のスキルスコア範囲を指定"
        )
    
    # シフトでフィルタリング
    if selected_shifts:
        df_filtered = df_loc[df_loc['シフト'].isin(selected_shifts)].copy()
    else:
        st.warning("⚠️ シフトを選択してください")
        df_filtered = df_loc.copy()
    
    # 経験年数でフィルタリング
    df_filtered = df_filtered[
        (df_filtered['経験年数'] >= exp_range[0]) & 
        (df_filtered['経験年数'] <= exp_range[1])
    ].copy()
    
    # スキルスコアでフィルタリング
    df_filtered = df_filtered[
        (df_filtered['総合スキルスコア'] >= skill_range[0]) & 
        (df_filtered['総合スキルスコア'] <= skill_range[1])
    ].copy()
    
    # フィルタ結果の表示
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"📊 フィルタ結果: **{len(df_filtered)}名** / 全体 {len(df_loc)}名")
    with col2:
        if st.button("🔄 全リセット", key="reset_filters", help="全てのフィルタをリセット"):
            st.rerun()
    
    # 適用中のフィルタ情報を表示
    if len(selected_shifts) < len(available_shifts) or \
       exp_range != (int(df_loc['経験年数'].min()), int(df_loc['経験年数'].max())) or \
       skill_range != (float(df_loc['総合スキルスコア'].min()), float(df_loc['総合スキルスコア'].max())):
        with st.expander("🔍 適用中のフィルタ条件", expanded=False):
            st.write(f"**シフト**: {', '.join(selected_shifts) if selected_shifts else '全て'}")
            st.write(f"**経験年数**: {exp_range[0]}年 〜 {exp_range[1]}年")
            st.write(f"**スキルスコア**: {skill_range[0]:.1f} 〜 {skill_range[1]:.1f}")
    
    if len(df_filtered) == 0:
        st.warning("⚠️ フィルタ条件に該当する従業員がいません。条件を調整してください。")
        return
    
    # 個人選択（複数選択可能）
    st.markdown("---")
    st.subheader("🎯 個人選択（複数選択可）")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"📊 **フィルタリング対象者数**: {len(df_filtered)}名")
    with col2:
        select_all = st.button("✅ 全員選択", key="select_all_employees", use_container_width=True)
    with col3:
        clear_all = st.button("❌ 全員解除", key="clear_all_employees", use_container_width=True)
    
    # 従業員リストを作成（ID + スキルスコアで表示）
    df_filtered_sorted = df_filtered.sort_values('総合スキルスコア', ascending=False)
    employee_options = [
        f"{row['従業員ID']} (スコア: {row['総合スキルスコア']:.2f}, 経験: {row['経験年数']}年, シフト: {row['シフト']})"
        for _, row in df_filtered_sorted.iterrows()
    ]
    employee_ids = df_filtered_sorted['従業員ID'].tolist()
    
    # デフォルト選択の決定
    if select_all:
        default_selection = employee_options  # 全員選択
    elif clear_all:
        default_selection = []  # 全員解除
    else:
        # 通常時：上位5名を選択（または全員が5名未満の場合は全員）
        default_count = min(5, len(employee_ids))
        default_selection = employee_options[:default_count]
    
    selected_employees_display = st.multiselect(
        "👥 レーダーチャートに表示する従業員を選択",
        options=employee_options,
        default=default_selection,
        help="複数選択可能です。比較したい従業員を選んでください。",
        key="employee_multiselect"
    )
    
    # 選択された従業員IDを取得
    if selected_employees_display:
        selected_indices = [employee_options.index(emp) for emp in selected_employees_display]
        selected_employee_ids = [employee_ids[i] for i in selected_indices]
        df_selected = df_filtered[df_filtered['従業員ID'].isin(selected_employee_ids)].copy()
    else:
        st.warning("⚠️ 少なくとも1名の従業員を選択してください。")
        df_selected = pd.DataFrame()
    
    # スキルマップ（選択された個人のみ）
    if len(df_selected) > 0:
        st.subheader("📊 選択メンバーのスキルプロファイル")
        
        skill_cols = ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理']
        
        fig = go.Figure()
        
        for _, member in df_selected.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[member[col] for col in skill_cols],
                theta=skill_cols,
                fill='toself',
                name=f"{member['従業員ID']} ({member['総合スキルスコア']:.1f})"
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            title=f"選択メンバー({len(df_selected)}名)のスキルプロファイル比較",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 選択メンバーの詳細統計
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("選択人数", f"{len(df_selected)}名")
        with col2:
            st.metric("平均スキルスコア", f"{df_selected['総合スキルスコア'].mean():.2f}")
        with col3:
            st.metric("平均経験年数", f"{df_selected['経験年数'].mean():.1f}年")
    
    # 詳細テーブル（フィルタリング結果のみ表示）
    st.subheader("📋 フィルタリング結果詳細データ")
    
    display_cols = ['従業員ID', 'シフト', '経験年数'] + ['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理'] + ['総合スキルスコア']
    
    # フィルタ結果全体を表示（選択した個人だけでなく）
    df_display = df_filtered[display_cols].sort_values('総合スキルスコア', ascending=False)
    
    try:
        # matplotlibが利用可能な場合
        st.dataframe(
            df_display.style.background_gradient(
                subset=['操炉技術', '成分制御', '異常対応', '設備保全', '品質検査', '安全管理', '総合スキルスコア'],
                cmap='RdYlGn',
                vmin=1,
                vmax=5
            ).format({
                '操炉技術': '{:.1f}',
                '成分制御': '{:.1f}',
                '異常対応': '{:.1f}',
                '設備保全': '{:.1f}',
                '品質検査': '{:.1f}',
                '安全管理': '{:.1f}',
                '総合スキルスコア': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )
    except ImportError:
        # matplotlibが利用できない場合のフォールバック
        st.dataframe(
            df_display.style.format({
                '操炉技術': '{:.1f}',
                '成分制御': '{:.1f}',
                '異常対応': '{:.1f}',
                '設備保全': '{:.1f}',
                '品質検査': '{:.1f}',
                '安全管理': '{:.1f}',
                '総合スキルスコア': '{:.2f}'
            }),
            use_container_width=True,
            height=400
        )
    
    # CSVダウンロード機能
    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 フィルタリング結果をCSVダウンロード",
        data=csv,
        file_name=f"step6_filtered_data_{selected_location}_{selected_line}.csv",
        mime="text/csv"
    )
    
    st.info("💡 **次のステップ**: 育成対象者を特定し「STEP 7: 教育効果分析」で最適な研修プログラムを選定")

def render_step7(df_training, df_employee):
    """STEP 7: 教育・訓練データとの連携"""
    st.title("📚 STEP 7: 教育・訓練効果分析")
    st.markdown("**目的**: 力量改善の取り組み状況を可視化し、教育投資効果を検証")
    
    # 研修プログラム別受講状況
    st.subheader("研修プログラム別受講状況")
    
    program_stats = df_training.groupby('研修プログラム').agg({
        '従業員ID': 'count',
        '受講時間': 'sum',
        '理解度テスト': 'mean',
        '実技評価': 'mean',
        'コスト_円': 'sum'
    }).reset_index()
    
    program_stats.columns = ['研修プログラム', '受講者数', '総受講時間', '平均理解度', '平均実技評価', '総コスト']
    
    fig = go.Figure(data=[
        go.Bar(
            x=program_stats['研修プログラム'],
            y=program_stats['受講者数'],
            text=program_stats['受講者数'],
            textposition='auto',
            marker_color='#1f77b4'
        )
    ])
    
    fig.update_layout(
        title="研修プログラム別受講者数",
        xaxis_title="研修プログラム",
        yaxis_title="受講者数",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 詳細テーブル
    st.dataframe(
        program_stats.style.format({
            '受講者数': '{:,.0f}',
            '総受講時間': '{:,.0f}',
            '平均理解度': '{:.1f}',
            '平均実技評価': '{:.1f}',
            '総コスト': '¥{:,.0f}'
        }),
        use_container_width=True
    )
    
    # ROI計算（簡易版）
    st.subheader("教育投資ROI（簡易試算）")
    
    total_cost = program_stats['総コスト'].sum()
    st.metric("総教育コスト", f"¥{total_cost:,.0f}")
    
    st.info("💡 **次のステップ**: 「STEP 8: 改善効果モニタリング」で実際の生産性向上を測定")

def render_step8(df_production, selected_location):
    """STEP 8: 改善施策の実行・効果モニタリング"""
    st.title(f"📊 STEP 8: 改善効果モニタリング - {selected_location}")
    st.markdown("**目的**: スキル向上による生産効率・品質改善効果を検証")
    
    df_loc = df_production[df_production['拠点'] == selected_location].copy()
    
    # 時系列での改善トレンド
    df_loc['年月'] = pd.to_datetime(df_loc['日付']).dt.to_period('M')
    
    monthly = df_loc.groupby('年月').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
    }).reset_index()
    
    monthly['年月'] = monthly['年月'].astype(str)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(monthly, x='年月', y='生産効率_指数', title="生産効率トレンド", markers=True)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(monthly, x='年月', y='品質不良率', title="品質不良率トレンド", markers=True)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Before/After比較（最初の3ヶ月 vs 最後の3ヶ月）
    st.subheader("Before/After 比較")
    
    before = monthly.head(3)[['生産効率_指数', '品質不良率']].mean()
    after = monthly.tail(3)[['生産効率_指数', '品質不良率']].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "生産効率", 
            f"{after['生産効率_指数']:.1f}",
            f"{after['生産効率_指数'] - before['生産効率_指数']:+.1f}"
        )
    
    with col2:
        st.metric(
            "品質不良率",
            f"{after['品質不良率']:.2f}%",
            f"{after['品質不良率'] - before['品質不良率']:+.2f}%",
            delta_color="inverse"
        )
    
    st.info("💡 **次のステップ**: 「STEP 9: ベンチマーキング」で他拠点との比較を実施")

def render_step9(df_production, df_employee):
    """STEP 9: 他拠点とのベンチマーキング"""
    st.title("🏆 STEP 9: 拠点間ベンチマーキング")
    st.markdown("**目的**: 優良拠点・高スキルチームの成功パターンを抽出")
    
    # 拠点別パフォーマンス
    location_perf = df_production.groupby('拠点').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
    }).reset_index()
    
    location_skill = df_employee.groupby('拠点')['総合スキルスコア'].mean().reset_index()
    
    benchmark = location_perf.merge(location_skill, on='拠点')
    
    # 散布図: スキル vs 生産効率
    fig = px.scatter(
        benchmark,
        x='総合スキルスコア',
        y='生産効率_指数',
        size='品質不良率',
        text='拠点',
        title="拠点別ベンチマーク分析",
        labels={'総合スキルスコア': '平均スキルスコア', '生産効率_指数': '生産効率指数'}
    )
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ベストプラクティス拠点
    st.subheader("🏆 ベストプラクティス拠点")
    
    best = benchmark.nlargest(3, '生産効率_指数')
    
    st.dataframe(
        best.style.format({
            '生産効率_指数': '{:.1f}',
            '品質不良率': '{:.2f}%',
            '総合スキルスコア': '{:.2f}'
        }),
        use_container_width=True
    )
    
    st.info("💡 **次のステップ**: 「STEP 10: 経営KPIダッシュボード」で全社視点の管理指標を確認")

def render_step10(df_employee, df_production, df_location):
    """STEP 10: 全社KPIダッシュボード"""
    st.title("📊 STEP 10: 全社KPIダッシュボード")
    st.markdown("**目的**: 人的スキルをKPI化し、経営レベルで管理する")
    
    # KPIメトリクス
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_skill = df_employee['総合スキルスコア'].mean()
        st.metric("平均Skill Index", f"{avg_skill:.2f}")
    
    with col2:
        avg_efficiency = df_production['生産効率_指数'].mean()
        st.metric("平均生産効率", f"{avg_efficiency:.1f}")
    
    with col3:
        avg_defect = df_production['品質不良率'].mean()
        st.metric("平均品質不良率", f"{avg_defect:.2f}%")
    
    with col4:
        total_accidents = df_production['労災発生'].sum()
        st.metric("労災発生件数", f"{total_accidents}")
    
    # 拠点別KPIヒートマップ
    st.subheader("拠点別KPIヒートマップ")
    
    location_kpi = df_production.groupby('拠点').agg({
        '生産効率_指数': 'mean',
        '品質不良率': 'mean',
        '稼働率': 'mean',
    }).reset_index()
    
    location_skill = df_employee.groupby('拠点')['総合スキルスコア'].mean().reset_index()
    kpi = location_kpi.merge(location_skill, on='拠点')
    
    # 正規化（0-100）
    for col in ['生産効率_指数', '稼働率', '総合スキルスコア']:
        kpi[col] = (kpi[col] / kpi[col].max() * 100)
    
    kpi['品質スコア'] = 100 - (kpi['品質不良率'] / kpi['品質不良率'].max() * 100)
    
    heatmap_data = kpi[['生産効率_指数', '品質スコア', '稼働率', '総合スキルスコア']].values
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.T,
        x=kpi['拠点'],
        y=['生産効率', '品質', '稼働率', 'スキル'],
        colorscale='RdYlGn',
        text=np.round(heatmap_data.T, 1),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="スコア")
    ))
    
    fig.update_layout(
        title="全社KPIヒートマップ",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("✅ SDP分析完了！継続的にモニタリングし、PDCAサイクルを回しましょう")