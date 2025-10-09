"""
SDP (Skill Driven Production) Dashboard
高炉メーカー向けスキル分析ダッシュボード
10ステップドリルダウン分析
"""

import streamlit as st
from pathlib import Path

# ページ設定
st.set_page_config(
    page_title="SDP Analysis Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データローダーのインポート
from data_loader_sdp import (
    load_all_data,
    get_skill_categories,
    get_benchmark_locations
)

# ビューのインポート
from views import step1_global_overview
from views import step2_location_analysis
from views import step3_skill_structure
from views import step4_correlation
from views import step5_bottleneck
from views import step6_10

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6 0%, #e8eaf0 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .step-box {
        padding: 1rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # データロード
    df_employee, df_production, df_training, df_bottleneck, df_location = load_all_data()
    
    # サイドバー
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=SDP+Dashboard", use_container_width=True)
        
        st.markdown("## 🏭 SDP Analysis")
        st.markdown("**Skill Driven Production**")
        st.markdown("---")
        
        # ステップ選択
        step = st.radio(
            "分析ステップを選択",
            [
                "🌍 STEP 1: 全社俯瞰",
                "🏭 STEP 2: 拠点内比較",
                "🎯 STEP 3: スキル構造",
                "📊 STEP 4: 相関分析",
                "🔍 STEP 5: ボトルネック",
                "👥 STEP 6: 個人・チーム",
                "📚 STEP 7: 教育効果",
                "📊 STEP 8: 改善効果",
                "🏆 STEP 9: ベンチマーク",
                "📊 STEP 10: 経営KPI"
            ]
        )
        
        st.markdown("---")
        
        # フィルタ条件
        if step != "🌍 STEP 1: 全社俯瞰" and step != "📊 STEP 10: 経営KPI":
            st.markdown("### フィルタ条件")
            selected_location = st.selectbox(
                "拠点を選択",
                df_location['拠点'].tolist()
            )
        else:
            selected_location = None
        
        if step in ["👥 STEP 6: 個人・チーム"]:
            if selected_location:
                lines = df_employee[df_employee['拠点'] == selected_location]['ライン'].unique()
                selected_line = st.selectbox("ラインを選択", lines)
            else:
                selected_line = None
        else:
            selected_line = None
        
        st.markdown("---")
        
        # データ情報
        st.markdown("### 📊 データ概要")
        st.info(f"""
        **従業員数**: {len(df_employee):,}  
        **拠点数**: {len(df_location)}  
        **データ期間**: {df_production['日付'].min().strftime('%Y/%m/%d')} ～ {df_production['日付'].max().strftime('%Y/%m/%d')}
        """)
    
    # メインエリア
    st.markdown('<div class="main-header">🏭 SDP Analysis Dashboard</div>', unsafe_allow_html=True)
    
    # ステップに応じた表示
    if step == "🌍 STEP 1: 全社俯瞰":
        step1_global_overview.render(df_employee, df_production, df_location)
    
    elif step == "🏭 STEP 2: 拠点内比較":
        if selected_location:
            step2_location_analysis.render(df_employee, df_production, selected_location)
        else:
            st.warning("⚠️ 拠点を選択してください")
    
    elif step == "🎯 STEP 3: スキル構造":
        if selected_location:
            step3_skill_structure.render(df_employee, selected_location)
        else:
            st.warning("⚠️ 拠点を選択してください")
    
    elif step == "📊 STEP 4: 相関分析":
        if selected_location:
            step4_correlation.render(df_employee, df_production, selected_location)
        else:
            st.warning("⚠️ 拠点を選択してください")
    
    elif step == "🔍 STEP 5: ボトルネック":
        if selected_location:
            step5_bottleneck.render(df_bottleneck, selected_location)
        else:
            st.warning("⚠️ 拠点を選択してください")
    
    elif step == "👥 STEP 6: 個人・チーム":
        if selected_location and selected_line:
            step6_10.render_step6(df_employee, selected_location, selected_line)
        else:
            st.warning("⚠️ 拠点とラインを選択してください")
    
    elif step == "📚 STEP 7: 教育効果":
        step6_10.render_step7(df_training, df_employee)
    
    elif step == "📊 STEP 8: 改善効果":
        if selected_location:
            step6_10.render_step8(df_production, selected_location)
        else:
            st.warning("⚠️ 拠点を選択してください")
    
    elif step == "🏆 STEP 9: ベンチマーク":
        step6_10.render_step9(df_production, df_employee)
    
    elif step == "📊 STEP 10: 経営KPI":
        step6_10.render_step10(df_employee, df_production, df_location)
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>SDP (Skill Driven Production) Dashboard</strong></p>
        <p>Skill × Production × Quality × Safety Analytics</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
