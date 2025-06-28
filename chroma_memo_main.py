#!/usr/bin/env python3
"""
Chroma-Memo main entry point for PyInstaller
"""

import os
import warnings

# ChromaDBのテレメトリを無効化（複数の方法で確実に）
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["CHROMA_SERVER_AUTHN_CREDENTIALS_FILE"] = ""
os.environ["CHROMA_SERVER_AUTHN_PROVIDER"] = ""

# ChromaDBの警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module="chromadb")
warnings.filterwarnings("ignore", message=".*telemetry.*")
warnings.filterwarnings("ignore", message=".*capture.*")

# posthogのテレメトリも無効化
try:
    import posthog
    posthog.disabled = True
except ImportError:
    pass

if __name__ == "__main__":
    import sys
    import io
    import contextlib
    
    # テレメトリエラーを抑制するため、stderrをフィルタリング
    class FilteredStderr:
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            
        def write(self, text):
            # テレメトリ関連のエラーは表示しない
            if text and ('telemetry' in text.lower() or 'capture()' in text):
                return
            self.original_stderr.write(text)
            
        def flush(self):
            self.original_stderr.flush()
            
        def __getattr__(self, name):
            return getattr(self.original_stderr, name)
    
    # stderrを一時的に置き換え
    original_stderr = sys.stderr
    sys.stderr = FilteredStderr(original_stderr)
    
    try:
        from chroma_memo.cli import main
        main()
    except ValueError as e:
        # APIキー設定エラーなどをユーザーフレンドリーに表示
        print(f"設定エラー: {e}", file=original_stderr)
        sys.exit(1)
    except Exception as e:
        # その他の予期しないエラー
        print(f"予期しないエラーが発生しました: {e}", file=original_stderr)
        print("詳細なエラー情報については、ログを確認してください。", file=original_stderr)
        sys.exit(1)
    finally:
        # stderrを元に戻す
        sys.stderr = original_stderr