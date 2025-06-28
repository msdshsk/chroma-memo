# Chroma-Memo

プロジェクト毎に独立したナレッジベースを作成・管理するCLIツールです。ChromaDBとOpenAIの埋め込み技術を使用して、効率的な情報の保存・検索・管理を可能にします。

## 特徴

- 🗂️ **プロジェクト隔離**: 各プロジェクトが独立したベクトルデータベースを持つ
- 🔍 **高速検索**: OpenAI text-embedding-3-smallによる意味的類似性検索
- 📝 **リッチなCLI**: 美しく直感的なコマンドラインインターフェース
- 🏷️ **タグ機能**: ナレッジの分類・整理が可能
- 📊 **プロジェクト管理**: 複数プロジェクトの統合管理
- 🤖 **Claude Code連携**: `--with-claude-command`でClaude Code用コマンドテンプレートを自動生成

## クイックスタート

### 🎯 対話型インストーラー使用（推奨）

最も簡単な方法は、対話型インストールスクリプトを使用することです：

```bash
git clone <repository-url>
cd chroma-memo
./install.sh
```

対話型インストーラーが以下を自動的に処理します：
- 🔍 Python環境の確認
- 📦 インストール方法の選択（ユーザー/システム/仮想環境）
- 🔑 OpenAI APIキーの設定
- 📥 実行可能ファイルのビルド（オプション）
- ✅ インストールの確認とパスの設定

インストール後、どこからでも使用可能：
```bash
cd ~/my-project
chroma-memo init my-project
chroma-memo add my-project "初めてのナレッジ"
```

### 🚀 ローカル実行（すぐに試したい場合）

インストールせずにすぐ使いたい場合は、自動セットアップスクリプトを使用：

```bash
git clone <repository-url>
cd chroma-memo
# Linux/Mac
./run.sh init my-project

# Windows
run.bat init my-project
```

## 詳細インストール（手動）

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd chroma-memo
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. パッケージのインストール

```bash
pip install -e .
```

### 4. OpenAI APIキーの設定

以下の3つの方法でAPIキーを設定できます：

#### 方法1: 設定コマンド（推奨）

```bash
chroma-memo config --set-api-key openai
# プロンプトでAPIキーを入力（非表示入力）
```

#### 方法2: .envファイル

`~/.chroma-memo/.env` ファイルを作成：

```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

#### 方法3: 環境変数

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

または `.bashrc` や `.zshrc` に追加：

```bash
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 基本的な使い方

### プロジェクトの初期化

```bash
# 基本的な初期化
chroma-memo init my-project

# Claude Code連携付きで初期化（推奨）
chroma-memo init my-project --with-claude-command
```

`--with-claude-command`オプションを使用すると、プロジェクトディレクトリに`.claude/commands/`フォルダが作成され、以下のClaude Code用コマンドテンプレートが自動生成されます：
- 📝 `memo-add.md`: ナレッジの追加
- 🔍 `memo-search.md`: ナレッジの検索
- 🔧 `memo-maintenance.md`: ナレッジのメンテナンス
- 📊 `project-info.md`: プロジェクト情報の確認

### ナレッジの追加

```bash
# 基本的な追加
chroma-memo add my-project "Pythonの基本構文についてのメモ"

# タグ付きで追加
chroma-memo add my-project "FastAPIのルーティング設定" --tags python --tags web
```

### ナレッジの検索

```bash
chroma-memo search my-project "Python 構文"

# 検索結果数を制限
chroma-memo search my-project "API" --max-results 5
```

### ナレッジの一覧表示

```bash
chroma-memo list my-project
```

### ナレッジの削除

```bash
chroma-memo del my-project <entry_id>

# 確認をスキップ
chroma-memo del my-project <entry_id> --confirm
```

### プロジェクト管理

```bash
# 全プロジェクトの一覧
chroma-memo projects

# プロジェクトの詳細情報
chroma-memo info my-project
```

### 設定の確認

```bash
# 現在の設定を表示
chroma-memo config

# APIキーの設定
chroma-memo config --set-api-key openai

# .envファイルのパスを確認
chroma-memo config --show-env-path

# データベースのパスを確認
chroma-memo config --show-db-path

# 全てのパスと状態を確認
chroma-memo config --show-all-paths
```

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

## 設定

設定ファイルは `~/.chroma-memo/config.yaml` に保存されます。

```yaml
embedding:
  model: "text-embedding-3-small"
  provider: "openai"
  api_key_env: "OPENAI_API_KEY"
db_path: "~/.chroma-memo/db"
max_results: 10
similarity_threshold: 0.7
export_formats:
  - json
  - csv
  - markdown
```

## 🤖 Claude Code連携

