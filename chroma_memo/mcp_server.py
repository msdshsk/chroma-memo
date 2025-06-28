#!/usr/bin/env python3
"""MCP Server for Chroma-Memo"""

import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .database import get_database
from .config import config_manager


class ChromaMemoMCPServer:
    """MCP Server wrapper for Chroma-Memo"""
    
    def __init__(self, project_name: str = None):
        self.mcp = FastMCP("chroma-memo")
        self.project_name = project_name
        self.db = get_database()
        self.config = config_manager.load_config()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        @self.mcp.tool()
        def memo_add(project: str, content: str, tags: Optional[List[str]] = None) -> str:
            """Add a new knowledge entry to a project
            
            Args:
                project: Project name
                content: Knowledge content to add
                tags: Optional list of tags
            """
            try:
                # Create project if it doesn't exist
                if not self.db.project_exists(project):
                    self.db.create_project(project)
                
                # Add knowledge to database
                entry_id = self.db.add_knowledge(project, content, tags or [])
                
                return f"✅ Knowledge entry added successfully!\nID: {entry_id}\nProject: {project}\nContent: {content[:100]}{'...' if len(content) > 100 else ''}"
                
            except Exception as e:
                return f"❌ Error adding knowledge entry: {str(e)}"

        @self.mcp.tool()
        def memo_search(project: str, query: str, max_results: int = 5) -> str:
            """Search knowledge entries in a project
            
            Args:
                project: Project name to search in
                query: Search query
                max_results: Maximum number of results (default: 5)
            """
            try:
                # Search in database
                results = self.db.search_knowledge(project, query, max_results)
                
                if not results:
                    return f"🔍 No results found for '{query}' in project '{project}'"
                
                # Format results
                formatted_results = [f"🔍 Search results for '{query}' in '{project}': {len(results)} found\n"]
                
                for i, search_result in enumerate(results, 1):
                    entry = search_result.entry
                    similarity = search_result.similarity_score
                    tags_str = f" [Tags: {', '.join(entry.tags)}]" if entry.tags else ""
                    formatted_results.append(
                        f"\n#{i}{tags_str}\n"
                        f"Content: {entry.content}\n"
                        f"Similarity: {similarity:.3f} | ID: {entry.id} | Created: {entry.created_at}"
                    )
                
                return "\n".join(formatted_results)
                
            except Exception as e:
                return f"❌ Error searching knowledge: {str(e)}"

        @self.mcp.tool()
        def memo_list(project: str) -> str:
            """List all knowledge entries in a project
            
            Args:
                project: Project name
            """
            try:
                entries = self.db.list_knowledge(project)
                
                if not entries:
                    return f"📝 No knowledge entries found in project '{project}'"
                
                formatted_entries = [f"📝 Knowledge entries in '{project}': {len(entries)} found\n"]
                
                for i, entry in enumerate(entries, 1):
                    tags_str = f" [Tags: {', '.join(entry.tags)}]" if entry.tags else ""
                    content_preview = entry.content[:80] + "..." if len(entry.content) > 80 else entry.content
                    formatted_entries.append(
                        f"\n#{i}{tags_str}\n"
                        f"Content: {content_preview}\n"
                        f"ID: {entry.id} | Created: {entry.created_at}"
                    )
                
                return "\n".join(formatted_entries)
                
            except Exception as e:
                return f"❌ Error listing knowledge entries: {str(e)}"

        @self.mcp.tool()
        def memo_delete(project: str, entry_id: str) -> str:
            """Delete a knowledge entry from a project
            
            Args:
                project: Project name
                entry_id: ID of the entry to delete
            """
            try:
                success = self.db.delete_knowledge(project, entry_id)
                
                if success:
                    return f"✅ Knowledge entry {entry_id} deleted successfully from project '{project}'"
                else:
                    return f"❌ Knowledge entry {entry_id} not found in project '{project}'"
                
            except Exception as e:
                return f"❌ Error deleting knowledge entry: {str(e)}"

        @self.mcp.tool()
        def projects_list() -> str:
            """List all available projects"""
            try:
                projects = self.db.list_projects()
                
                if not projects:
                    return "📁 No projects found"
                
                formatted_projects = [f"📁 Available projects: {len(projects)} found\n"]
                
                for i, project_info in enumerate(projects, 1):
                    formatted_projects.append(
                        f"\n#{i} {project_info.name}\n"
                        f"Entries: {project_info.total_entries} | "
                        f"Created: {project_info.created_at.strftime('%Y-%m-%d %H:%M')} | "
                        f"Updated: {project_info.last_updated.strftime('%Y-%m-%d %H:%M') if project_info.last_updated else 'N/A'}"
                    )
                
                return "\n".join(formatted_projects)
                
            except Exception as e:
                return f"❌ Error listing projects: {str(e)}"

        @self.mcp.tool()
        def memo_get(project: str, entry_id: str) -> str:
            """Get a specific knowledge entry by ID
            
            Args:
                project: Project name
                entry_id: ID of the entry to retrieve
            """
            try:
                entry = self.db.get_knowledge_by_id(project, entry_id)
                
                if entry is None:
                    return f"❌ Knowledge entry '{entry_id}' not found in project '{project}'"
                
                tags_str = f" [Tags: {', '.join(entry.tags)}]" if entry.tags else ""
                
                return (
                    f"📄 Knowledge Entry Details\n\n"
                    f"ID: {entry.id}\n"
                    f"Project: {entry.project}{tags_str}\n"
                    f"Content: {entry.content}\n"
                    f"Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Source: {entry.source.value}"
                )
                
            except Exception as e:
                return f"❌ Error getting knowledge entry: {str(e)}"

        @self.mcp.tool()
        def project_info(project: str) -> str:
            """Get detailed information about a project
            
            Args:
                project: Project name
            """
            try:
                info = self.db.get_project_info(project)
                
                if not info:
                    return f"❌ Project '{project}' not found"
                
                return (
                    f"📊 Project Information: {project}\n\n"
                    f"Total Entries: {info.total_entries}\n"
                    f"Created: {info.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Last Updated: {info.last_updated.strftime('%Y-%m-%d %H:%M') if info.last_updated else 'N/A'}\n"
                    f"Database Path: {self.db.db_path}"
                )
                
            except Exception as e:
                return f"❌ Error getting project info: {str(e)}"
        
        # If project name is specified, add project-specific tools
        if self.project_name:
            @self.mcp.tool()
            def add_to_current_project(content: str, tags: Optional[List[str]] = None) -> str:
                """Add knowledge entry to the current project
                
                Args:
                    content: Knowledge content to add
                    tags: Optional list of tags
                """
                return memo_add(self.project_name, content, tags)
            
            @self.mcp.tool()
            def search_current_project(query: str, max_results: int = 5) -> str:
                """Search in the current project
                
                Args:
                    query: Search query
                    max_results: Maximum number of results (default: 5)
                """
                return memo_search(self.project_name, query, max_results)
            
            @self.mcp.tool()
            def list_current_project() -> str:
                """List all entries in the current project"""
                return memo_list(self.project_name)
            
            @self.mcp.tool()
            def get_from_current_project(entry_id: str) -> str:
                """Get a specific knowledge entry from the current project
                
                Args:
                    entry_id: ID of the entry to retrieve
                """
                return memo_get(self.project_name, entry_id)
            
            @self.mcp.tool()
            def delete_from_current_project(entry_id: str) -> str:
                """Delete a knowledge entry from the current project
                
                Args:
                    entry_id: ID of the entry to delete
                """
                return memo_delete(self.project_name, entry_id)
    
    def run(self):
        """Run the MCP server"""
        # Log server startup to stderr (not stdout)
        if self.project_name:
            print(f"🚀 Chroma-Memo MCP Server starting for project: {self.project_name}", file=sys.stderr)
            print(f"📦 Available tools: memo_add, memo_search, memo_list, memo_get, memo_delete, projects_list, project_info", file=sys.stderr)
            print(f"🎯 Project-specific tools: add_to_current_project, search_current_project, list_current_project, get_from_current_project, delete_from_current_project", file=sys.stderr)
        else:
            print("🚀 Chroma-Memo MCP Server starting (all projects)", file=sys.stderr)
            print(f"📦 Available tools: memo_add, memo_search, memo_list, memo_get, memo_delete, projects_list, project_info", file=sys.stderr)
        
        # Run the server
        self.mcp.run(transport="stdio")


def start_mcp_server(project_name: str = None, auto_init: bool = True):
    """Start MCP server for a specific project
    
    Args:
        project_name: Project name to serve (optional)
        auto_init: Automatically initialize project if it doesn't exist
    """
    if project_name and auto_init:
        # Auto-initialize project if it doesn't exist
        db = get_database()
        if not db.project_exists(project_name):
            print(f"📁 Project '{project_name}' does not exist. Creating...", file=sys.stderr)
            try:
                db.create_project(project_name)
                print(f"✅ Project '{project_name}' created successfully", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to create project '{project_name}': {e}", file=sys.stderr)
                sys.exit(1)
    
    # Start the server
    server = ChromaMemoMCPServer(project_name)
    server.run()