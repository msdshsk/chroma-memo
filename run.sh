#!/bin/bash

# Chroma-Memo 自動セットアップ・実行スクリプト
# Usage: ./run.sh [command] [args...]

set -e  # エラー時に終了

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_CMD="python3"

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Python3の存在確認
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 が見つかりません。Python3をインストールしてください。"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python version: $PYTHON_VERSION"
}

# venvの作成
create_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_info "仮想環境を作成中..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "仮想環境を作成しました: $VENV_DIR"
    else
        print_info "仮想環境が既に存在します: $VENV_DIR"
    fi
}

# venvのアクティベート
activate_venv() {
    print_info "仮想環境をアクティベート中..."
    source "$VENV_DIR/bin/activate"
    print_success "仮想環境をアクティベートしました"
}

# 依存関係のインストール
install_dependencies() {
    print_info "依存関係をチェック中..."
    
    # requirements.txtが存在するかチェック
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        print_error "requirements.txt が見つかりません"
        exit 1
    fi
    
    # pipのアップグレード
    print_info "pip をアップグレード中..."
    pip install --upgrade pip --quiet
    
    # 依存関係のインストール
    print_info "依存関係をインストール中..."
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    
    # パッケージのインストール（開発モード）
    print_info "chroma-memo パッケージをインストール中..."
    pip install -e "$SCRIPT_DIR" --quiet
    
    print_success "すべての依存関係をインストールしました"
}

# APIキーの確認
check_api_key() {
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OpenAI API キーが設定されていません"
        echo ""
        echo "以下のいずれかの方法でAPIキーを設定してください："
        echo "1. 環境変数: export OPENAI_API_KEY='your_api_key'"
        echo "2. 設定コマンド: chroma-memo config --set-api-key openai"
        echo "3. .envファイル: ~/.chroma-memo/.env"
        echo ""
        read -p "APIキーを今すぐ設定しますか？ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            chroma-memo config --set-api-key openai
        else
            print_info "後でAPIキーを設定してください"
        fi
    else
        print_success "OpenAI API キーが設定されています"
    fi
}

# メイン実行関数
run_chroma_memo() {
    if [ $# -eq 0 ]; then
        print_info "Chroma-Memo を起動します"
        chroma-memo --help
    else
        print_info "コマンドを実行中: chroma-memo $*"
        chroma-memo "$@"
    fi
}

# ヘルプ表示
show_help() {
    echo "Chroma-Memo 自動セットアップ・実行スクリプト"
    echo ""
    echo "Usage: $0 [options] [chroma-memo-command] [args...]"
    echo ""
    echo "Options:"
    echo "  --setup-only    セットアップのみ実行（chroma-memoは起動しない）"
    echo "  --help          このヘルプを表示"
    echo ""
    echo "Examples:"
    echo "  $0                              # セットアップ後、ヘルプを表示"
    echo "  $0 init my-project              # セットアップ後、プロジェクト作成"
    echo "  $0 projects                     # セットアップ後、プロジェクト一覧"
    echo "  $0 --setup-only                 # セットアップのみ"
    echo ""
    echo "初回実行時は自動的に以下を行います："
    echo "  - Python仮想環境の作成"
    echo "  - 依存関係のインストール"
    echo "  - chroma-memoパッケージのインストール"
}

# メイン処理
main() {
    # 引数の解析
    if [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    SETUP_ONLY=false
    if [ "$1" = "--setup-only" ]; then
        SETUP_ONLY=true
        shift
    fi
    
    echo "🚀 Chroma-Memo セットアップ・実行スクリプト"
    echo "=============================================="
    
    # セットアップ処理
    check_python
    create_venv
    activate_venv
    install_dependencies
    
    print_success "セットアップが完了しました！"
    echo ""
    
    # APIキーの確認（セットアップのみの場合もチェック）
    check_api_key
    
    # セットアップのみの場合は終了
    if [ "$SETUP_ONLY" = true ]; then
        echo ""
        print_success "セットアップのみ完了しました"
        print_info "chroma-memo を使用するには: source venv/bin/activate && chroma-memo [command]"
        exit 0
    fi
    
    echo ""
    echo "=============================================="
    
    # chroma-memo実行
    run_chroma_memo "$@"
}

# スクリプト実行
main "$@" 