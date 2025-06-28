# MCP (Model Context Protocol) ガイド

Chroma-MemoをMCPサーバーとして使用し、Claude CodeやCursorから直接アクセスする方法を説明します。

## MCPとは

MCP (Model Context Protocol) は、AIアシスタントが外部ツールやデータソースと対話するための標準プロトコルです。Chroma-MemoはMCPサーバーとして動作し、Claude CodeやCursorから直接ナレッジベースにアクセスできます。

## 利用可能なMCPツール

Chroma-MemoのMCPサーバーは以下のツールを提供します：

### 基本ツール（全プロジェクト対応）

| ツール名 | 説明 | パラメータ |
|---------|------|-----------|
| **memo_add** | ナレッジを追加 | `content` (必須), `tags` (任意), `project` (任意※) |
| **memo_search** | ナレッジを検索 | `project` (必須), `query` (必須), `max_results` (任意、デフォルト: 5) |
| **memo_list** | ナレッジの一覧表示 | `project` (必須) |
| **memo_get** | ID指定でナレッジを取得 | `project` (必須), `entry_id` (必須) |
| **memo_delete** | ナレッジを削除 | `project` (必須), `entry_id` (必須) |
| **projects_list** | 全プロジェクトの一覧 | なし |
| **project_info** | プロジェクトの詳細情報 | `project` (必須) |

※ `memo_add`の`project`パラメータは、プロジェクト指定でサーバー起動時は省略可能

### プロジェクト特化ツール（特定プロジェクトでサーバー起動時のみ）

| ツール名 | 説明 | パラメータ |
|---------|------|-----------|
| **add_to_current_project** | 現在のプロジェクトに追加 | `content` (必須), `tags` (任意) |
| **search_current_project** | 現在のプロジェクトで検索 | `query` (必須), `max_results` (任意、デフォルト: 5) |
| **list_current_project** | 現在のプロジェクトの一覧 | なし |
| **get_from_current_project** | 現在のプロジェクトからID指定で取得 | `entry_id` (必須) |
| **delete_from_current_project** | 現在のプロジェクトから削除 | `entry_id` (必須) |

## クイックスタート

### ステップ1: Chroma-Memoのインストール

```bash
# インストール（詳細はINSTALL.mdを参照）
./install.sh
```

### ステップ2: Claude CodeにMCPサーバーを追加

```bash
# プロジェクト用のMCPサーバーを追加（最も簡単な方法）
claude mcp add chroma-memo chroma-memo serve my-project

# APIキーが設定されていない場合は環境変数付きで追加
claude mcp add chroma-memo -e OPENAI_API_KEY=your-api-key -- chroma-memo serve my-project
```

### ステップ3: 接続確認

```bash
# 追加されたサーバーを確認
claude mcp list
```

これで準備完了です！Claude Code内でChroma-Memoのツールが使用できます。

## MCPサーバーの起動方法

### 特定プロジェクト用

```bash
# プロジェクトが存在しない場合は自動で作成
chroma-memo serve my-project
```

### 全プロジェクト対応

```bash
# プロジェクト名を指定しない場合、全プロジェクトにアクセス可能
chroma-memo serve
```

## Claude Codeでの設定

### 方法1: CLIコマンドで追加（推奨・最も簡単）

Claude Codeの`claude`コマンドを使用してMCPサーバーを追加：

```bash
# 基本的な追加方法
claude mcp add chroma-memo chroma-memo serve my-project

# 環境変数付きで追加（APIキーが必要な場合）
claude mcp add chroma-memo -e OPENAI_API_KEY=your-api-key -- chroma-memo serve my-project

# 絶対パスを使用する場合
claude mcp add chroma-memo /home/user/.local/bin/chroma-memo serve my-project
```

### 方法2: 設定ファイルの直接編集

より詳細な設定が必要な場合は、`.claude.json`ファイルを直接編集：

#### 1. 設定ファイルの準備

プロジェクトルートに `.claude.json` ファイルを作成：

```json
{
  "mcpServers": {
    "chroma-memo": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "my-project"]
    }
  }
}
```

