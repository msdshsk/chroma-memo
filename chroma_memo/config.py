"""
Configuration management for Chroma-Memo
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from .models import AppConfig


class ConfigManager:
    """Configuration manager for Chroma-Memo"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path or "~/.chroma-memo/config.yaml").expanduser()
        self.config_dir = self.config_path.parent
        self.env_path = self.config_dir / ".env"
        self._config: Optional[AppConfig] = None
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load environment variables from .env file in config directory
        if self.env_path.exists():
            load_dotenv(self.env_path)
        
        # Also load from current directory .env file if exists
        load_dotenv()
        
    def load_config(self) -> AppConfig:
        """Load configuration from file"""
        if self._config is not None:
            return self._config
            
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}
            
        # Merge with default configuration
        default_config = AppConfig()
        config_dict = default_config.dict()
        
        # Handle nested embedding config
        if 'embedding' in config_data:
            embedding_config = config_data.pop('embedding')
            config_dict.update({
                'embedding_model': embedding_config.get('model', default_config.embedding_model),
                'embedding_provider': embedding_config.get('provider', default_config.embedding_provider),
                'api_key_env': embedding_config.get('api_key_env', default_config.api_key_env),
            })
            
        config_dict.update(config_data)
        self._config = AppConfig(**config_dict)
        return self._config
    
    def save_config(self, config: Optional[AppConfig] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.load_config()
            
        config_data = {
            'embedding': {
                'model': config.embedding_model,
                'provider': config.embedding_provider,
                'api_key_env': config.api_key_env,
            },
            'db_path': config.db_path,
            'max_results': config.max_results,
            'similarity_threshold': config.similarity_threshold,
            'export_formats': config.export_formats,
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
    def get_api_key(self) -> str:
        """Get API key from environment variable"""
        config = self.load_config()
        api_key = os.getenv(config.api_key_env)
        if not api_key:
            env_path = self.get_env_file_path()
            raise ValueError(
                f"API key not found in environment variable: {config.api_key_env}\n"
                f"設定方法:\n"
                f"1. 環境変数: export {config.api_key_env}='your_api_key'\n"
                f"2. .envファイル: {env_path}\n"
                f"3. 設定コマンド: chroma-memo config --set-api-key openai"
            )
        # テスト用ダミーキーの場合はそのまま返す
        if api_key.startswith("test-"):
            return api_key
        return api_key
    
    def get_db_path(self) -> Path:
        """Get database path"""
        config = self.load_config()
        return Path(config.db_path).expanduser()
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values"""
        config = self.load_config()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self._config = config
        self.save_config(config)
    
    def set_api_key(self, api_key: str) -> None:
        """Set API key in .env file"""
        env_content = ""
        
        # Read existing .env file if it exists
        if self.env_path.exists():
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update existing OPENAI_API_KEY line or add new one
            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith('OPENAI_API_KEY='):
                    lines[i] = f'OPENAI_API_KEY={api_key}\n'
                    found = True
                    break
            
            if not found:
                lines.append(f'OPENAI_API_KEY={api_key}\n')
            
            env_content = ''.join(lines)
        else:
            # Create new .env file
            env_content = f"""# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY={api_key}
"""
        
        # Write to .env file
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # Reload environment variables
        load_dotenv(self.env_path, override=True)
    
    def get_env_file_path(self) -> Path:
        """Get path to .env file"""
        return self.env_path


# Global config manager instance
config_manager = ConfigManager() 