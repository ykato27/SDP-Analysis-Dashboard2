# SDP Analysis Dashboard - ファイル構成

## 📁 ディレクトリ構造

```
SDP-Analysis-Dashboard-Clean/
│
├── app.py                          # メインアプリケーション
├── data_loader.py                  # データローダーモジュール
├── generate_dummy_data.py          # ダミーデータ生成スクリプト
├── requirements.txt                # 依存パッケージリスト
│
├── README.md                       # プロジェクト詳細ドキュメント
├── SETUP_GUIDE.md                  # セットアップガイド
├── PROJECT_OVERVIEW.md             # プロジェクト概要
│
├── data/                           # データディレクトリ
│   ├── employee_skill_data.csv     # 従業員スキルデータ (2,079件)
│   ├── daily_production_data.csv   # 日次生産データ (43,200件)
│   ├── training_history_data.csv   # 研修履歴データ (500件)
│   ├── process_bottleneck_data.csv # 工程ボトルネック (480件)
│   └── location_master_data.csv    # 拠点マスタ (10拠点)
│
└── views/                          # ビューモジュール
    ├── __init__.py
    ├── step1_global_overview.py    # STEP 1: 全社俯瞰
    ├── step2_location_analysis.py  # STEP 2: 拠点内比較
    ├── step3_skill_structure.py    # STEP 3: スキル構造比較
    ├── step4_correlation.py        # STEP 4: 相関分析
    ├── step5_bottleneck.py         # STEP 5: ボトルネック分析
    └── step6_10.py                 # STEP 6-10: 残りのステップ
```

## 📊 ファイル統計

- **Pythonコード**: 10ファイル
- **ドキュメント**: 3ファイル
- **データファイル**: 5 CSVファイル
- **総サイズ**: 約4.2MB (圧縮後: 793KB)

## 🗑️ 削除した不要ファイル

元のリポジトリから以下の不要ファイルを削除しました:

### 古いアプリケーションファイル
- ❌ `app.py` (旧バージョン)
- ❌ `data_loader.py` (旧バージョン)
- ❌ `generate_dummy_data.py` (旧バージョン)
- ❌ `requirements.txt` (旧バージョン)

### 使用していないビューファイル
- ❌ `views/welcome.py`
- ❌ `views/action_plan.py`
- ❌ `views/executive_summary.py`
- ❌ `views/monitoring.py`
- ❌ `views/raw_data.py`
- ❌ `views/root_cause_analysis.py`
- ❌ `views/integrated_quality_analysis.py`
- ❌ `views/quality_skill_analysis.py`

### 不要なディレクトリ
- ❌ `utils/` (カスタムスタイル等、未使用)
- ❌ `.git/` (Gitリポジトリ情報)

### 古いデータファイル
- ❌ `data/daily_production_dummy.csv` (旧ダミーデータ)

## ✅ クリーン版の特徴

1. **シンプルな構成**: 必要最小限のファイルのみ
2. **一貫した命名**: `_sdp` サフィックスを削除
3. **明確な責任分離**: 各ステップが独立したモジュール
4. **ドキュメント完備**: README, SETUP, OVERVIEW

## 🚀 次のステップ

このクリーン版は以下の用途に最適です:

- ✅ 新規プロジェクトとしての使用
- ✅ カスタマイズのベースライン
- ✅ チームへの配布
- ✅ 実データへの接続

---

**削減効果**:
- Pythonファイル: 23 → 10 (57%削減)
- 圧縮サイズ: 839KB → 793KB (5%削減)