#### 2. 環境変数の設定

APIキーが必要な場合：

```json
{
  "mcpServers": {
    "chroma-memo": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "my-project"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 接続確認

1. **設定したサーバーの一覧表示**：
   ```bash
   claude mcp list
   ```

2. **特定のサーバーの詳細確認**：
   ```bash
   claude mcp get chroma-memo
   ```

3. **Claude Code内での確認**：
   ```
   /mcp
   ```
   「chroma-memo」が「connected」ステータスで表示されれば成功です。

### その他の便利なコマンド

```bash
# サーバーの削除
claude mcp remove chroma-memo

# スコープを指定して追加（local/project/user）
claude mcp add -s project chroma-memo chroma-memo serve my-project

# ヘルプ表示
claude mcp --help
```

## Cursorでの設定

Cursorも同様の設定ファイル形式をサポートしています。プロジェクトルートに `.mcp.json` ファイルを作成：

```json
{
  "mcpServers": {
    "chroma-memo": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "my-project"]
    }
  }
}
```

## 使用例

### Claude Code内での使用

MCPサーバーが接続されると、Claude Codeは自動的にツールを認識します：

```
User: このプロジェクトに React Hooks のベストプラクティスについてメモを追加して
Assistant: memo_add ツールを使用して追加します...

User: TypeScriptの型定義について検索して
Assistant: memo_search ツールを使用して検索します...
```

### プロジェクト管理

```
User: どんなプロジェクトがあるか教えて
Assistant: projects_list ツールで確認します...

User: machine-learning-notesプロジェクトの詳細を見せて
Assistant: project_info ツールで情報を取得します...
```

## トラブルシューティング

### 接続エラー

1. **コマンドが見つからない**
   - `chroma-memo`がPATHに含まれているか確認
   - 絶対パスを使用して設定

2. **権限エラー**
   - 実行権限があるか確認: `chmod +x $(which chroma-memo)`

3. **APIキーエラー**
   - 環境変数にAPIキーを設定
   - または設定ファイルの`env`セクションに追加

### デバッグ方法

1. **直接実行テスト**
   ```bash
   chroma-memo serve my-project
   ```
   
2. **ログ確認**
   - MCPサーバーはstderrにログを出力
   - stdoutはJSON-RPC通信専用

3. **設定確認**
   ```bash
   chroma-memo config --show-all-paths
   ```

## ベストプラクティス

### プロジェクト構成

```
my-project/
├── .claude.json       # Claude Code設定
├── .mcp.json         # Cursor設定（オプション）
├── src/              # ソースコード
└── docs/             # ドキュメント
```

### 推奨ワークフロー

1. **プロジェクト初期化時**
   ```bash
   chroma-memo init my-project --with-claude-command
   ```

2. **開発開始時**
   ```bash
   chroma-memo serve my-project
   ```

3. **Claude Code内で作業**
   - 自然言語でナレッジの追加・検索
   - コード実装時の参照情報として活用

### セキュリティ

- APIキーは`.env`ファイルか環境変数で管理
- `.claude.json`にAPIキーを直接記載しない
- プロジェクト固有の設定は`.gitignore`に追加

## 高度な設定

### 複数プロジェクトの同時利用

```json
{
  "mcpServers": {
    "chroma-memo-backend": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "backend-project"]
    },
    "chroma-memo-frontend": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "frontend-project"]
    }
  }
}
```

### カスタムデータベースパス

環境変数で設定：

```json
{
  "mcpServers": {
    "chroma-memo": {
      "type": "stdio",
      "command": "chroma-memo",
      "args": ["serve", "my-project"],
      "env": {
        "CHROMA_MEMO_DB_PATH": "/custom/path/to/db"
      }
    }
  }
}
```

## まとめ

Chroma-MemoのMCP機能により、Claude CodeやCursorから直接ナレッジベースにアクセスできます。これにより、開発中の情報管理が大幅に効率化され、AIアシスタントがプロジェクト固有の知識を活用できるようになります。