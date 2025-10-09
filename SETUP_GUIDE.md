# SDP Analysis Dashboard - セットアップガイド

## 📦 クイックスタート

### 1. プロジェクトのダウンロードと展開

```bash
# 圧縮ファイルを展開
tar -xzf SDP-Analysis-Dashboard.tar.gz
cd SDP-Analysis-Dashboard
```

### 2. Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

または個別にインストール:

```bash
pip install streamlit pandas numpy plotly scipy
```

### 3. ダミーデータの生成

```bash
python generate_dummy_data.py
```

以下のファイルが `data/` ディレクトリに生成されます:
- `employee_skill_data.csv` (従業員スキルデータ: 約2,000件)
- `daily_production_data.csv` (日次生産データ: 約43,000件)
- `training_history_data.csv` (研修履歴データ: 500件)
- `process_bottleneck_data.csv` (工程ボトルネックデータ: 480件)
- `location_master_data.csv` (拠点マスタ: 10件)

### 4. アプリケーションの起動

```bash
streamlit run app.py
```

### 5. ブラウザでアクセス

アプリケーションが起動したら、ブラウザで以下にアクセス:

```
http://localhost:8501
```

## 🎯 使い方

### 基本的な操作フロー

1. **サイドバーでステップを選択**
   - STEP 1〜10 の分析ステップから選択

2. **フィルタ条件の設定**
   - 拠点、ライン、シフトなどを選択

3. **グラフやデータを確認**
   - インタラクティブなグラフで分析
   - CSVダウンロードも可能

### 推奨分析フロー

```
STEP 1: 全社俯瞰
   ↓ 問題拠点を特定
STEP 2: 拠点内比較
   ↓ ライン・シフトの差異を分析
STEP 3: スキル構造比較
   ↓ スキル分布の偏りを確認
STEP 4: 相関分析
   ↓ スキルと生産性の関係を定量化
STEP 5: ボトルネック分析
   ↓ 優先改善項目を特定
STEP 6: 個人・チーム分析
   ↓ 育成対象者を選定
STEP 7: 教育効果分析
   ↓ 最適な研修プログラムを選択
STEP 8: 改善効果モニタリング
   ↓ Before/Afterを測定
STEP 9: ベンチマーキング
   ↓ 他拠点の成功パターンを学習
STEP 10: 経営KPI
   ↓ 全社視点で継続管理
```

## 🔧 カスタマイズ

### 1. 拠点データの変更

`generate_dummy_data.py` の `LOCATIONS` 辞書を編集:

```python
LOCATIONS = {
    '新拠点名': {
        'country': '国名',
        'lat': 緯度,
        'lon': 経度,
        'benchmark': False,
        'efficiency_base': 85,  # ベース効率指数
        'quality_base': 2.5,     # ベース品質不良率
        'safety_base': 1.5       # ベース労災率
    }
}
```

### 2. スキルカテゴリーの追加

`generate_dummy_data.py` の `SKILL_CATEGORIES` を編集:

```python
SKILL_CATEGORIES = {
    '新スキル名': {
        'weight': 0.10,              # 総合スコアへの重み
        'impact_efficiency': 0.20,    # 生産効率への影響度
        'impact_quality': 0.15,       # 品質への影響度
        'impact_safety': 0.10         # 安全への影響度
    }
}
```

### 3. 工程の追加

`generate_dummy_data.py` の `PROCESSES` リストを編集:

```python
PROCESSES = ['工程1', '工程2', '新工程', ...]
```

## 🐛 トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'xxx'`

```bash
pip install --upgrade -r requirements.txt
```

### エラー: `FileNotFoundError: data/employee_skill_data.csv`

データファイルが生成されていません:

```bash
python generate_dummy_data.py
```

### ポート8501が使用中

別のポートで起動:

```bash
streamlit run app.py --server.port 8502
```

### データが表示されない

ブラウザのキャッシュをクリア、またはStreamlitのキャッシュをクリア:

```bash
streamlit cache clear
```

## 📊 実データへの切り替え

### CSVファイルを実データに置き換え

1. `data/` ディレクトリに実際のCSVファイルを配置
2. ファイル名は以下の通り:
   - `employee_skill_data.csv`
   - `daily_production_data.csv`
   - `training_history_data.csv`
   - `process_bottleneck_data.csv`
   - `location_master_data.csv`

3. 列名とデータ型が README_SDP.md の仕様と一致していることを確認

### データベース接続への変更

`data_loader_sdp.py` の `load_all_data()` 関数を編集:

```python
import sqlalchemy

@st.cache_data
def load_all_data():
    engine = sqlalchemy.create_engine('your_connection_string')
    
    df_employee = pd.read_sql_query("SELECT * FROM employee_skill", engine)
    df_production = pd.read_sql_query("SELECT * FROM daily_production", engine)
    # ...
    
    return df_employee, df_production, df_training, df_bottleneck, df_location
```

## 🚀 本番環境へのデプロイ

### Streamlit Cloud

1. GitHubリポジトリにプッシュ
2. https://share.streamlit.io/ でアプリをデプロイ
3. `requirements.txt` が自動認識されます

### Docker

Dockerfileを作成:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

ビルドと起動:

```bash
docker build -t sdp-dashboard .
docker run -p 8501:8501 sdp-dashboard
```

## 📞 サポート

問題が発生した場合:

1. README_SDP.md の詳細ドキュメントを確認
2. エラーメッセージをコピーして検索
3. 開発チームに問い合わせ

---

**Happy Analyzing! 🎉**
