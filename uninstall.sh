#!/bin/bash

# Chroma-Memo アンインストールスクリプト
# Usage: ./uninstall.sh [--keep-data]

set -e

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

KEEP_DATA=false

# 引数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --keep-data)
            KEEP_DATA=true
            shift
            ;;
        --help)
            echo "Chroma-Memo アンインストールスクリプト"
            echo ""
            echo "Usage: $0 [--keep-data]"
            echo ""
            echo "Options:"
            echo "  --keep-data   データベースと設定ファイルを保持"
            echo "  --help        このヘルプを表示"
            echo ""
            echo "デフォルトでは以下が削除されます："
            echo "  - chroma-memoパッケージ"
            echo "  - ~/.chroma-memo/ ディレクトリ（設定とDB）"
            exit 0
            ;;
        *)
            print_error "不明なオプション: $1"
            exit 1
            ;;
    esac
done

echo "🗑️  Chroma-Memo アンインストール"
echo "================================="

# pipの存在確認
PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    if command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip が見つかりません"
        exit 1
    fi
fi

# chroma-memoの存在確認
if ! command -v chroma-memo &> /dev/null; then
    print_warning "chroma-memo コマンドが見つかりません（すでにアンインストール済み？）"
else
    print_info "chroma-memo パッケージをアンインストール中..."
    $PIP_CMD uninstall chroma-memo -y || print_warning "パッケージのアンインストールに失敗しました"
fi

# データディレクトリの処理
CHROMA_DIR="$HOME/.chroma-memo"
if [ -d "$CHROMA_DIR" ]; then
    if [ "$KEEP_DATA" = true ]; then
        print_info "データディレクトリを保持します: $CHROMA_DIR"
    else
        print_warning "データディレクトリを削除します: $CHROMA_DIR"
        echo "以下のファイル/ディレクトリが削除されます："
        find "$CHROMA_DIR" -type f | head -10
        if [ $(find "$CHROMA_DIR" -type f | wc -l) -gt 10 ]; then
            echo "... および他のファイル"
        fi
        echo ""
        read -p "本当に削除しますか？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$CHROMA_DIR"
            print_success "データディレクトリを削除しました"
        else
            print_info "データディレクトリを保持します"
        fi
    fi
else
    print_info "データディレクトリが見つかりません: $CHROMA_DIR"
fi

# 確認
if command -v chroma-memo &> /dev/null; then
    print_warning "chroma-memo コマンドがまだ使用可能です"
    print_info "ターミナルを再起動してください"
else
    print_success "chroma-memo コマンドが正常にアンインストールされました"
fi

print_success "アンインストール完了！" 