Chroma-MemoはClaude Codeとシームレスに連携できます。プロジェクト初期化時に`--with-claude-command`オプションを使用すると、自動的にClaude Code用のコマンドテンプレートが生成されます。

### Claude Codeコマンドの使用方法

1. **プロジェクト初期化時に自動生成**
   ```bash
   chroma-memo init my-project --with-claude-command
   ```
   
2. **生成されるコマンド**
   - `/memo-add`: 会話履歴や実装内容からナレッジを抽出・追加
   - `/memo-search`: プロジェクトのナレッジを検索
   - `/memo-maintenance`: 古いナレッジの更新・削除
   - `/project-info`: プロジェクトの統計情報を確認

3. **Claude Codeでの使用例**
   ```
   # Claude Code内で
   /memo-add 今回の実装で学んだReact Hooksのベストプラクティスをまとめて
   /memo-search TypeScriptの型定義について
   /memo-maintenance 古いAPI仕様のナレッジを削除して
   ```

## 使用例

### 機械学習プロジェクトの例

```bash
# Claude Code連携付きでプロジェクト初期化
chroma-memo init machine-learning-notes --with-claude-command

# ナレッジの追加
chroma-memo add machine-learning-notes "線形回帰は教師あり学習の手法で、連続値を予測する" --tags regression --tags supervised

chroma-memo add machine-learning-notes "ランダムフォレストは決定木の集合学習手法" --tags ensemble --tags tree

# 検索
chroma-memo search machine-learning-notes "回帰"
# 結果:
# 🔍 検索結果: 1件
# 
# ┌─ #1 [タグ: regression, supervised] ────────────────────────────────────────┐
# │ 線形回帰は教師あり学習の手法で、連続値を予測する                           │
# │                                                                            │
# │ 類似度: 0.892 | ID: abc12345 | 作成: 2024-01-01 10:30                     │
# └────────────────────────────────────────────────────────────────────────────┘

# プロジェクト一覧
chroma-memo projects
# 結果:
# 📁 プロジェクト一覧: 1件
# 
# ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
# ┃ プロジェクト名        ┃ エントリ数 ┃ 作成日     ┃ 最終更新   ┃
# ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
# │ machine-learning-notes │        2 │ 2024-01-01 │ 2024-01-01 │
# └───────────────────────┴──────────┴────────────┴────────────┘
```

## 技術詳細

- **ベクトルデータベース**: ChromaDB (永続化対応)
- **埋め込みモデル**: OpenAI text-embedding-3-small (1536次元)
- **CLIフレームワーク**: Click
- **UIライブラリ**: Rich
- **データ検証**: Pydantic
- **設定管理**: YAML + 環境変数

## トラブルシューティング

### APIキーエラー

```
API key not found in environment variable: OPENAI_API_KEY
```

OpenAI APIキーが設定されていません。環境変数を確認してください：

```bash
echo $OPENAI_API_KEY
export OPENAI_API_KEY="your_api_key_here"
```

### パッケージインストールエラー

依存関係が不足している可能性があります：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### データベースエラー

データベースファイルが破損している場合、リセットしてください：

```bash
rm -rf ~/.chroma-memo/db
```

## インストール・アンインストール

### 対話型インストーラー

```bash
# 対話型インストーラーを起動
./install.sh
```

インストーラーが提供するオプション：
- 📦 **ユーザー環境インストール**: ~/.local/bin にインストール（推奨）
- 🌍 **システム全体インストール**: /usr/local/bin にインストール（sudo必要）
- 🔧 **仮想環境インストール**: 現在の仮想環境にインストール
- 📥 **実行ファイルのビルド**: スタンドアロン実行ファイルを作成（PyInstaller使用）

### アンインストール

```bash
# パッケージとデータを完全削除
./uninstall.sh

# データを保持してパッケージのみ削除
./uninstall.sh --keep-data
```

## データ保存場所

### 📂 デフォルト保存先
- **設定ファイル**: `~/.chroma-memo/config.yaml`
- **.envファイル**: `~/.chroma-memo/.env`
- **データベース**: `~/.chroma-memo/db/`

### 📊 保存場所の確認
```bash
# データベースの場所と状態を確認
chroma-memo config --show-db-path

# 全てのファイル場所を確認
chroma-memo config --show-all-paths
```

### 🔧 保存場所の変更
設定ファイル (`~/.chroma-memo/config.yaml`) を編集：
```yaml
db_path: "/path/to/your/custom/db"
```

## 開発

### 開発環境のセットアップ

```bash
# 開発モードでインストール
pip install -e .

# テストの実行
python -m pytest tests/

# 型チェック
mypy chroma_memo/
```

## ライセンス

MIT License

## 貢献

Issue や Pull Request をお待ちしています！ 