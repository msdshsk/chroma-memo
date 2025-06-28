# Chroma-Memo プロジェクト計画書

## プロジェクト概要

PythonとChromaDBを使用して、プロジェクト毎に独立したナレッジベースを作成・管理するCLIツールです。各プロジェクトが独自のベクトルデータベースを持ち、効率的な情報の保存・検索・管理を可能にします。

## 基本機能

### 1. 必須コマンド（提案された基本機能）

| コマンド | 説明 | 例 |
|---------|------|-----|
| `init {project_name}` | プロジェクト専用のDBを新規作成 | `chroma-memo init my-project` |
| `add {project_name} {message}` | ナレッジをDBに追加 | `chroma-memo add my-project "Pythonの基本構文について"` |
| `search {project_name} {query}` | クエリでDBを検索 | `chroma-memo search my-project "Python 構文"` |
| `del {project_name} {id}` | 指定IDのナレッジを削除 | `chroma-memo del my-project 12345` |

### 2. 推奨追加機能

| コマンド | 説明 | 例 |
|---------|------|-----|
| `list {project_name}` | プロジェクトの全ナレッジを一覧表示 | `chroma-memo list my-project` |
| `update {project_name} {id} {new_message}` | 既存ナレッジの更新 | `chroma-memo update my-project 12345 "更新された内容"` |
| `projects` | 全プロジェクトの一覧表示 | `chroma-memo projects` |
| `info {project_name}` | プロジェクトの統計・詳細情報 | `chroma-memo info my-project` |
| `export {project_name} [format]` | ナレッジのエクスポート | `chroma-memo export my-project json` |
| `import {project_name} {file}` | ナレッジのインポート | `chroma-memo import my-project data.json` |
| `backup [project_name]` | バックアップ作成 | `chroma-memo backup my-project` |
| `config` | 設定管理 | `chroma-memo config --set-api-key openai` |

## 技術仕様

### アーキテクチャ
```
chroma-memo/
├── chroma_memo/
│   ├── __init__.py
│   ├── cli.py              # CLIエントリーポイント
│   ├── database.py         # Chroma DB操作
│   ├── embeddings.py       # OpenAI embedding処理
│   ├── models.py           # データモデル
│   ├── config.py           # 設定管理
│   ├── utils.py            # ユーティリティ関数
│   └── commands/
│       ├── __init__.py
│       ├── init.py         # initコマンド
│       ├── add.py          # addコマンド
│       ├── search.py       # searchコマンド
│       ├── delete.py       # delコマンド
│       ├── list.py         # listコマンド
│       ├── update.py       # updateコマンド
│       ├── export.py       # exportコマンド
│       ├── import.py       # importコマンド
│       └── info.py         # infoコマンド
├── tests/
├── docs/
├── requirements.txt
├── setup.py
├── README.md
├── .env.example            # 環境変数テンプレート
└── .gitignore
```

### 主要依存関係
- `chromadb`: ベクトルデータベース
- `openai`: OpenAI API（text-embedding-3-small用）
- `click`: CLIフレームワーク
- `rich`: リッチなCLI出力
- `pydantic`: データバリデーション
- `python-dotenv`: 環境変数管理

## データベース設計

### Chromaコレクション構造
```python
# 各プロジェクトは独立したコレクションを持つ
collection_name = f"project_{project_name}"

# ドキュメント構造
{
    "id": "uuid4_string",
    "document": "ナレッジ内容",
    "metadata": {
        "project": "project_name",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "tags": ["tag1", "tag2"],
        "source": "manual|import|api"
    }
}
```

### 設定ファイル構造
```yaml
# ~/.chroma-memo/config.yaml
embedding:
  model: "text-embedding-3-small"
  provider: "openai"
  api_key_env: "OPENAI_API_KEY"  # 環境変数名
db_path: "~/.chroma-memo/db"
max_results: 10
similarity_threshold: 0.7
export_formats:
  - json
  - csv
  - markdown
```

### 環境変数設定
```bash
# ~/.chroma-memo/.env または システム環境変数
OPENAI_API_KEY=your_openai_api_key_here
```

### APIキー設定方法
1. **環境変数での設定（推奨）**:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

2. **設定コマンドでの設定**:
   ```bash
   chroma-memo config --set-api-key openai
   # APIキーを安全にプロンプトで入力
   ```

3. **.envファイルでの設定**:
   ```bash
   # ~/.chroma-memo/.env
   OPENAI_API_KEY=your_api_key_here
   ```

## 実装フェーズ

### Phase 1: コア機能（MVP）
- [x] プロジェクト構造設定
- [ ] `init`コマンド実装
- [ ] `add`コマンド実装
- [ ] `search`コマンド実装
- [ ] `del`コマンド実装
- [ ] 基本的なCLIインターフェース

### Phase 2: 拡張機能
- [ ] `list`コマンド実装
- [ ] `projects`コマンド実装
- [ ] `info`コマンド実装
- [ ] リッチなCLI出力（Rich）
- [ ] 設定管理システム

### Phase 3: 高度な機能
- [ ] `update`コマンド実装
- [ ] `export`/`import`機能
- [ ] `backup`機能
- [ ] タグ機能
- [ ] 全文検索機能

### Phase 4: 最適化・UX改善
- [ ] パフォーマンス最適化
- [ ] エラーハンドリング強化
- [ ] ドキュメント整備
- [ ] テストカバレッジ向上

## 使用例

```bash
# プロジェクト初期化
chroma-memo init "machine-learning-notes"

# ナレッジ追加
chroma-memo add machine-learning-notes "線形回帰は教師あり学習の手法で、連続値を予測する"
chroma-memo add machine-learning-notes "ランダムフォレストは決定木の集合学習手法"

# 検索
chroma-memo search machine-learning-notes "回帰"
# 結果:
# ID: abc123 (類似度: 0.85)
# 線形回帰は教師あり学習の手法で、連続値を予測する

# プロジェクト一覧
chroma-memo projects
# 結果:
# - machine-learning-notes (3 items)
# - web-development-tips (5 items)

# エクスポート
chroma-memo export machine-learning-notes json > ml_notes.json
```

## 特徴・利点
1. **プロジェクト隔離**: 各プロジェクトが独立したDBを持つ
2. **高速検索**: ベクトル検索による意味的類似性検索
3. **高品質embedding**: OpenAI text-embedding-3-smallによる高精度な意味理解
4. **柔軟性**: インポート/エクスポート機能で他ツールとの連携
5. **拡張性**: プラグイン機能で機能拡張可能
6. **使いやすさ**: 直感的なCLIインターフェース
7. **セキュア**: APIキー管理の安全な仕組み

## セキュリティ考慮事項
- **APIキー保護**: 
  - 環境変数での管理を推奨
  - `.env`ファイルは`.gitignore`に追加
  - 設定ファイルには平文でAPIキーを保存しない
- **データプライバシー**: 
  - ナレッジデータがOpenAI APIに送信されることの明示
  - 機密情報の取り扱い注意喚起
- **レート制限**: 
  - OpenAI APIのレート制限への対応
  - バッチ処理時の適切な間隔制御

## 今後の拡張可能性
- Web UI の提供
- API サーバー機能
- 他のベクトルDBサポート（Pinecone、Weaviate等）
- 外部ドキュメント連携（PDF、Markdown等の自動取り込み）
- チーム共有機能
- AI チャットボット統合 