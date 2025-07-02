"""
ChromaDB database operations for Chroma-Memo
"""
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings

from .models import KnowledgeEntry, SearchResult, ProjectInfo
from .embeddings import embedding_service
from .config import config_manager


class ChromaMemoDatabase:
    """ChromaDB database manager for Chroma-Memo"""
    
    def __init__(self):
        self.config = config_manager.load_config()
        self.db_path = config_manager.get_db_path()
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        # テレメトリを確実に無効化
        import os
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        try:
            # 最小限の設定でクライアントを初期化
            self.client = chromadb.PersistentClient(path=str(self.db_path))
        except Exception as e:
            # エラーをログに出力
            import sys
            print(f"⚠️  ChromaDB PersistentClient initialization failed: {e}", file=sys.stderr)
            print(f"📂 Attempted path: {self.db_path}", file=sys.stderr)
            # デフォルトのクライアントを使用
            self.client = chromadb.Client()
    
    def _get_collection_name(self, project_name: str) -> str:
        """Get collection name for a project"""
        return f"project_{project_name.lower().replace('-', '_').replace(' ', '_')}"
    
    def create_project(self, project_name: str) -> bool:
        """Create a new project (collection)"""
        try:
            collection_name = self._get_collection_name(project_name)
            
            # Try to get or create collection
            try:
                collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"project_name": project_name, "created_at": datetime.now().isoformat()}
                )
                # Check if it was already existing by trying to get its count
                try:
                    count = collection.count()
                    if count == 0:
                        return True  # New empty collection
                    else:
                        return False  # Collection already had data
                except:
                    return True  # Assume it's new if we can't check count
            except Exception as e:
                # Fallback: try create_collection directly
                self.client.create_collection(
                    name=collection_name,
                    metadata={"project_name": project_name, "created_at": datetime.now().isoformat()}
                )
                return True
        except Exception as e:
            raise RuntimeError(f"Failed to create project '{project_name}': {str(e)}")
    
    def project_exists(self, project_name: str) -> bool:
        """Check if a project exists"""
        import sys
        try:
            collection_name = self._get_collection_name(project_name)
            print(f"🔍 Checking if project exists: '{project_name}' -> collection: '{collection_name}'", file=sys.stderr)
            self.client.get_collection(collection_name)
            print(f"✅ Project '{project_name}' exists", file=sys.stderr)
            return True
        except Exception as e:
            # Any exception means the collection doesn't exist
            print(f"📝 Project '{project_name}' does not exist (Exception: {type(e).__name__}: {e})", file=sys.stderr)
            return False
    
    def add_knowledge(self, project_name: str, content: str, tags: Optional[List[str]] = None) -> str:
        """Add knowledge to a project"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist. Create it first with 'init' command.")
        
        try:
            # Generate unique ID
            entry_id = str(uuid.uuid4())
            
            # Create knowledge entry
            entry = KnowledgeEntry(
                id=entry_id,
                content=content,
                project=project_name,
                tags=tags or [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Get embedding
            embedding = embedding_service.get_embedding(content)
            
            # Add to collection (存在しない場合は作成)
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"project_name": project_name, "created_at": datetime.now().isoformat()}
            )
            
            collection.add(
                ids=[entry_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[entry.to_chroma_metadata()]
            )
            
            return entry_id
        except Exception as e:
            raise RuntimeError(f"Failed to add knowledge to project '{project_name}': {str(e)}")
    
    def search_knowledge(self, project_name: str, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Search knowledge in a project"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            max_results = max_results or self.config.max_results
            
            # Get query embedding
            query_embedding = embedding_service.get_embedding(query)
            
            # Search in collection
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_collection(collection_name)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results
            )
            
            # Convert to SearchResult objects
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, (doc_id, content, metadata, distance) in enumerate(zip(
                    results['ids'][0],
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses cosine distance)
                    similarity_score = 1.0 - distance
                    
                    # Skip results below threshold
                    if similarity_score < self.config.similarity_threshold:
                        continue
                    
                    entry = KnowledgeEntry.from_chroma_result(doc_id, content, metadata)
                    search_results.append(SearchResult(
                        entry=entry,
                        similarity_score=similarity_score,
                        rank=i + 1
                    ))
            
            return search_results
        except Exception as e:
            raise RuntimeError(f"Failed to search in project '{project_name}': {str(e)}")
    
    def get_knowledge_by_id(self, project_name: str, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a specific knowledge entry by ID (supports partial ID)"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_collection(collection_name)
            
            # First try exact match
            results = collection.get(ids=[entry_id])
            
            if results['ids'] and results['ids'][0]:
                # Exact match found
                doc_id = results['ids'][0]
                content = results['documents'][0]
                metadata = results['metadatas'][0]
                return KnowledgeEntry.from_chroma_result(doc_id, content, metadata)
            
            # If not found and entry_id is short (partial ID), search through all entries
            if len(entry_id) < 36:  # UUID is 36 chars
                all_results = collection.get()
                if all_results['ids']:
                    # Find entries that start with the partial ID
                    matching_entries = []
                    for i, doc_id in enumerate(all_results['ids']):
                        if doc_id.startswith(entry_id):
                            matching_entries.append(i)
                    
                    if len(matching_entries) == 1:
                        # Exactly one match found
                        idx = matching_entries[0]
                        return KnowledgeEntry.from_chroma_result(
                            all_results['ids'][idx],
                            all_results['documents'][idx],
                            all_results['metadatas'][idx]
                        )
                    elif len(matching_entries) > 1:
                        # Multiple matches found
                        raise ValueError(f"Multiple entries found starting with '{entry_id}'. Please provide more characters.")
            
            return None  # Entry doesn't exist
            
        except ValueError:
            raise  # Re-raise ValueError for multiple matches
        except Exception as e:
            raise RuntimeError(f"Failed to get knowledge from project '{project_name}': {str(e)}")

    def delete_knowledge(self, project_name: str, entry_id: str) -> bool:
        """Delete knowledge from a project"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_collection(collection_name)
            
            # Check if entry exists
            try:
                results = collection.get(ids=[entry_id])
                if not results['ids']:
                    return False  # Entry doesn't exist
            except Exception:
                return False
            
            # Delete the entry
            collection.delete(ids=[entry_id])
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete knowledge from project '{project_name}': {str(e)}")
    
    def list_knowledge(self, project_name: str) -> List[KnowledgeEntry]:
        """List all knowledge in a project"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_collection(collection_name)
            
            # Get all entries
            results = collection.get()
            
            entries = []
            if results['ids']:
                for doc_id, content, metadata in zip(
                    results['ids'],
                    results['documents'],
                    results['metadatas']
                ):
                    entry = KnowledgeEntry.from_chroma_result(doc_id, content, metadata)
                    entries.append(entry)
            
            # Sort by creation date (newest first)
            entries.sort(key=lambda x: x.created_at, reverse=True)
            return entries
        except Exception as e:
            raise RuntimeError(f"Failed to list knowledge in project '{project_name}': {str(e)}")
    
    def get_project_info(self, project_name: str) -> ProjectInfo:
        """Get project information"""
        if not self.project_exists(project_name):
            raise ValueError(f"Project '{project_name}' does not exist.")
        
        try:
            collection_name = self._get_collection_name(project_name)
            collection = self.client.get_collection(collection_name)
            
            # Get collection metadata
            collection_metadata = collection.metadata or {}
            
            # Count entries
            results = collection.get()
            total_entries = len(results['ids']) if results['ids'] else 0
            
            # Get creation date from metadata
            created_at_str = collection_metadata.get('created_at')
            created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
            
            # Get last updated (from most recent entry)
            last_updated = None
            if total_entries > 0:
                entries = self.list_knowledge(project_name)
                if entries:
                    last_updated = max(entry.updated_at for entry in entries)
            
            return ProjectInfo(
                name=project_name,
                total_entries=total_entries,
                created_at=created_at,
                last_updated=last_updated
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get info for project '{project_name}': {str(e)}")
    
    def list_projects(self) -> List[ProjectInfo]:
        """List all projects"""
        try:
            collections = self.client.list_collections()
            projects = []
            
            for collection in collections:
                if collection.name.startswith("project_"):
                    # Extract project name from collection name
                    project_name = collection.metadata.get('project_name', collection.name[8:])
                    try:
                        project_info = self.get_project_info(project_name)
                        projects.append(project_info)
                    except Exception:
                        # Skip collections that can't be processed
                        continue
            
            # Sort by creation date (newest first)
            projects.sort(key=lambda x: x.created_at, reverse=True)
            return projects
        except Exception as e:
            raise RuntimeError(f"Failed to list projects: {str(e)}")


# Global database instance (遅延初期化)
_database_instance = None

def get_database():
    """データベースインスタンスを取得（遅延初期化）"""
    global _database_instance
    if _database_instance is None:
        _database_instance = ChromaMemoDatabase()
    return _database_instance

# Proxyクラスでdatabaseオブジェクトをエミュレート
class DatabaseProxy:
    def __getattr__(self, name):
        return getattr(get_database(), name)

database = DatabaseProxy() 