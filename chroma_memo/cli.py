"""
CLI interface for Chroma-Memo
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List
import os
import shutil
import sys
from pathlib import Path
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

from .database import database
from .models import SearchResult, ProjectInfo, KnowledgeEntry
from .config import config_manager

console = Console()


def _copy_claude_commands_template(project_name: str):
    """Claude Code用のcommandsテンプレートをコピー"""
    try:
        # カレントディレクトリに.claudeディレクトリを作成
        claude_dir = os.path.join(os.getcwd(), '.claude')
        commands_dir = os.path.join(claude_dir, 'commands')
        
        os.makedirs(commands_dir, exist_ok=True)
        
        # テンプレートファイルをコピー
        _copy_template_files(commands_dir, project_name)
        console.print(f"✅ Claude Commandsテンプレートを {commands_dir} に作成しました。", style="green")
            
    except Exception as e:
        console.print(f"⚠️  Claude Commandsテンプレートのコピーに失敗しました: {str(e)}", style="yellow")


def _copy_template_files(commands_dir: str, project_name: str):
    """パッケージからテンプレートファイルをコピーして、project_nameを置換"""
    template_files = [
        'memo-add.md',
        'memo-search.md', 
        'project-info.md',
        'memo-maintenance.md'
    ]
    
    try:
        success_count = 0
        for template_file in template_files:
            template_content = None
            
            # 複数の方法でテンプレートファイルを読み込み試行
            try:
                # Method 1: importlib.resources.read_text (Python 3.9+)
                template_content = resources.read_text('chroma_memo.templates', template_file)
            except Exception:
                try:
                    # Method 2: importlib.resources.path (Python 3.7+)
                    with resources.path('chroma_memo.templates', template_file) as template_path:
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_content = f.read()
                except Exception:
                    try:
                        # Method 3: pkg_resources fallback
                        import pkg_resources
                        template_path = pkg_resources.resource_filename('chroma_memo', f'templates/{template_file}')
                        with open(template_path, 'r', encoding='utf-8') as f:
                            template_content = f.read()
                    except Exception:
                        # Method 4: Direct file path fallback
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        template_path = os.path.join(current_dir, 'templates', template_file)
                        if os.path.exists(template_path):
                            with open(template_path, 'r', encoding='utf-8') as f:
                                template_content = f.read()
                        else:
                            # Method 5: PyInstaller専用パス
                            if hasattr(sys, '_MEIPASS'):
                                meipass_template_path = os.path.join(sys._MEIPASS, 'chroma_memo', 'templates', template_file)
                                if os.path.exists(meipass_template_path):
                                    with open(meipass_template_path, 'r', encoding='utf-8') as f:
                                        template_content = f.read()
            
            if template_content:
                # project_nameを置換
                processed_content = template_content.replace('{project_name}', project_name)
                
                # ファイルに書き込み
                output_path = os.path.join(commands_dir, template_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                success_count += 1
                
        if success_count == 0:
            raise Exception("テンプレートファイルが見つかりませんでした")
        elif success_count < len(template_files):
            console.print(f"⚠️  一部のテンプレートファイルの読み込みに失敗しました ({success_count}/{len(template_files)})", style="yellow")
                
    except Exception as e:
        console.print(f"⚠️  テンプレートファイルの読み込みに失敗しました: {str(e)}", style="yellow")
        # フォールバック: 基本的なテンプレートを作成
        _create_fallback_templates(commands_dir, project_name)


def _create_fallback_templates(commands_dir: str, project_name: str):
    """テンプレートファイルが見つからない場合のフォールバック"""
    console.print("フォールバックテンプレートを作成しています...", style="yellow")
    
    fallback_content = f"""# Chroma-Memo Commands

## Add Knowledge
```bash
chroma-memo add {project_name} "$ARGUMENTS"
```

## Search Knowledge  
```bash
chroma-memo search {project_name} "$ARGUMENTS"
```

## List Knowledge
```bash
chroma-memo list {project_name}
```

