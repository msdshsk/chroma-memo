@echo off
setlocal enabledelayedexpansion

REM Chroma-Memo 自動セットアップ・実行スクリプト (Windows版)
REM Usage: run.bat [command] [args...]

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set PYTHON_CMD=python

echo 🚀 Chroma-Memo セットアップ・実行スクリプト
echo ==============================================

REM Pythonの存在確認
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python が見つかりません。Pythonをインストールしてください。
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM venvの作成
if not exist "%VENV_DIR%" (
    echo [INFO] 仮想環境を作成中...
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    echo [SUCCESS] 仮想環境を作成しました: %VENV_DIR%
) else (
    echo [INFO] 仮想環境が既に存在します: %VENV_DIR%
)

REM venvのアクティベート
echo [INFO] 仮想環境をアクティベート中...
call "%VENV_DIR%\Scripts\activate.bat"
echo [SUCCESS] 仮想環境をアクティベートしました

REM requirements.txtの存在確認
if not exist "%SCRIPT_DIR%requirements.txt" (
    echo [ERROR] requirements.txt が見つかりません
    pause
    exit /b 1
)

REM 依存関係のインストール
echo [INFO] 依存関係をチェック中...

echo [INFO] pip をアップグレード中...
pip install --upgrade pip --quiet

echo [INFO] 依存関係をインストール中...
pip install -r "%SCRIPT_DIR%requirements.txt" --quiet

echo [INFO] chroma-memo パッケージをインストール中...
pip install -e "%SCRIPT_DIR%" --quiet

echo [SUCCESS] すべての依存関係をインストールしました
echo.

REM APIキーの確認
if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] OpenAI API キーが設定されていません
    echo.
    echo 以下のいずれかの方法でAPIキーを設定してください：
    echo 1. 環境変数: set OPENAI_API_KEY=your_api_key
    echo 2. 設定コマンド: chroma-memo config --set-api-key openai
    echo 3. .envファイル: ~/.chroma-memo/.env
    echo.
    set /p SETUP_KEY="APIキーを今すぐ設定しますか？ (y/n): "
    if /i "!SETUP_KEY!"=="y" (
        chroma-memo config --set-api-key openai
    ) else (
        echo [INFO] 後でAPIキーを設定してください
    )
) else (
    echo [SUCCESS] OpenAI API キーが設定されています
)

echo [SUCCESS] セットアップが完了しました！
echo.
echo ==============================================

REM chroma-memo実行
if "%~1"=="" (
    echo [INFO] Chroma-Memo を起動します
    chroma-memo --help
) else (
    echo [INFO] コマンドを実行中: chroma-memo %*
    chroma-memo %*
)

pause 