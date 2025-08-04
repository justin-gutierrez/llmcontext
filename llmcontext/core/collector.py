"""
Documentation Collector Module

This module handles downloading and collecting documentation for various tools and frameworks
from their official websites, GitHub repositories, and other sources.
"""

import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Union
import re
import json
import logging
from urllib.parse import urljoin, urlparse
import time
from dataclasses import dataclass
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class DocSource:
    """Represents a documentation source for a tool."""
    name: str
    url: str
    type: str  # 'website', 'github', 'api'
    selectors: Optional[Dict[str, str]] = None  # CSS selectors for content extraction
    headers: Optional[Dict[str, str]] = None


class DocumentationCollector:
    """Collects documentation from various sources for tools and frameworks."""
    
    def __init__(self, docs_dir: Path = Path("raw_docs")):
        self.docs_dir = docs_dir
        self.docs_dir.mkdir(exist_ok=True)
        
        # Documentation sources for various tools
        self.doc_sources = {
            # Frontend Frameworks
            "react": [
                DocSource(
                    name="React Documentation",
                    url="https://react.dev/learn",
                    type="website",
                    selectors={"content": "main", "title": "h1"}
                ),
                DocSource(
                    name="React API Reference",
                    url="https://react.dev/reference",
                    type="website",
                    selectors={"content": "main", "title": "h1"}
                )
            ],
            "vue": [
                DocSource(
                    name="Vue.js Guide",
                    url="https://vuejs.org/guide/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "angular": [
                DocSource(
                    name="Angular Documentation",
                    url="https://angular.io/docs",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "svelte": [
                DocSource(
                    name="Svelte Documentation",
                    url="https://svelte.dev/docs",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            
            # CSS Frameworks
            "tailwindcss": [
                DocSource(
                    name="Tailwind CSS Documentation",
                    url="https://tailwindcss.com/docs",
                    type="website",
                    selectors={"content": ".prose", "title": "h1"}
                )
            ],
            "bootstrap": [
                DocSource(
                    name="Bootstrap Documentation",
                    url="https://getbootstrap.com/docs/",
                    type="website",
                    selectors={"content": ".bd-content", "title": "h1"}
                )
            ],
            
            # Backend Frameworks
            "fastapi": [
                DocSource(
                    name="FastAPI Documentation",
                    url="https://fastapi.tiangolo.com/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                ),
                DocSource(
                    name="FastAPI GitHub",
                    url="https://github.com/tiangolo/fastapi",
                    type="github",
                    selectors={"content": ".markdown-body", "readme": "#readme"}
                )
            ],
            "django": [
                DocSource(
                    name="Django Documentation",
                    url="https://docs.djangoproject.com/",
                    type="website",
                    selectors={"content": ".document", "title": "h1"}
                )
            ],
            "flask": [
                DocSource(
                    name="Flask Documentation",
                    url="https://flask.palletsprojects.com/",
                    type="website",
                    selectors={"content": ".document", "title": "h1"}
                )
            ],
            
            # JavaScript Tools
            "typescript": [
                DocSource(
                    name="TypeScript Handbook",
                    url="https://www.typescriptlang.org/docs/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "webpack": [
                DocSource(
                    name="Webpack Documentation",
                    url="https://webpack.js.org/concepts/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "vite": [
                DocSource(
                    name="Vite Documentation",
                    url="https://vitejs.dev/guide/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            
            # Testing Frameworks
            "jest": [
                DocSource(
                    name="Jest Documentation",
                    url="https://jestjs.io/docs/getting-started",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "pytest": [
                DocSource(
                    name="Pytest Documentation",
                    url="https://docs.pytest.org/",
                    type="website",
                    selectors={"content": ".document", "title": "h1"}
                )
            ],
            
            # Database & ORM
            "prisma": [
                DocSource(
                    name="Prisma Documentation",
                    url="https://www.prisma.io/docs/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "sqlalchemy": [
                DocSource(
                    name="SQLAlchemy Documentation",
                    url="https://docs.sqlalchemy.org/",
                    type="website",
                    selectors={"content": ".document", "title": "h1"}
                )
            ],
            
            # Development Tools
            "eslint": [
                DocSource(
                    name="ESLint Documentation",
                    url="https://eslint.org/docs/latest/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "prettier": [
                DocSource(
                    name="Prettier Documentation",
                    url="https://prettier.io/docs/en/",
                    type="website",
                    selectors={"content": ".content", "title": "h1"}
                )
            ],
            "black": [
                DocSource(
                    name="Black Documentation",
                    url="https://black.readthedocs.io/",
                    type="website",
                    selectors={"content": ".document", "title": "h1"}
                )
            ],
        }
        
        # Default headers for web scraping
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def collect_documentation(self, tool_name: str, force_refresh: bool = False) -> bool:
        """
        Collect documentation for a specific tool.
        
        Args:
            tool_name: Name of the tool to collect documentation for
            force_refresh: Whether to force refresh existing documentation
            
        Returns:
            True if documentation was successfully collected, False otherwise
        """
        tool_name = tool_name.lower()
        
        if tool_name not in self.doc_sources:
            logger.warning(f"No documentation sources found for tool: {tool_name}")
            return False
        
        output_file = self.docs_dir / f"{tool_name}.md"
        
        # Check if file already exists and we're not forcing refresh
        if output_file.exists() and not force_refresh:
            logger.info(f"Documentation for {tool_name} already exists. Use force_refresh=True to update.")
            return True
        
        logger.info(f"Collecting documentation for {tool_name}...")
        
        try:
            # Collect from all sources
            all_content = []
            sources = self.doc_sources[tool_name]
            
            # Progress bar for sources
            with tqdm(total=len(sources), desc=f"Collecting {tool_name}", unit="source") as pbar:
                for source in sources:
                    try:
                        pbar.set_description(f"Collecting {tool_name} from {source.name}")
                        content = await self._fetch_from_source(source)
                        if content:
                            all_content.append(f"# {source.name}\n\n{content}\n\n---\n\n")
                            logger.info(f"Successfully collected from {source.name}")
                            pbar.set_postfix(status="✅ Success")
                        else:
                            logger.warning(f"No content collected from {source.name}")
                            pbar.set_postfix(status="⚠️ No content")
                    except Exception as e:
                        logger.error(f"Error collecting from {source.name}: {e}")
                        pbar.set_postfix(status="❌ Error")
                        continue
                    finally:
                        pbar.update(1)
            
            if all_content:
                # Write combined content to file
                async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                    await f.write(f"# {tool_name.title()} Documentation\n\n")
                    await f.write(f"Collected on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    await f.write("".join(all_content))
                
                logger.info(f"Documentation saved to {output_file}")
                return True
            else:
                logger.error(f"No content collected for {tool_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error collecting documentation for {tool_name}: {e}")
            return False
    
    async def _fetch_from_source(self, source: DocSource) -> Optional[str]:
        """
        Fetch documentation from a specific source.
        
        Args:
            source: Documentation source configuration
            
        Returns:
            Extracted content as string, or None if failed
        """
        if source.type == "website":
            return await self._fetch_from_website(source)
        elif source.type == "github":
            return await self._fetch_from_github(source)
        else:
            logger.warning(f"Unknown source type: {source.type}")
            return None
    
    async def _fetch_from_website(self, source: DocSource) -> Optional[str]:
        """
        Fetch documentation from a website.
        
        Args:
            source: Website source configuration
            
        Returns:
            Extracted content as string, or None if failed
        """
        try:
            headers = {**self.default_headers}
            if source.headers:
                headers.update(source.headers)
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(source.url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"HTTP {response.status} for {source.url}")
                        return None
                    
                    html = await response.text()
                    
                    # Basic content extraction (simplified - in production you'd use BeautifulSoup)
                    if source.selectors and "content" in source.selectors:
                        # Simple regex-based extraction as fallback
                        content_pattern = r'<main[^>]*>(.*?)</main>'
                        match = re.search(content_pattern, html, re.DOTALL | re.IGNORECASE)
                        if match:
                            content = match.group(1)
                            # Basic HTML tag removal
                            content = re.sub(r'<[^>]+>', '', content)
                            content = re.sub(r'\s+', ' ', content).strip()
                            return content
                    
                    # Fallback: extract text from body
                    body_pattern = r'<body[^>]*>(.*?)</body>'
                    match = re.search(body_pattern, html, re.DOTALL | re.IGNORECASE)
                    if match:
                        content = match.group(1)
                        content = re.sub(r'<[^>]+>', '', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                        return content
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching from website {source.url}: {e}")
            return None
    
    async def _fetch_from_github(self, source: DocSource) -> Optional[str]:
        """
        Fetch documentation from GitHub repository.
        
        Args:
            source: GitHub source configuration
            
        Returns:
            Extracted content as string, or None if failed
        """
        try:
            # Parse GitHub URL to get owner/repo
            parsed = urlparse(source.url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                logger.error(f"Invalid GitHub URL: {source.url}")
                return None
            
            owner, repo = path_parts[0], path_parts[1]
            
            # Fetch README content using GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            
            headers = {**self.default_headers}
            headers["Accept"] = "application/vnd.github.v3+json"
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(api_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"GitHub API error {response.status} for {api_url}")
                        return None
                    
                    data = await response.json()
                    content = data.get("content", "")
                    
                    if content:
                        # Decode base64 content
                        import base64
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        return decoded_content
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching from GitHub {source.url}: {e}")
            return None
    
    async def collect_all_documentation(self, force_refresh: bool = False) -> Dict[str, bool]:
        """
        Collect documentation for all available tools.
        
        Args:
            force_refresh: Whether to force refresh existing documentation
            
        Returns:
            Dictionary mapping tool names to success status
        """
        results = {}
        tools = list(self.doc_sources.keys())
        
        # Progress bar for all tools
        with tqdm(total=len(tools), desc="Collecting all documentation", unit="tool") as pbar:
            for tool_name in tools:
                try:
                    pbar.set_description(f"Collecting {tool_name}")
                    success = await self.collect_documentation(tool_name, force_refresh)
                    results[tool_name] = success
                    if success:
                        pbar.set_postfix(status="✅ Success")
                    else:
                        pbar.set_postfix(status="❌ Failed")
                except Exception as e:
                    logger.error(f"Error collecting documentation for {tool_name}: {e}")
                    results[tool_name] = False
                    pbar.set_postfix(status="❌ Error")
                finally:
                    pbar.update(1)
        
        return results
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of tools that have documentation sources configured.
        
        Returns:
            List of tool names
        """
        return list(self.doc_sources.keys())
    
    def add_documentation_source(self, tool_name: str, source: DocSource) -> None:
        """
        Add a new documentation source for a tool.
        
        Args:
            tool_name: Name of the tool
            source: Documentation source configuration
        """
        tool_name = tool_name.lower()
        
        if tool_name not in self.doc_sources:
            self.doc_sources[tool_name] = []
        
        self.doc_sources[tool_name].append(source)
        logger.info(f"Added documentation source for {tool_name}: {source.name}")


# Convenience functions for easy usage
async def collect_docs_for_tool(tool_name: str, docs_dir: Path = Path("raw_docs"), force_refresh: bool = False) -> bool:
    """
    Convenience function to collect documentation for a single tool.
    
    Args:
        tool_name: Name of the tool to collect documentation for
        docs_dir: Directory to save documentation
        force_refresh: Whether to force refresh existing documentation
        
    Returns:
        True if successful, False otherwise
    """
    collector = DocumentationCollector(docs_dir)
    return await collector.collect_documentation(tool_name, force_refresh)


async def collect_docs_for_all_tools(docs_dir: Path = Path("raw_docs"), force_refresh: bool = False) -> Dict[str, bool]:
    """
    Convenience function to collect documentation for all available tools.
    
    Args:
        docs_dir: Directory to save documentation
        force_refresh: Whether to force refresh existing documentation
        
    Returns:
        Dictionary mapping tool names to success status
    """
    collector = DocumentationCollector(docs_dir)
    return await collector.collect_all_documentation(force_refresh) 