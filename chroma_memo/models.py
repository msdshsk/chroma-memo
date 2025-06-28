"""
Data models for Chroma-Memo
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SourceType(str, Enum):
    """Source type for knowledge entries"""
    MANUAL = "manual"
    IMPORT = "import"
    API = "api"


class KnowledgeEntry(BaseModel):
    """Model for a knowledge entry"""
    id: str = Field(..., description="Unique identifier")
    content: str = Field(..., description="Knowledge content")
    project: str = Field(..., description="Project name")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    source: SourceType = Field(default=SourceType.MANUAL, description="Source of the entry")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_chroma_metadata(self) -> Dict[str, Any]:
        """Convert to ChromaDB metadata format"""
        return {
            "project": self.project,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": ",".join(self.tags) if self.tags else "",
            "source": self.source.value,
            **self.metadata
        }

    @classmethod
    def from_chroma_result(cls, doc_id: str, content: str, metadata: Dict[str, Any]) -> "KnowledgeEntry":
        """Create KnowledgeEntry from ChromaDB result"""
        return cls(
            id=doc_id,
            content=content,
            project=metadata.get("project", ""),
            created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(metadata.get("updated_at", datetime.now().isoformat())),
            tags=metadata.get("tags", "").split(",") if metadata.get("tags") else [],
            source=SourceType(metadata.get("source", SourceType.MANUAL.value)),
            metadata={k: v for k, v in metadata.items() 
                     if k not in ["project", "created_at", "updated_at", "tags", "source"]}
        )


class ProjectInfo(BaseModel):
    """Model for project information"""
    name: str = Field(..., description="Project name")
    total_entries: int = Field(default=0, description="Total number of entries")
    created_at: datetime = Field(default_factory=datetime.now, description="Project creation timestamp")
    last_updated: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    
class SearchResult(BaseModel):
    """Model for search results"""
    entry: KnowledgeEntry
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    rank: int = Field(..., description="Rank in search results")


class AppConfig(BaseModel):
    """Application configuration model"""
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    embedding_provider: str = Field(default="openai", description="Embedding provider")
    api_key_env: str = Field(default="OPENAI_API_KEY", description="Environment variable for API key")
    db_path: str = Field(default="~/.chroma-memo/db", description="ChromaDB path")
    config_path: str = Field(default="~/.chroma-memo/config.yaml", description="Config file path")
    max_results: int = Field(default=10, description="Maximum search results")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold for searches")
    export_formats: List[str] = Field(default=["json", "csv", "markdown"], description="Supported export formats") 