# インストールガイド

Chroma-Memoのインストール方法を説明します。複数の方法から選択できます。

## 🎯 対話型インストーラー使用（推奨）

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

## 🚀 ローカル実行（すぐに試したい場合）

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

### 4. APIキーの設定

Chroma-MemoはOpenAIとGoogle Geminiの両方に対応しています。

#### 方法1: 設定コマンド（推奨）

**OpenAI APIキーの設定**
```bash
chroma-memo config --set-api-key openai
# プロンプトでAPIキーを入力（非表示入力）
```

**Google API キーの設定**
```bash
chroma-memo config --set-api-key google
# プロンプトでAPIキーを入力（非表示入力）
```

#### 方法2: .envファイル

`~/.chroma-memo/.env` ファイルを作成：

**OpenAI使用の場合**
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

**Google使用の場合**
```bash
# Google API Key
GOOGLE_API_KEY=your_google_api_key_here
USE_API=GOOGLE
```

**両方設定する場合**
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# 使用するAPI（OPENAI または GOOGLE）
USE_API=GOOGLE
```

#### 方法3: 環境変数

**OpenAI**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

**Google**
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export USE_API="GOOGLE"
```

#### APIキーの取得方法

**OpenAI APIキー**
- [OpenAI Platform](https://platform.openai.com/api-keys) でアカウント作成
- APIキーを生成して取得

**Google API キー**
- [Google AI Studio](https://aistudio.google.com/app/apikey) でアカウント作成
- APIキーを生成して取得

#### API切り替え方法

使用するAPIを切り替えるには、`USE_API`環境変数を設定：

```bash
# OpenAIに切り替え
export USE_API=OPENAI

# Googleに切り替え
export USE_API=GOOGLE
```

または`.env`ファイルで：

```bash
USE_API=GOOGLE
```

## インストールオプション

### 対話型インストーラーのオプション

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

## トラブルシューティング

### APIキーエラー

```
API key not found in environment variable: OPENAI_API_KEY
```

**OpenAI APIキーエラー**

OpenAI APIキーが設定されていません：

```bash
# 確認
echo $OPENAI_API_KEY

# 設定
export OPENAI_API_KEY="your_api_key_here"
# または
chroma-memo config --set-api-key openai
```

**Google APIキーエラー**
```
Google API キーが設定されていません
```

Google APIキーが設定されていません：

```bash
# 確認
echo $GOOGLE_API_KEY

# 設定
export GOOGLE_API_KEY="your_api_key_here"
export USE_API="GOOGLE"
# または
chroma-memo config --set-api-key google
```

### API切り替えの問題

使用するAPIを切り替えたい場合：

```bash
# 現在の設定確認
chroma-memo config

# GoogleからOpenAIに切り替え
export USE_API=OPENAI

# OpenAIからGoogleに切り替え
export USE_API=GOOGLE
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

## インストール確認

インストールが正常に完了したか確認：

```bash
# バージョン確認
chroma-memo --version

# ヘルプ表示
chroma-memo --help

# 設定確認
chroma-memo config
```

## 開発環境のセットアップ

開発に参加する場合：

```bash
# 開発モードでインストール
pip install -e .

# テストの実行
python -m pytest tests/

# 型チェック
mypy chroma_memo/
```