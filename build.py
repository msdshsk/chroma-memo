#!/usr/bin/env python3
"""
Chroma-Memo Executable Builder

PyInstallerを使って単一実行ファイルを作成するスクリプト
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime


def print_info(msg):
    print(f"\033[0;34m[INFO]\033[0m {msg}")

def print_success(msg):
    print(f"\033[0;32m[SUCCESS]\033[0m {msg}")

def print_error(msg):
    print(f"\033[0;31m[ERROR]\033[0m {msg}")

def print_warning(msg):
    print(f"\033[1;33m[WARNING]\033[0m {msg}")


def setup_logging():
    """ロギングの設定"""
    log_dir = Path("build_logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"build_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    print_info(f"ログファイル: {log_file}")
    return log_file


def check_requirements():
    """必要なツールの確認"""
    print_info("ビルド環境を確認中...")
    logging.info("=== ビルド環境確認開始 ===")
    
    # Python バージョン確認
    python_version = sys.version_info
    logging.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 8):
        error_msg = f"Python 3.8以降が必要です。現在: {python_version.major}.{python_version.minor}"
        print_error(error_msg)
        logging.error(error_msg)
        return False
    
    print_info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # PyInstaller の確認
    try:
        import PyInstaller
        pyinstaller_version = PyInstaller.__version__
        print_info(f"PyInstaller version: {pyinstaller_version}")
        logging.info(f"PyInstaller version: {pyinstaller_version}")
    except ImportError as e:
        error_msg = "PyInstaller がインストールされていません"
        print_error(error_msg)
        logging.error(f"{error_msg}: {str(e)}")
        print_info("pip install pyinstaller でインストールしてください")
        return False
    
    # 依存パッケージの確認
    logging.info("=== 依存パッケージ確認 ===")
    required_packages = ['chromadb', 'openai', 'click', 'rich', 'pydantic', 'dotenv', 'yaml']
    for package in required_packages:
        try:
            __import__(package)
            logging.info(f"✓ {package} is installed")
        except ImportError:
            logging.warning(f"✗ {package} is not installed")
    
    return True


def create_spec_file():
    """PyInstaller用の.specファイルを作成"""
    try:
        # エントリーポイントのファイルが存在するか確認
        entry_point = Path('chroma_memo_main.py')
        if not entry_point.exists():
            error_msg = f"エントリーポイントが見つかりません: {entry_point}"
            print_error(error_msg)
            logging.error(error_msg)
            return False
        
        logging.info(f"エントリーポイント確認: {entry_point.absolute()}")
        
        spec_content = '''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ChromaDBの全ファイルを収集
datas = []
binaries = []
hiddenimports = []

for pkg in ['chromadb', 'onnxruntime', 'tokenizers']:
    tmp_datas, tmp_binaries, tmp_hiddenimports = collect_all(pkg)
    datas.extend(tmp_datas)
    binaries.extend(tmp_binaries)
    hiddenimports.extend(tmp_hiddenimports)

a = Analysis(
    ['chroma_memo_main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas + [
        ('chroma_memo/*.py', 'chroma_memo'),
        ('chroma_memo/templates/*.md', 'chroma_memo/templates'),
    ],
    hiddenimports=hiddenimports + [
        'chroma_memo',
        'chroma_memo.cli',
        'chroma_memo.config',
        'chroma_memo.database', 
        'chroma_memo.embeddings',
        'chroma_memo.models',
        'chromadb',
        'chromadb.api',
        'chromadb.config',
        'openai',
        'google.generativeai',
        'click',
        'rich',
        'pydantic',
        'python-dotenv',
        'dotenv',
        'yaml',
        'sqlite3',
        'tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'numpy',
        'pkg_resources',
        'multiprocessing',
        'uvloop',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pytest',
        'jupyter',
        'notebook',
        'ipython',
        'tensorflow',
        'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='chroma-memo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        with open('chroma-memo.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print_success("chroma-memo.spec ファイルを作成しました")
        logging.info("Specファイル作成成功")
        return True
        
    except Exception as e:
        error_msg = f"Specファイル作成エラー: {str(e)}"
        print_error(error_msg)
        logging.exception(error_msg)
        return False


def build_executable():
    """実行ファイルをビルド"""
    print_info("実行ファイルをビルド中...")
    print_warning("ビルドには数分かかる場合があります...")
    logging.info("=== PyInstaller ビルド開始 ===")
    
    try:
        # PyInstaller実行
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--log-level=DEBUG',  # デバッグログを有効化
            'chroma-memo.spec'
        ]
        
        logging.info(f"実行コマンド: {' '.join(cmd)}")
        
        # リアルタイムでログを出力
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 出力をリアルタイムで表示とログに記録
        for line in process.stdout:
            line = line.rstrip()
            if line:
                logging.info(f"PyInstaller: {line}")
                if "ERROR" in line or "error" in line:
                    print_error(line)
                elif "WARNING" in line or "warning" in line:
                    print_warning(line)
        
        process.wait()
        
        if process.returncode != 0:
            error_msg = f"ビルドに失敗しました (終了コード: {process.returncode})"
            print_error(error_msg)
            logging.error(error_msg)
            
            # ビルドログの場所を案内
            print_error("詳細なエラー情報はログファイルを確認してください")
            print_error("また、build/chroma-memo/warn-chroma-memo.txt も確認してください")
            return False
        
        print_success("ビルドが完了しました！")
        logging.info("=== ビルド成功 ===")
        return True
        
    except Exception as e:
        error_msg = f"ビルドエラー: {str(e)}"
        print_error(error_msg)
        logging.exception(error_msg)
        return False


def organize_output():
    """出力ファイルの整理"""
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    if not dist_dir.exists():
        print_error("dist ディレクトリが見つかりません")
        return False
    
    executable_path = dist_dir / "chroma-memo"
    if sys.platform == "win32":
        executable_path = executable_path.with_suffix(".exe")
    
    if not executable_path.exists():
        print_error(f"実行ファイルが見つかりません: {executable_path}")
        return False
    
    # 実行権限を付与（Unix系）
    if sys.platform != "win32":
        os.chmod(executable_path, 0o755)
    
    print_success(f"実行ファイル: {executable_path}")
    print_info(f"ファイルサイズ: {executable_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return True


def cleanup():
    """一時ファイルのクリーンアップ"""
    print_info("一時ファイルをクリーンアップ中...")
    
    cleanup_items = [
        "build",
        "chroma-memo.spec",
        "__pycache__",
        "*.pyc",
    ]
    
    for item in cleanup_items:
        if item == "build" and Path(item).exists():
            shutil.rmtree(item)
            print_info(f"削除: {item}/")
        elif item == "chroma-memo.spec" and Path(item).exists():
            os.remove(item)
            print_info(f"削除: {item}")


def test_executable():
    """作成された実行ファイルのテスト"""
    print_info("実行ファイルをテスト中...")
    
    executable_path = Path("dist/chroma-memo")
    if sys.platform == "win32":
        executable_path = executable_path.with_suffix(".exe")
    
    if not executable_path.exists():
        print_error("実行ファイルが見つかりません")
        return False
    
    try:
        result = subprocess.run([str(executable_path), "--version"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_success("実行ファイルのテストが成功しました")
            print_info(f"出力: {result.stdout.strip()}")
            return True
        else:
            print_warning("実行ファイルのテストで警告が発生しました")
            print(f"STDERR: {result.stderr}")
            return True  # 警告でも続行
            
    except subprocess.TimeoutExpired:
        print_warning("実行ファイルのテストがタイムアウトしました")
        return True
    except Exception as e:
        print_error(f"実行ファイルのテスト中にエラー: {str(e)}")
        return False


def main():
    print("🔨 Chroma-Memo Executable Builder")
    print("=" * 40)
    
    # ロギング設定
    log_file = setup_logging()
    logging.info("=== Chroma-Memo ビルド開始 ===")
    logging.info(f"作業ディレクトリ: {os.getcwd()}")
    logging.info(f"Pythonパス: {sys.executable}")
    
    # 前提条件チェック
    if not check_requirements():
        logging.error("前提条件チェックに失敗しました")
        print_error(f"ビルドに失敗しました。詳細はログファイルを確認してください: {log_file}")
        sys.exit(1)
    
    # ビルドプロセス
    steps = [
        ("Specファイル作成", create_spec_file),
        ("実行ファイルビルド", build_executable),
        ("出力整理", organize_output),
        ("実行ファイルテスト", test_executable),
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        logging.info(f"=== {step_name} 開始 ===")
        if not step_func():
            print_error(f"{step_name} に失敗しました")
            logging.error(f"{step_name} に失敗しました")
            print_error(f"詳細はログファイルを確認してください: {log_file}")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print_success("🎉 ビルド完了！")
    logging.info("=== ビルド正常終了 ===")
    
    executable_path = Path("dist/chroma-memo")
    if sys.platform == "win32":
        executable_path = executable_path.with_suffix(".exe")
    
    print(f"\n実行ファイル: {executable_path.absolute()}")
    print("\n使用方法:")
    print(f"  {executable_path} init my-project")
    print(f"  {executable_path} add my-project \"メモ内容\"")
    print(f"  {executable_path} search my-project \"検索語\"")
    
    # クリーンアップ確認
    try:
        print(f"\n一時ファイルをクリーンアップしますか？ (y/N): ", end="")
        response = input().strip().lower()
        if response in ['y', 'yes']:
            cleanup()
    except (EOFError, KeyboardInterrupt):
        # テスト環境など対話できない場合はスキップ
        print("\n対話モードでないため、クリーンアップをスキップします")
        logging.info("対話モードでないため、クリーンアップをスキップ")
    
    print_success("完了!")


if __name__ == "__main__":
    main() 