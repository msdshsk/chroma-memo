#!/bin/bash

# Chroma-Memo インストールスクリプト
# 対話型で複数のインストール方法を選択可能

set -e

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

print_menu() {
    echo -e "${CYAN}$1${NC}"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ヘルプ表示
show_help() {
    echo "Chroma-Memo インストールスクリプト"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help     このヘルプを表示"
    echo "  --quick    対話モードをスキップして標準インストール"
    echo ""
    echo "対話モードでは以下から選択できます:"
    echo "  - pipxインストール（推奨）"
    echo "  - ユーザー環境へのインストール"
    echo "  - システム全体へのインストール"
    echo "  - バイナリビルド（スタンドアロン実行ファイル）"
}

# 引数解析
QUICK_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            show_help
            exit 0
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        *)
            print_error "不明なオプション: $1"
            show_help
            exit 1
            ;;
    esac
done

# Python3の存在確認
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 が見つかりません。Python3をインストールしてください。"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python version: $PYTHON_VERSION"
    
    # Python 3.8以上の確認
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [[ $MAJOR -lt 3 ]] || [[ $MAJOR -eq 3 && $MINOR -lt 8 ]]; then
        print_warning "Python 3.8以上を推奨します"
    fi
    
    return 0
}

# pipxの存在確認
check_pipx() {
    if command -v pipx &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# pipの存在確認
check_pip() {
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        return 0
    else
        print_error "pip が見つかりません。pipをインストールしてください。"
        return 1
    fi
}

# PyInstallerの存在確認
check_pyinstaller() {
    if python3 -c "import PyInstaller" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# pipxでインストール
install_with_pipx() {
    print_info "pipxでインストールを開始します..."
    
    if ! check_pipx; then
        print_error "pipx がインストールされていません"
        echo ""
        echo "pipxのインストール方法:"
        echo "  Ubuntu/Debian: sudo apt install pipx"
        echo "  macOS: brew install pipx"
        echo "  その他: pip install --user pipx"
        echo ""
        echo "詳細: https://pypa.github.io/pipx/"
        return 1
    fi
    
    print_info "pipxでchroma-memoをインストール中..."
    if pipx install -e "$SCRIPT_DIR"; then
        print_success "pipxでのインストールが完了しました！"
        echo ""
        print_info "pipxは隔離された環境にインストールするため、依存関係の競合を避けられます"
        return 0
    else
        print_error "pipxでのインストールに失敗しました"
        return 1
    fi
}

# ユーザー環境にインストール
install_user() {
    print_info "ユーザー環境へのインストールを開始します..."
    
    if ! check_pip; then
        return 1
    fi
    
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    print_info "依存関係をインストール中..."
    $PIP_CMD install --user -r "$SCRIPT_DIR/requirements.txt" --quiet
    
    print_info "chroma-memo パッケージをインストール中..."
    $PIP_CMD install --user -e "$SCRIPT_DIR" --quiet
    
    print_success "ユーザー環境へのインストールが完了しました！"
    
    # パスの確認
    USER_BIN_PATH=$(python3 -m site --user-base)/bin
    if [[ ":$PATH:" != *":$USER_BIN_PATH:"* ]]; then
        print_warning "ユーザーbinディレクトリがPATHに含まれていません"
        echo ""
        echo "以下のコマンドを実行してPATHに追加してください："
        echo "echo 'export PATH=\"$USER_BIN_PATH:\$PATH\"' >> ~/.bashrc"
        echo "source ~/.bashrc"
        echo ""
        echo "または ~/.zshrc を使用している場合："
        echo "echo 'export PATH=\"$USER_BIN_PATH:\$PATH\"' >> ~/.zshrc"
        echo "source ~/.zshrc"
    fi
    
    return 0
}

# システム全体にインストール
install_system() {
    print_info "システム全体へのインストールを開始します..."
    print_warning "この操作にはsudo権限が必要です"
    
    if ! check_pip; then
        return 1
    fi
    
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    print_info "依存関係をインストール中..."
    if ! sudo $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt" --quiet; then
        print_error "依存関係のインストールに失敗しました"
        return 1
    fi
    
    print_info "chroma-memo パッケージをインストール中..."
    if ! sudo $PIP_CMD install -e "$SCRIPT_DIR" --quiet; then
        print_error "chroma-memoのインストールに失敗しました"
        return 1
    fi
    
    print_success "システム全体へのインストールが完了しました！"
    return 0
}

# バイナリビルド
build_binary() {
    print_info "バイナリビルドを開始します..."
    print_info "隔離された仮想環境でビルドを実行します"
    
    VENV_DIR="$SCRIPT_DIR/build-venv"
    
    # 既存の仮想環境があれば削除
    if [ -d "$VENV_DIR" ]; then
        print_info "既存のビルド環境を削除中..."
        rm -rf "$VENV_DIR"
    fi
    
    # 仮想環境の作成
    print_info "ビルド用仮想環境を作成中..."
    python3 -m venv "$VENV_DIR"
    
    # 仮想環境のアクティベート
    source "$VENV_DIR/bin/activate"
    
    # pipのアップグレード
    print_info "pipをアップグレード中..."
    pip install --upgrade pip --quiet
    
    # 依存関係のインストール
    print_info "依存関係をインストール中..."
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    
    # PyInstallerのインストール
    print_info "PyInstallerをインストール中..."
    pip install pyinstaller --quiet
    
    # build.pyの実行
    if [ -f "$SCRIPT_DIR/build.py" ]; then
        print_info "build.pyを実行中..."
        cd "$SCRIPT_DIR"
        
        # ビルドログディレクトリの作成
        mkdir -p build_logs
        
        # build.pyを実行
        python3 build.py 2>&1 | tee build_logs/install_build.log
        BUILD_RESULT=${PIPESTATUS[0]}
        
        # 仮想環境を抜ける
        deactivate
        
        # 成功時の処理
        if [ $BUILD_RESULT -eq 0 ]; then
            print_success "ビルドが成功しました！"
            
            # ビルド成果物の確認
            if [ -f "$SCRIPT_DIR/dist/chroma-memo" ]; then
                print_info "実行ファイル: $SCRIPT_DIR/dist/chroma-memo"
                print_info "ファイルサイズ: $(du -h $SCRIPT_DIR/dist/chroma-memo | cut -f1)"
                
                echo ""
                echo "バイナリをシステムにインストールしますか？"
                echo "インストール先を選択してください:"
                echo "1) ユーザーディレクトリ (~/.local/bin/)"
                echo "2) システムディレクトリ (/usr/local/bin/) [要sudo]"
                echo "3) インストールしない"
                echo ""
                read -p "選択 (1-3): " install_choice
                
                case $install_choice in
                    1)
                        mkdir -p "$HOME/.local/bin"
                        cp "$SCRIPT_DIR/dist/chroma-memo" "$HOME/.local/bin/"
                        chmod +x "$HOME/.local/bin/chroma-memo"
                        print_success "~/.local/bin/ にインストールしました"
                        
                        # PATH確認
                        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                            print_warning "~/.local/bin がPATHに含まれていません"
                            echo "以下をシェルの設定ファイルに追加してください:"
                            echo 'export PATH="$HOME/.local/bin:$PATH"'
                        fi
                        ;;
                    2)
                        sudo cp "$SCRIPT_DIR/dist/chroma-memo" /usr/local/bin/
                        sudo chmod +x /usr/local/bin/chroma-memo
                        print_success "/usr/local/bin/ にインストールしました"
                        ;;
                    3)
                        print_info "インストールをスキップしました"
                        ;;
                    *)
                        print_warning "無効な選択です。インストールをスキップしました"
                        ;;
                esac
            fi
        else
            print_error "ビルドに失敗しました"
            print_error "詳細なエラー情報："
            print_error "1. build_logs/install_build.log"
            print_error "2. build_logs/build_*.log (タイムスタンプ付き)"
            print_error "3. build/chroma-memo/warn-chroma-memo.txt (存在する場合)"
            echo ""
            echo "最近のエラーログ:"
            echo "=================="
            tail -n 20 build_logs/install_build.log | grep -E "(ERROR|error|Failed|failed)" || echo "エラーメッセージが見つかりません"
        fi
        
        # 仮想環境の削除確認
        echo ""
        echo "ビルド用仮想環境を削除しますか？ (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "仮想環境を削除しました"
        else
            print_info "仮想環境を保持します: $VENV_DIR"
        fi
        
        return $BUILD_RESULT
    else
        print_error "build.pyが見つかりません"
        deactivate
        return 1
    fi
}

