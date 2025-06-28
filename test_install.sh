#!/bin/bash

# Chroma-Memo インストールテストスクリプト
# Dockerコンテナ内で各インストール方法をテスト

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[TEST INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[TEST PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[TEST FAIL]${NC} $1"
}

print_section() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
}

# テスト結果を記録
RESULTS=()

# chroma-memoコマンドの動作確認
test_command() {
    local test_name=$1
    print_info "Testing: $test_name"
    
    # バージョン確認
    if chroma-memo --version &>/dev/null; then
        print_success "chroma-memo --version works"
    else
        print_error "chroma-memo --version failed"
        RESULTS+=("FAIL: $test_name - version check")
        return 1
    fi
    
    # ヘルプ確認
    if chroma-memo --help &>/dev/null; then
        print_success "chroma-memo --help works"
    else
        print_error "chroma-memo --help failed"
        RESULTS+=("FAIL: $test_name - help check")
        return 1
    fi
    
    # データベースディレクトリの作成を確実にする
    mkdir -p ~/.chroma-memo
    chmod 755 ~/.chroma-memo
    
    # プロジェクト初期化テスト（エラー出力も確認）
    test_project="test_project_$$"
    print_info "Initializing project: $test_project"
    if chroma-memo init "$test_project" 2>&1; then
        print_success "chroma-memo init works"
    else
        print_error "chroma-memo init failed"
        # エラーの詳細を表示
        chroma-memo init "$test_project" 2>&1 || true
        RESULTS+=("FAIL: $test_name - init")
        return 1
    fi
    
    # メモ追加テスト
    if chroma-memo add "$test_project" "テストメモ" 2>&1; then
        print_success "chroma-memo add works"
    else
        print_error "chroma-memo add failed"
        # エラーの詳細を表示
        chroma-memo add "$test_project" "テストメモ" 2>&1 || true
        RESULTS+=("FAIL: $test_name - add")
        return 1
    fi
    
    # 検索テスト
    if chroma-memo search "$test_project" "テスト" 2>&1; then
        print_success "chroma-memo search works"
        RESULTS+=("PASS: $test_name")
        return 0
    else
        print_error "chroma-memo search failed"
        # エラーの詳細を表示
        chroma-memo search "$test_project" "テスト" 2>&1 || true
        RESULTS+=("FAIL: $test_name - search")
        return 1
    fi
}

# クリーンアップ
cleanup() {
    print_info "Cleaning up..."
    
    # chroma-memoのアンインストール
    if command -v pipx &>/dev/null; then
        pipx uninstall chroma-memo &>/dev/null || true
    fi
    
    pip3 uninstall -y chroma-memo &>/dev/null || true
    sudo pip3 uninstall -y chroma-memo &>/dev/null || true
    
    # データベースのクリーンアップ
    rm -rf ~/.chroma-memo
    
    # パスのリセット（必要に応じて）
    unset PATH
    export PATH="/home/testuser/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
}

# メイン処理
main() {
    echo "🧪 Chroma-Memo インストールテスト"
    echo "=================================="
    echo ""
    
    # 環境情報の表示
    print_info "Test environment:"
    echo "  Python: $(python3 --version)"
    echo "  pip: $(pip3 --version)"
    echo "  pipx: $(pipx --version 2>/dev/null || echo 'not installed')"
    echo "  User: $(whoami)"
    echo ""
    
    # APIキーの設定（テスト用のダミーキー）
    export OPENAI_API_KEY="test-api-key-dummy"
    export GOOGLE_API_KEY="test-google-api-key-dummy"
    export USE_API="OPENAI"
    
    # 1. pipxインストールテスト
    print_section "Test 1: pipx Installation"
    cleanup
    
    if command -v pipx &>/dev/null; then
        # pipxパスの確保
        pipx ensurepath
        source ~/.bashrc 2>/dev/null || true
        
        # 作業ディレクトリにコピー（書き込み権限のあるディレクトリ）
        cp -r /app ~/chroma-memo-test
        cd ~/chroma-memo-test
        
        echo "1" | ./install.sh
        sleep 2
        
        # pipxインストール後のパス更新
        export PATH="/home/testuser/.local/bin:$PATH"
        
        test_command "pipx installation"
        
        # 元のディレクトリに戻る
        cd /app
    else
        print_error "pipx not available, skipping test"
        RESULTS+=("SKIP: pipx installation - pipx not available")
    fi
    
    # 2. ユーザー環境インストールテスト
    print_section "Test 2: User Installation"
    cleanup
    
    # 作業ディレクトリにコピー（書き込み権限のあるディレクトリ）
    cp -r /app ~/chroma-memo-test
    cd ~/chroma-memo-test
    
    echo "2" | ./install.sh
    sleep 2
    
    # ユーザーインストール後のパス更新
    export PATH="/home/testuser/.local/bin:$PATH"
    
    test_command "user installation"
    
    # 元のディレクトリに戻る
    cd /app
    
    # 3. システム全体インストールテスト（sudoが必要）
    print_section "Test 3: System Installation"
    cleanup
    
    # 作業ディレクトリにコピー（書き込み権限のあるディレクトリ）
    cp -r /app ~/chroma-memo-test
    cd ~/chroma-memo-test
    
    echo "3" | ./install.sh
    sleep 2
    
    test_command "system installation"
    
    # 元のディレクトリに戻る
    cd /app
    
    # 4. バイナリビルドテスト
    print_section "Test 4: Binary Build"
    cleanup
    
    # 作業ディレクトリにコピー（書き込み権限のあるディレクトリ）
    cp -r /app ~/chroma-memo-test
    cd ~/chroma-memo-test
    
    # PyInstallerのインストール確認
    if ! python3 -c "import PyInstaller" 2>/dev/null; then
        print_info "Installing PyInstaller for test..."
        pip3 install --user pyinstaller
    fi
    
    # バイナリビルドの実行（build.pyを直接実行）
    print_info "Running binary build..."
    if echo "" | python3 build.py; then
        if [ -f "dist/chroma-memo" ]; then
            print_success "Binary built successfully"
            
            # バイナリの動作テスト
            if ./dist/chroma-memo --version &>/dev/null; then
                print_success "Binary execution works"
                RESULTS+=("PASS: binary build")
            else
                print_error "Binary execution failed"
                RESULTS+=("FAIL: binary build - execution")
            fi
        else
            print_error "Binary not found"
            RESULTS+=("FAIL: binary build - file not found")
        fi
    else
        print_error "Binary build failed"
        RESULTS+=("FAIL: binary build - build process")
    fi
    
    # 元のディレクトリに戻る
    cd /app
    
    # テスト結果のサマリー
    print_section "Test Summary"
    
    echo "Test Results:"
    for result in "${RESULTS[@]}"; do
        if [[ $result == PASS* ]]; then
            echo -e "${GREEN}✓${NC} $result"
        elif [[ $result == SKIP* ]]; then
            echo -e "${YELLOW}⚠${NC} $result"
        else
            echo -e "${RED}✗${NC} $result"
        fi
    done
    
    # 最終クリーンアップ
    cleanup
    
    # 失敗があったかチェック
    for result in "${RESULTS[@]}"; do
        if [[ $result == FAIL* ]]; then
            print_error "Some tests failed!"
            exit 1
        fi
    done
    
    print_success "All tests passed!"
}

# スクリプト実行
main