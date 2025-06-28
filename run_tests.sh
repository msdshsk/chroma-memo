#!/bin/bash

# Dockerを使ったインストールテストの実行スクリプト

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🐳 Chroma-Memo Docker Installation Tests${NC}"
echo "========================================"
echo ""

# Dockerの確認
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker Compose is not installed"
    exit 1
fi

# テスト方法の選択
echo "Select test mode:"
echo "1) Quick test (Ubuntu only)"
echo "2) Full test (Ubuntu + Debian)"
echo "3) Interactive mode (bash shell)"
echo ""
read -p "Choice (1-3): " choice

case $choice in
    1)
        echo -e "\n${BLUE}Running Ubuntu tests...${NC}"
        docker build -f Dockerfile.test -t chroma-memo-test:ubuntu .
        docker run --rm -v "$(pwd)":/app:ro chroma-memo-test:ubuntu /app/test_install.sh
        ;;
    2)
        echo -e "\n${BLUE}Running full tests...${NC}"
        docker-compose -f docker-compose.test.yml build
        docker-compose -f docker-compose.test.yml up --abort-on-container-exit
        docker-compose -f docker-compose.test.yml down
        ;;
    3)
        echo -e "\n${BLUE}Starting interactive shell...${NC}"
        echo -e "${YELLOW}You can manually test installation methods:${NC}"
        echo "  ./install.sh    - Run interactive installer"
        echo "  ./test_install.sh - Run automated tests"
        echo ""
        docker build -f Dockerfile.test -t chroma-memo-test:ubuntu .
        docker run --rm -it -v "$(pwd)":/app:ro chroma-memo-test:ubuntu /bin/bash
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Test completed!${NC}"