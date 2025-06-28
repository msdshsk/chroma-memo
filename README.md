# Chroma-Memo

プロジェクト毎に独立したナレッジベースを作成・管理するCLIツールです。ChromaDBとOpenAIの埋め込み技術を使用して、効率的な情報の保存・検索・管理を可能にします。

## 特徴

- 🗂️ **プロジェクト隔離**: 各プロジェクトが独立したベクトルデータベースを持つ
- 🔍 **高速検索**: OpenAI text-embedding-3-smallによる意味的類似性検索
- 📝 **リッチなCLI**: 美しく直感的なコマンドラインインターフェース
- 🏷️ **タグ機能**: ナレッジの分類・整理が可能
- 📊 **プロジェクト管理**: 複数プロジェクトの統合管理
- 🤖 **Claude Code/Cursor連携**: MCPサーバーとして動作可能

## クイックスタート

### インストール

```bash
git clone <repository-url>
cd chroma-memo
./install.sh
```

詳細なインストール方法は [INSTALL.md](INSTALL.md) をご覧ください。

### 基本的な使い方

```bash
# プロジェクトの初期化
chroma-memo init my-project

# ナレッジの追加
chroma-memo add my-project "Pythonの基本構文についてのメモ"

# タグ付きで追加
chroma-memo add my-project "FastAPIのルーティング設定" --tags python --tags web

# ナレッジの検索
chroma-memo search my-project "Python 構文"

# ナレッジの一覧表示
chroma-memo list my-project

# プロジェクト一覧
chroma-memo projects
```

### MCP サーバーとして使用

Claude CodeやCursorからChroma-Memoを使用できます：

```bash
# MCPサーバーを起動
chroma-memo serve my-project
```

詳細なMCP設定方法は [MCP_GUIDE.md](MCP_GUIDE.md) をご覧ください。

## コマンド一覧

| コマンド | 説明 | 例 |
|---------|------|-----|
| `init <project>` | プロジェクトを初期化 | `chroma-memo init my-project` |
| `add <project> <message>` | ナレッジを追加 | `chroma-memo add my-project "メモ"` |
| `search <project> <query>` | ナレッジを検索 | `chroma-memo search my-project "検索語"` |
| `list <project>` | ナレッジの一覧表示 | `chroma-memo list my-project` |
| `del <project> <id>` | ナレッジを削除 | `chroma-memo del my-project abc123` |
| `projects` | プロジェクト一覧 | `chroma-memo projects` |
| `info <project>` | プロジェクト情報 | `chroma-memo info my-project` |
| `config` | 設定管理 | `chroma-memo config` |
| `serve [project]` | MCPサーバー起動 | `chroma-memo serve my-project` |

## 使用例

### 機械学習プロジェクトの例

```bash
# プロジェクト初期化
chroma-memo init machine-learning-notes

# ナレッジの追加
chroma-memo add machine-learning-notes "線形回帰は教師あり学習の手法で、連続値を予測する" --tags regression --tags supervised

chroma-memo add machine-learning-notes "ランダムフォレストは決定木の集合学習手法" --tags ensemble --tags tree

# 検索
chroma-memo search machine-learning-notes "回帰"
```

### Claude Code連携の例

```bash
# Claude Code用コマンドテンプレート付きで初期化
chroma-memo init my-project --with-claude-command

# MCPサーバーとして起動
chroma-memo serve my-project
```

## 技術詳細

- **ベクトルデータベース**: ChromaDB (永続化対応)
- **埋め込みモデル**: OpenAI text-embedding-3-small (1536次元)
- **CLIフレームワーク**: Click
- **UIライブラリ**: Rich
- **データ検証**: Pydantic
- **設定管理**: YAML + 環境変数

## ライセンス

MIT License

## 貢献

Issue や Pull Request をお待ちしています！