## Delete Knowledge
```bash
chroma-memo del {project_name} "$ARGUMENTS" --confirm
```
"""
    
    fallback_path = os.path.join(commands_dir, 'chroma-memo-commands.md')
    with open(fallback_path, 'w', encoding='utf-8') as f:
        f.write(fallback_content)


@click.group()
@click.version_option(version="0.1.0", prog_name="chroma-memo")
def main():
    """Chroma-Memo: Project-specific knowledge base using ChromaDB and OpenAI embeddings"""
    pass


@main.command()
@click.argument('project_name')
@click.option('--with-claude-command', is_flag=True, help='Claude Code用のcommandsテンプレートをコピー')
def init(project_name: str, with_claude_command: bool):
    """プロジェクト専用のDBを新規作成"""
    try:
        if database.create_project(project_name):
            console.print(f"✅ プロジェクト '{project_name}' を作成しました。", style="green")
        else:
            console.print(f"⚠️  プロジェクト '{project_name}' は既に存在します。", style="yellow")
    except Exception as e:
        console.print(f"❌ プロジェクト作成エラー: {str(e)}", style="red")
        if not with_claude_command:
            raise click.ClickException(str(e))
    
    # Claude Command テンプレートをコピー（プロジェクト作成の成否に関わらず実行）
    if with_claude_command:
        _copy_claude_commands_template(project_name)


@main.command()
@click.argument('project_name')
@click.argument('message')
@click.option('--tags', '-t', multiple=True, help='ナレッジにタグを追加')
def add(project_name: str, message: str, tags: tuple):
    """ナレッジをDBに追加"""
    try:
        tags_list = list(tags) if tags else None
        entry_id = database.add_knowledge(project_name, message, tags_list)
        
        console.print(f"✅ ナレッジを追加しました", style="green")
        console.print(f"ID: {entry_id}")
        if tags_list:
            console.print(f"タグ: {', '.join(tags_list)}")
    except Exception as e:
        console.print(f"❌ ナレッジ追加エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command()
@click.argument('project_name')
@click.argument('query')
@click.option('--max-results', '-n', default=None, type=int, help='最大検索結果数')
def search(project_name: str, query: str, max_results: int):
    """クエリでDBを検索"""
    try:
        results = database.search_knowledge(project_name, query, max_results)
        
        if not results:
            console.print("🔍 該当するナレッジが見つかりませんでした。", style="yellow")
            return
        
        console.print(f"🔍 検索結果: {len(results)}件", style="blue")
        console.print()
        
        for result in results:
            # Create panel for each result
            content_text = Text(result.entry.content)
            similarity_text = Text(f"類似度: {result.similarity_score:.3f}", style="dim")
            id_text = Text(f"ID: {result.entry.id}", style="dim")
            created_text = Text(f"作成: {result.entry.created_at.strftime('%Y-%m-%d %H:%M')}", style="dim")
            
            header = f"#{result.rank}"
            if result.entry.tags:
                header += f" [タグ: {', '.join(result.entry.tags)}]"
            
            panel_content = f"{content_text}\n\n{similarity_text} | {id_text} | {created_text}"
            
            console.print(Panel(
                panel_content,
                title=header,
                title_align="left",
                border_style="blue" if result.similarity_score >= 0.9 else "green" if result.similarity_score >= 0.8 else "yellow"
            ))
            
    except Exception as e:
        console.print(f"❌ 検索エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command(name='del')
@click.argument('project_name')
@click.argument('entry_id')
@click.option('--confirm', '-y', is_flag=True, help='確認をスキップ')
def delete(project_name: str, entry_id: str, confirm: bool):
    """指定IDのナレッジを削除"""
    try:
        if not confirm:
            if not click.confirm(f"ID '{entry_id}' のナレッジを削除しますか？"):
                console.print("削除をキャンセルしました。", style="yellow")
                return
        
        if database.delete_knowledge(project_name, entry_id):
            console.print(f"✅ ナレッジ (ID: {entry_id}) を削除しました。", style="green")
        else:
            console.print(f"⚠️  指定されたID '{entry_id}' のナレッジが見つかりませんでした。", style="yellow")
    except Exception as e:
        console.print(f"❌ 削除エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command()
@click.argument('project_name')
def list(project_name: str):
    """プロジェクトの全ナレッジを一覧表示"""
    try:
        entries = database.list_knowledge(project_name)
        
        if not entries:
            console.print(f"📝 プロジェクト '{project_name}' にナレッジがありません。", style="yellow")
            return
        
        console.print(f"📝 プロジェクト '{project_name}' のナレッジ一覧: {len(entries)}件", style="blue")
        console.print()
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="dim", width=8)
        table.add_column("内容", min_width=30)
        table.add_column("タグ", style="cyan")
        table.add_column("作成日時", style="dim")
        
        for entry in entries:
            content_preview = entry.content[:50] + "..." if len(entry.content) > 50 else entry.content
            tags_str = ", ".join(entry.tags) if entry.tags else "-"
            created_str = entry.created_at.strftime('%m-%d %H:%M')
            
            table.add_row(
                entry.id[:8],
                content_preview,
                tags_str,
                created_str
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ 一覧取得エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command()
def projects():
    """全プロジェクトの一覧表示"""
    try:
        project_list = database.list_projects()
        
        if not project_list:
            console.print("📁 プロジェクトがありません。", style="yellow")
            console.print("新しいプロジェクトを作成するには: chroma-memo init <project_name>")
            return
        
        console.print(f"📁 プロジェクト一覧: {len(project_list)}件", style="blue")
        console.print()
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("プロジェクト名", style="bold")
        table.add_column("エントリ数", justify="right")
        table.add_column("作成日", style="dim")
        table.add_column("最終更新", style="dim")
        
        for project in project_list:
            created_str = project.created_at.strftime('%Y-%m-%d')
            updated_str = project.last_updated.strftime('%Y-%m-%d') if project.last_updated else "-"
            
            table.add_row(
                project.name,
                str(project.total_entries),
                created_str,
                updated_str
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ プロジェクト一覧取得エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command()
@click.argument('project_name')
def info(project_name: str):
    """プロジェクトの統計・詳細情報"""
    try:
        project_info = database.get_project_info(project_name)
        
        console.print(f"📊 プロジェクト情報: {project_name}", style="bold blue")
        console.print()
        
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("項目", style="bold")
        info_table.add_column("値")
        
        info_table.add_row("プロジェクト名", project_info.name)
        info_table.add_row("総エントリ数", str(project_info.total_entries))
        info_table.add_row("作成日時", project_info.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        if project_info.last_updated:
            info_table.add_row("最終更新", project_info.last_updated.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            info_table.add_row("最終更新", "-")
        
        console.print(Panel(info_table, title="プロジェクト詳細", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ プロジェクト情報取得エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


@main.command()
@click.option('--set-api-key', type=click.Choice(['openai']), help='APIキーを設定')
@click.option('--show-env-path', is_flag=True, help='.envファイルのパスを表示')
@click.option('--show-db-path', is_flag=True, help='データベースパスを表示')
@click.option('--show-all-paths', is_flag=True, help='全てのパスを表示')
def config(set_api_key: str, show_env_path: bool, show_db_path: bool, show_all_paths: bool):
    """設定管理"""
    try:
        if set_api_key == 'openai':
            api_key = click.prompt('OpenAI APIキーを入力してください', hide_input=True)
            config_manager.set_api_key(api_key)
            env_path = config_manager.get_env_file_path()
            console.print("✅ APIキーを設定しました:", style="green")
            console.print(f"保存先: {env_path}")
            return
        
        if show_env_path:
            env_path = config_manager.get_env_file_path()
            console.print(f"📄 .envファイルのパス: {env_path}", style="blue")
            if env_path.exists():
                console.print("✅ .envファイルが存在します", style="green")
            else:
                console.print("⚠️  .envファイルが存在しません", style="yellow")
            return
        
        if show_db_path:
            db_path = config_manager.get_db_path()
            console.print(f"🗄️  データベースパス: {db_path}", style="blue")
            if db_path.exists():
                console.print("✅ データベースディレクトリが存在します", style="green")
                # DB内のプロジェクト数を表示
                try:
                    project_list = database.list_projects()
                    console.print(f"📊 保存されているプロジェクト数: {len(project_list)}", style="cyan")
                except Exception:
                    console.print("⚠️  データベースの読み込みに失敗しました", style="yellow")
            else:
                console.print("⚠️  データベースディレクトリが存在しません", style="yellow")
            return
        
        if show_all_paths:
            current_config = config_manager.load_config()
            env_path = config_manager.get_env_file_path()
            db_path = config_manager.get_db_path()
            
            console.print("📂 Chroma-Memo ファイル・ディレクトリ一覧:", style="bold blue")
            console.print()
            
            paths_table = Table(show_header=True, header_style="bold blue")
            paths_table.add_column("項目", style="bold")
            paths_table.add_column("パス", min_width=40)
            paths_table.add_column("状態", justify="center")
            
            # 設定ファイル
            config_exists = "✅" if config_manager.config_path.exists() else "❌"
            paths_table.add_row("設定ファイル", str(config_manager.config_path), config_exists)
            
            # .envファイル
            env_exists = "✅" if env_path.exists() else "❌"
            paths_table.add_row(".envファイル", str(env_path), env_exists)
            
            # データベース
            db_exists = "✅" if db_path.exists() else "❌"
            paths_table.add_row("データベース", str(db_path), db_exists)
            
            console.print(paths_table)
            
            # プロジェクト情報
            try:
                project_list = database.list_projects()
                console.print(f"\n📊 保存されているプロジェクト: {len(project_list)}個")
                if project_list:
                    for project in project_list[:5]:  # 最大5個まで表示
                        console.print(f"  - {project.name} ({project.total_entries}件)")
                    if len(project_list) > 5:
                        console.print(f"  ... および他{len(project_list) - 5}個")
            except Exception:
                console.print("\n⚠️  プロジェクト情報の取得に失敗しました", style="yellow")
            return
        
        # Show current configuration
        current_config = config_manager.load_config()
        
        console.print("⚙️  現在の設定:", style="bold blue")
        console.print()
        
        config_table = Table(show_header=False, box=None, padding=(0, 2))
        config_table.add_column("設定項目", style="bold")
        config_table.add_column("値")
        
        config_table.add_row("埋め込みモデル", current_config.embedding_model)
        config_table.add_row("プロバイダー", current_config.embedding_provider)
        config_table.add_row("DB パス", current_config.db_path)
        config_table.add_row("最大検索結果数", str(current_config.max_results))
        config_table.add_row("類似度閾値", str(current_config.similarity_threshold))
        
        console.print(Panel(config_table, title="設定情報", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ 設定エラー: {str(e)}", style="red")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main() 