"""
Embedding utilities for Chroma-Memo
"""
import os
import openai
from typing import List, Union
from .config import config_manager


class EmbeddingService:
    """Service for generating embeddings using OpenAI or Google"""
    
    def __init__(self):
        self.config = config_manager.load_config()
        self.use_api = os.getenv("USE_API", "OPENAI").upper()
        self._client = None
        self._initialized = False
        
        if self.use_api == "GOOGLE":
            self.google_model = "text-embedding-004"
    
    def _ensure_initialized(self):
        """遅延初期化 - 実際に使用する時にAPIキーをチェック"""
        if self._initialized:
            return
            
        if self.use_api == "GOOGLE":
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "\n"
                    "Google API キーが設定されていません。\n"
                    "設定方法:\n"
                    "1. 環境変数: export GOOGLE_API_KEY='your_api_key'\n" 
                    "2. .envファイル: ~/.chroma-memo/.env に GOOGLE_API_KEY=your_api_key を追加"
                )
            genai.configure(api_key=api_key)
        else:  # OpenAI
            try:
                api_key = config_manager.get_api_key()
                self._client = openai.OpenAI(api_key=api_key)
            except ValueError as e:
                # より親切なエラーメッセージに置き換え
                raise ValueError(
                    "\n"
                    "OpenAI API キーが設定されていません。\n"
                    "設定方法:\n"
                    "1. 環境変数: export OPENAI_API_KEY='your_api_key'\n"
                    "2. .envファイル: ~/.chroma-memo/.env に OPENAI_API_KEY=your_api_key を追加\n"
                    "3. 設定コマンド: chroma-memo config --set-api-key openai"
                ) from None
        
        self._initialized = True
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        # APIキーの初期化を確認
        self._ensure_initialized()
        
        try:
            # テスト用ダミーキーの場合はダミーの埋め込みを返す
            if self.use_api == "GOOGLE" and os.getenv("GOOGLE_API_KEY", "").startswith("test-"):
                return [0.1] * 768  # Google embedding dimension
            elif self.use_api == "OPENAI" and os.getenv("OPENAI_API_KEY", "").startswith("test-"):
                return [0.1] * self.get_embedding_dimension()  # OpenAI embedding dimension
            
            if self.use_api == "GOOGLE":
                import google.generativeai as genai
                result = genai.embed_content(
                    model=f"models/{self.google_model}",
                    content=text
                )
                return result['embedding']
            else:  # OpenAI
                assert self._client is not None, "OpenAI client should be initialized"
                response = self._client.embeddings.create(
                    model=self.config.embedding_model,
                    input=text,
                    encoding_format="float"
                )
                return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to get embedding: {str(e)}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        # APIキーの初期化を確認
        self._ensure_initialized()
        
        try:
            # テスト用ダミーキーの場合はダミーの埋め込みを返す
            if self.use_api == "GOOGLE" and os.getenv("GOOGLE_API_KEY", "").startswith("test-"):
                return [[0.1] * 768 for _ in texts]  # Google embedding dimension
            elif self.use_api == "OPENAI" and os.getenv("OPENAI_API_KEY", "").startswith("test-"):
                return [[0.1] * self.get_embedding_dimension() for _ in texts]  # OpenAI embedding dimension
            
            if self.use_api == "GOOGLE":
                import google.generativeai as genai
                results = []
                for text in texts:
                    result = genai.embed_content(
                        model=f"models/{self.google_model}",
                        content=text
                    )
                    results.append(result['embedding'])
                return results
            else:  # OpenAI
                assert self._client is not None, "OpenAI client should be initialized"
                response = self._client.embeddings.create(
                    model=self.config.embedding_model,
                    input=texts,
                    encoding_format="float"
                )
                return [item.embedding for item in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to get embeddings: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model"""
        if self.use_api == "GOOGLE":
            # Google's text-embedding-004 has 768 dimensions
            return 768
        else:  # OpenAI
            # text-embedding-3-small has 1536 dimensions
            model_dimensions = {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "text-embedding-ada-002": 1536,
            }
            return model_dimensions.get(self.config.embedding_model, 1536)


# Global embedding service instance
embedding_service = EmbeddingService() 