# インストール確認
verify_installation() {
    print_info "インストール確認中..."
    
    if command -v chroma-memo &> /dev/null; then
        INSTALLED_VERSION=$(chroma-memo --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "不明")
        print_success "chroma-memo コマンドが使用可能です (version: $INSTALLED_VERSION)"
        echo ""
        echo "🎉 使用例:"
        echo "  chroma-memo init my-project"
        echo "  chroma-memo add my-project \"メモ内容\""
        echo "  chroma-memo search my-project \"検索語\""
        echo "  chroma-memo --help"
    else
        print_warning "chroma-memo コマンドが見つかりません"
        echo "ターミナルを再起動するか、PATHを更新してください"
    fi
    
    echo ""
    print_info "設定ファイルとデータベースの保存場所:"
    echo "  設定: ~/.chroma-memo/config.yaml"
    echo "  .env: ~/.chroma-memo/.env"
    echo "  DB:   ~/.chroma-memo/db/"
}

# メイン処理
main() {
    echo "🚀 Chroma-Memo インストーラー"
    echo "==============================="
    echo ""
    
    # Python確認
    if ! check_python; then
        exit 1
    fi
    
    # クイックモードの場合は標準インストール
    if [ "$QUICK_MODE" = true ]; then
        print_info "クイックモード: ユーザー環境にインストールします"
        if install_user; then
            verify_installation
            print_success "インストール完了！"
        else
            print_error "インストールに失敗しました"
            exit 1
        fi
        exit 0
    fi
    
    # 対話型メニュー
    echo "インストール方法を選択してください:"
    echo ""
    
    # pipxの状態確認
    if check_pipx; then
        print_menu "1) pipx でインストール (推奨) ✓ pipx利用可能"
    else
        print_menu "1) pipx でインストール (要pipxインストール)"
    fi
    
    print_menu "2) ユーザー環境にインストール (~/.local/)"
    print_menu "3) システム全体にインストール (要sudo)"
    print_menu "4) バイナリをビルド (スタンドアロン実行ファイル)"
    print_menu "5) キャンセル"
    echo ""
    
    read -p "選択してください (1-5): " choice
    echo ""
    
    case $choice in
        1)
            if install_with_pipx; then
                verify_installation
                print_success "インストール完了！"
            else
                print_error "インストールに失敗しました"
                exit 1
            fi
            ;;
        2)
            if install_user; then
                verify_installation
                print_success "インストール完了！"
            else
                print_error "インストールに失敗しました"
                exit 1
            fi
            ;;
        3)
            if install_system; then
                verify_installation
                print_success "インストール完了！"
            else
                print_error "インストールに失敗しました"
                exit 1
            fi
            ;;
        4)
            if build_binary; then
                print_success "ビルド完了！"
            else
                print_error "ビルドに失敗しました"
                exit 1
            fi
            ;;
        5)
            print_info "インストールをキャンセルしました"
            exit 0
            ;;
        *)
            print_error "無効な選択です"
            exit 1
            ;;
    esac
}

# 実行
main