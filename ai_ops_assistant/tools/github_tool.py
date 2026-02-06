"""
GitHub Tool for repository search and information retrieval
"""
import os
from typing import Dict, Any, List, Optional
from github import Github, GithubException
import requests
from .base_tool import BaseTool


class GitHubTool(BaseTool):
    """Tool for interacting with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub tool
        
        Args:
            token: GitHub personal access token (optional, for higher rate limits)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if self.token:
            self.github = Github(self.token)
        else:
            self.github = Github()  # Anonymous access with lower rate limits
    
    @property
    def name(self) -> str:
        return "github"
    
    @property
    def description(self) -> str:
        return "Search GitHub repositories, get repository details, stars, and descriptions"
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "action": "Action to perform: 'search_repos', 'get_repo_info', 'get_user_info'",
            "query": "Search query (for search_repos)",
            "repo_name": "Repository full name like 'owner/repo' (for get_repo_info)",
            "username": "GitHub username (for get_user_info)",
            "language": "Filter by programming language (optional)",
            "sort": "Sort by: 'stars', 'forks', 'updated' (default: stars)",
            "limit": "Maximum number of results (default: 5)"
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute GitHub tool action
        
        Args:
            action: The action to perform
            **kwargs: Action-specific parameters
            
        Returns:
            Dictionary with execution results
        """
        action = kwargs.get("action", "search_repos")
        
        try:
            if action == "search_repos":
                return self._search_repos(**kwargs)
            elif action == "get_repo_info":
                return self._get_repo_info(**kwargs)
            elif action == "get_user_info":
                return self._get_user_info(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        except GithubException as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing GitHub tool: {str(e)}"
            }
    
    def _search_repos(self, **kwargs) -> Dict[str, Any]:
        """Search GitHub repositories"""
        query = kwargs.get("query", "")
        language = kwargs.get("language")
        sort = kwargs.get("sort", "stars")
        limit = int(kwargs.get("limit", 5))
        
        if not query:
            return {"success": False, "error": "Query parameter is required"}
        
        # Build search query
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        # Search repositories
        repositories = self.github.search_repositories(
            query=search_query,
            sort=sort
        )
        
        # Get top results
        results = []
        for repo in repositories[:limit]:
            results.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "url": repo.html_url,
                "owner": repo.owner.login
            })
        
        return {
            "success": True,
            "action": "search_repos",
            "query": query,
            "count": len(results),
            "repositories": results
        }
    
    def _get_repo_info(self, **kwargs) -> Dict[str, Any]:
        """Get detailed information about a specific repository"""
        repo_name = kwargs.get("repo_name")
        
        if not repo_name:
            return {"success": False, "error": "repo_name parameter is required"}
        
        repo = self.github.get_repo(repo_name)
        
        return {
            "success": True,
            "action": "get_repo_info",
            "repository": {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "language": repo.language,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "url": repo.html_url,
                "owner": repo.owner.login,
                "topics": repo.get_topics(),
                "open_issues": repo.open_issues_count
            }
        }
    
    def _get_user_info(self, **kwargs) -> Dict[str, Any]:
        """Get information about a GitHub user"""
        username = kwargs.get("username")
        
        if not username:
            return {"success": False, "error": "username parameter is required"}
        
        user = self.github.get_user(username)
        
        return {
            "success": True,
            "action": "get_user_info",
            "user": {
                "username": user.login,
                "name": user.name,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
                "email": user.email,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat(),
                "url": user.html_url
            }
        }
