"""
Framework detection functionality.
"""

import json
import re
import toml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DetectedFramework:
    """Represents a detected framework in the codebase."""
    name: str
    version: Optional[str]
    confidence: float
    files: List[str]
    metadata: Dict[str, Any]
    tags: List[str]


class FrameworkDetector:
    """Detects frameworks and libraries in a codebase."""
    
    def __init__(self):
        self.supported_frameworks = {
            "python": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
            "node": ["package.json", "yarn.lock", "package-lock.json"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum"],
            "java": ["pom.xml", "build.gradle", "gradle.properties"],
            "ruby": ["Gemfile", "Gemfile.lock"],
            "php": ["composer.json", "composer.lock"],
            "dotnet": ["*.csproj", "global.json"],
            "elixir": ["mix.exs"],
            "haskell": ["stack.yaml", "*.cabal"],
            "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        }
        
        # Framework inference rules based on config files and project structure
        self.framework_inference_rules = {
            # JavaScript/TypeScript frameworks
            "next.config.js": "nextjs",
            "next.config.ts": "nextjs",
            "next.config.mjs": "nextjs",
            "nuxt.config.js": "nuxt",
            "nuxt.config.ts": "nuxt",
            "vite.config.js": "vite",
            "vite.config.ts": "vite",
            "svelte.config.js": "sveltekit",
            "svelte.config.ts": "sveltekit",
            "angular.json": "angular",
            "remix.config.js": "remix",
            "remix.config.ts": "remix",
            "astro.config.js": "astro",
            "astro.config.mjs": "astro",
            "astro.config.ts": "astro",
            
            # Python frameworks
            "manage.py": "django",
            "settings.py": "django",
            "urls.py": "django",
            "wsgi.py": "django",
            "asgi.py": "django",
            "app.py": "flask",
            "main.py": "fastapi",
            
            # Java frameworks
            "application.properties": "spring-boot",
            "application.yml": "spring-boot",
            "application.yaml": "spring-boot",
            "bootstrap.properties": "spring-boot",
            "bootstrap.yml": "spring-boot",
            
            # Other frameworks
            "gatsby-config.js": "gatsby",
            "gatsby-config.ts": "gatsby",
            "vue.config.js": "vue",
            "vue.config.ts": "vue",
            "quasar.config.js": "quasar",
            "quasar.config.ts": "quasar",
            "capacitor.config.ts": "capacitor",
            "capacitor.config.js": "capacitor",
        }
        
        # Framework classification tags mapping
        self.framework_tags = {
            # Python Web Frameworks
            "fastapi": ["web", "api", "async"],
            "django": ["web", "orm", "backend"],
            "flask": ["web", "api", "backend"],
            "uvicorn": ["web", "async", "server"],
            "gunicorn": ["web", "server"],
            "starlette": ["web", "async"],
            
            # Python API & HTTP
            "requests": ["api", "http"],
            "httpx": ["api", "http", "async"],
            "aiohttp": ["api", "http", "async"],
            "urllib3": ["api", "http"],
            
            # Python Data & ORM
            "sqlalchemy": ["orm", "database"],
            "alembic": ["database", "migration"],
            "django-orm": ["orm", "database"],
            "peewee": ["orm", "database"],
            "tortoise-orm": ["orm", "database", "async"],
            
            # Python Testing
            "pytest": ["testing"],
            "unittest": ["testing"],
            "nose": ["testing"],
            "coverage": ["testing", "devtool"],
            "tox": ["testing", "devtool"],
            "pytest-asyncio": ["testing", "async"],
            "pytest-django": ["testing", "web"],
            "factory-boy": ["testing"],
            "faker": ["testing"],
            
            # Python Development Tools
            "black": ["devtool", "formatting"],
            "isort": ["devtool", "formatting"],
            "flake8": ["devtool", "linting"],
            "pylint": ["devtool", "linting"],
            "mypy": ["devtool", "linting", "typing"],
            "bandit": ["devtool", "security"],
            "pre-commit": ["devtool"],
            "poetry": ["devtool", "packaging"],
            "pip": ["devtool", "packaging"],
            
            # Python CLI & Utilities
            "click": ["cli"],
            "typer": ["cli"],
            "argparse": ["cli"],
            "rich": ["cli", "ui"],
            "tqdm": ["cli", "ui"],
            "colorama": ["cli", "ui"],
            
            # Python Data Science & ML
            "numpy": ["data", "scientific"],
            "pandas": ["data", "scientific"],
            "matplotlib": ["data", "visualization"],
            "seaborn": ["data", "visualization"],
            "scikit-learn": ["ai", "ml"],
            "tensorflow": ["ai", "ml"],
            "pytorch": ["ai", "ml"],
            "jupyter": ["data", "scientific"],
            
            # Python Async & Concurrency
            "asyncio": ["async"],
            "aiofiles": ["async", "file"],
            "aio-pika": ["async", "message"],
            "celery": ["async", "task"],
            
            # JavaScript Frontend Frameworks
            "react": ["frontend", "web", "ui"],
            "vue": ["frontend", "web", "ui"],
            "angular": ["frontend", "web", "ui"],
            "svelte": ["frontend", "web", "ui"],
            "next": ["frontend", "web", "ssr"],
            "nuxt": ["frontend", "web", "ssr"],
            "gatsby": ["frontend", "web", "ssg"],
            "remix": ["frontend", "web", "ssr"],
            "astro": ["frontend", "web", "ssg"],
            
            # JavaScript Backend & API
            "express": ["backend", "api", "web"],
            "koa": ["backend", "api", "web"],
            "fastify": ["backend", "api", "web"],
            "nest": ["backend", "api", "web"],
            "hapi": ["backend", "api", "web"],
            
            # JavaScript Database & ORM
            "prisma": ["orm", "database"],
            "sequelize": ["orm", "database"],
            "typeorm": ["orm", "database"],
            "mongoose": ["orm", "database"],
            "knex": ["orm", "database"],
            
            # JavaScript Testing
            "jest": ["testing"],
            "mocha": ["testing"],
            "vitest": ["testing"],
            "cypress": ["testing", "e2e"],
            "playwright": ["testing", "e2e"],
            "testing-library": ["testing"],
            
            # JavaScript Development Tools
            "typescript": ["devtool", "typing"],
            "eslint": ["devtool", "linting"],
            "prettier": ["devtool", "formatting"],
            "webpack": ["devtool", "bundling"],
            "vite": ["devtool", "bundling"],
            "rollup": ["devtool", "bundling"],
            "parcel": ["devtool", "bundling"],
            "babel": ["devtool", "transpiling"],
            
            # JavaScript Styling
            "tailwindcss": ["styling", "css"],
            "styled-components": ["styling", "css"],
            "emotion": ["styling", "css"],
            "sass": ["styling", "css"],
            "less": ["styling", "css"],
            "postcss": ["styling", "css"],
            
            # JavaScript State Management
            "redux": ["state", "frontend"],
            "zustand": ["state", "frontend"],
            "mobx": ["state", "frontend"],
            "recoil": ["state", "frontend"],
            
            # Java Frameworks
            "spring": ["web", "backend", "api"],
            "spring-boot": ["web", "backend", "api"],
            "spring-mvc": ["web", "backend", "api"],
            "spring-data": ["orm", "database"],
            "hibernate": ["orm", "database"],
            "jpa": ["orm", "database"],
            
            # Java Testing
            "junit": ["testing"],
            "testng": ["testing"],
            "mockito": ["testing"],
            "selenium": ["testing", "e2e"],
            
            # Java Build Tools
            "maven": ["devtool", "build"],
            "gradle": ["devtool", "build"],
            "ant": ["devtool", "build"],
            
            # Ruby Frameworks
            "rails": ["web", "backend", "orm"],
            "sinatra": ["web", "api"],
            "hanami": ["web", "backend"],
            
            # Ruby Testing
            "rspec": ["testing"],
            "minitest": ["testing"],
            "cucumber": ["testing", "bdd"],
            
            # PHP Frameworks
            "laravel": ["web", "backend", "orm"],
            "symfony": ["web", "backend", "orm"],
            "codeigniter": ["web", "backend"],
            "slim": ["web", "api"],
            
            # PHP Testing
            "phpunit": ["testing"],
            "behat": ["testing", "bdd"],
            
            # Go Frameworks
            "gin": ["web", "api"],
            "echo": ["web", "api"],
            "fiber": ["web", "api"],
            "gorilla": ["web", "api"],
            
            # Go Database
            "gorm": ["orm", "database"],
            "sqlx": ["database"],
            
            # Go Testing
            "testify": ["testing"],
            
            # Rust Frameworks
            "actix": ["web", "api"],
            "rocket": ["web", "api"],
            "warp": ["web", "api"],
            "axum": ["web", "api"],
            
            # Rust Database
            "diesel": ["orm", "database"],
            "sqlx": ["database"],
            
            # Rust Testing
            "criterion": ["testing", "benchmark"],
            
            # .NET Frameworks
            "aspnet": ["web", "api"],
            "aspnet-core": ["web", "api"],
            "entity-framework": ["orm", "database"],
            "nhibernate": ["orm", "database"],
            
            # .NET Testing
            "nunit": ["testing"],
            "xunit": ["testing"],
            "moq": ["testing"],
            
            # Infrastructure & Cloud
            "docker": ["infra", "container"],
            "kubernetes": ["infra", "container", "orchestration"],
            "terraform": ["infra", "iac"],
            "ansible": ["infra", "automation"],
            "helm": ["infra", "kubernetes"],
            
            # Cloud Platforms
            "aws": ["cloud", "infra"],
            "azure": ["cloud", "infra"],
            "gcp": ["cloud", "infra"],
            "heroku": ["cloud", "platform"],
            
            # Message Queues & Event Systems
            "redis": ["cache", "message"],
            "rabbitmq": ["message", "queue"],
            "kafka": ["message", "stream"],
            "celery": ["task", "queue"],
            
            # Monitoring & Logging
            "prometheus": ["monitoring", "metrics"],
            "grafana": ["monitoring", "visualization"],
            "elk": ["logging", "search"],
            "sentry": ["monitoring", "error"],
            
            # Security
            "jwt": ["security", "auth"],
            "oauth": ["security", "auth"],
            "bcrypt": ["security", "crypto"],
            "cryptography": ["security", "crypto"],
        }
    
    def detect_frameworks(self, codebase_path: Path) -> List[DetectedFramework]:
        """
        Detect frameworks in the given codebase.
        
        Args:
            codebase_path: Path to the codebase to analyze
            
        Returns:
            List of detected frameworks
        """
        detected_frameworks = []
        
        # Scan for manifest files
        manifest_files = self._scan_for_manifest_files(codebase_path)
        
        # Analyze each type of manifest
        for framework_type, files in manifest_files.items():
            if framework_type == "python":
                detected_frameworks.extend(self._analyze_python_frameworks(files))
            elif framework_type == "node":
                detected_frameworks.extend(self._analyze_node_frameworks(files))
            elif framework_type == "rust":
                detected_frameworks.extend(self._analyze_rust_frameworks(files))
            elif framework_type == "go":
                detected_frameworks.extend(self._analyze_go_frameworks(files))
            elif framework_type == "java":
                detected_frameworks.extend(self._analyze_java_frameworks(files))
            elif framework_type == "ruby":
                detected_frameworks.extend(self._analyze_ruby_frameworks(files))
            elif framework_type == "php":
                detected_frameworks.extend(self._analyze_php_frameworks(files))
            elif framework_type == "dotnet":
                detected_frameworks.extend(self._analyze_dotnet_frameworks(files))
            elif framework_type == "elixir":
                detected_frameworks.extend(self._analyze_elixir_frameworks(files))
            elif framework_type == "haskell":
                detected_frameworks.extend(self._analyze_haskell_frameworks(files))
            elif framework_type == "docker":
                detected_frameworks.extend(self._analyze_docker_frameworks(files))
        
        # Infer frameworks based on project structure and config files
        inferred_frameworks = self._infer_frameworks_from_structure(codebase_path)
        detected_frameworks.extend(inferred_frameworks)
        
        return detected_frameworks
    
    def _analyze_rust_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Rust-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "Cargo.toml":
                    detected.extend(self._parse_cargo_toml(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_go_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Go-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "go.mod":
                    detected.extend(self._parse_go_mod(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_java_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Java-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "pom.xml":
                    detected.extend(self._parse_pom_xml(file_path))
                elif file_path.name == "build.gradle":
                    detected.extend(self._parse_build_gradle(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_ruby_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Ruby-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "Gemfile":
                    detected.extend(self._parse_gemfile(file_path))
                elif file_path.name == "Gemfile.lock":
                    detected.extend(self._parse_gemfile_lock(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_php_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze PHP-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "composer.json":
                    detected.extend(self._parse_composer_json(file_path))
                elif file_path.name == "composer.lock":
                    detected.extend(self._parse_composer_lock(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_dotnet_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze .NET-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name.endswith(".csproj"):
                    detected.extend(self._parse_csproj(file_path))
                elif file_path.name == "global.json":
                    detected.extend(self._parse_global_json(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_elixir_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Elixir-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "mix.exs":
                    detected.extend(self._parse_mix_exs(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_haskell_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Haskell-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "stack.yaml":
                    detected.extend(self._parse_stack_yaml(file_path))
                elif file_path.name.endswith(".cabal"):
                    detected.extend(self._parse_cabal_file(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_docker_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Docker-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "Dockerfile":
                    detected.extend(self._parse_dockerfile(file_path))
                elif file_path.name in ["docker-compose.yml", "docker-compose.yaml"]:
                    detected.extend(self._parse_docker_compose(file_path))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _infer_frameworks_from_structure(self, codebase_path: Path) -> List[DetectedFramework]:
        """
        Infer frameworks based on project structure and config files.
        
        Args:
            codebase_path: Path to the codebase to analyze
            
        Returns:
            List of inferred frameworks
        """
        inferred_frameworks = []
        
        # Scan for framework-specific config files
        for filename, framework_name in self.framework_inference_rules.items():
            # Handle glob patterns
            if '*' in filename:
                pattern = filename.replace('*', '**')
                matching_files = list(codebase_path.rglob(pattern))
            else:
                matching_files = list(codebase_path.rglob(filename))
            
            for file_path in matching_files:
                # Skip if file is in common exclude directories
                if any(exclude in str(file_path) for exclude in ['node_modules', '__pycache__', '.git', 'dist', 'build']):
                    continue
                
                # Try to extract version from the file content
                version = self._extract_version_from_config_file(file_path, framework_name)
                
                inferred_frameworks.append(DetectedFramework(
                    name=framework_name,
                    version=version,
                    confidence=0.6,  # Lower confidence for inferred frameworks
                    files=[str(file_path)],
                    metadata={
                        "source": "inferred",
                        "inferred": True,
                        "config_file": filename,
                        "framework_type": "config_based"
                    },
                    tags=self._get_framework_tags(framework_name)
                ))
        
        # Additional inference based on file content analysis
        content_based_inferences = self._infer_from_file_content(codebase_path)
        inferred_frameworks.extend(content_based_inferences)
        
        return inferred_frameworks
    
    def _extract_version_from_config_file(self, file_path: Path, framework_name: str) -> Optional[str]:
        """
        Try to extract version information from config files.
        
        Args:
            file_path: Path to the config file
            framework_name: Name of the framework
            
        Returns:
            Version string if found, None otherwise
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Framework-specific version extraction patterns
            version_patterns = {
                "nextjs": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "nuxt": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "vite": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "sveltekit": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "angular": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "remix": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "astro": [
                    r'"version":\s*["\']([^"\']+)["\']',
                    r'version:\s*["\']([^"\']+)["\']',
                ],
                "django": [
                    r'VERSION\s*=\s*["\']([^"\']+)["\']',
                    r'version\s*=\s*["\']([^"\']+)["\']',
                ],
                "flask": [
                    r'__version__\s*=\s*["\']([^"\']+)["\']',
                    r'version\s*=\s*["\']([^"\']+)["\']',
                ],
                "fastapi": [
                    r'__version__\s*=\s*["\']([^"\']+)["\']',
                    r'version\s*=\s*["\']([^"\']+)["\']',
                ],
                "spring-boot": [
                    r'spring\.boot\.version\s*=\s*([^\s]+)',
                    r'version\s*=\s*([^\s]+)',
                ],
            }
            
            patterns = version_patterns.get(framework_name, [])
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            # Generic version patterns
            generic_patterns = [
                r'"version":\s*["\']([^"\']+)["\']',
                r'version:\s*["\']([^"\']+)["\']',
                r'VERSION\s*=\s*["\']([^"\']+)["\']',
                r'__version__\s*=\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in generic_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
                    
        except Exception as e:
            print(f"Error extracting version from {file_path}: {e}")
        
        return None
    
    def _infer_from_file_content(self, codebase_path: Path) -> List[DetectedFramework]:
        """
        Infer frameworks by analyzing file content for framework-specific patterns.
        
        Args:
            codebase_path: Path to the codebase to analyze
            
        Returns:
            List of inferred frameworks
        """
        inferred_frameworks = []
        
        # Content-based inference patterns
        content_patterns = {
            "react": [
                (r'import\s+React', "*.js", "*.jsx", "*.ts", "*.tsx"),
                (r'from\s+["\']react["\']', "*.js", "*.jsx", "*.ts", "*.tsx"),
                (r'ReactDOM\.render', "*.js", "*.jsx", "*.ts", "*.tsx"),
            ],
            "vue": [
                (r'import\s+{.*}\s+from\s+["\']vue["\']', "*.js", "*.ts", "*.vue"),
                (r'Vue\.createApp', "*.js", "*.ts", "*.vue"),
                (r'<template>', "*.vue"),
            ],
            "angular": [
                (r'@Component', "*.ts"),
                (r'import\s+{.*}\s+from\s+["\']@angular', "*.ts"),
                (r'@Injectable', "*.ts"),
            ],
            "svelte": [
                (r'<script>', "*.svelte"),
                (r'import\s+{.*}\s+from\s+["\']svelte', "*.svelte", "*.js", "*.ts"),
            ],
            "tailwind": [
                (r'@tailwind', "*.css", "*.scss", "*.sass"),
                (r'tailwindcss', "*.js", "*.ts", "*.json"),
            ],
            "bootstrap": [
                (r'@import\s+["\']bootstrap', "*.css", "*.scss", "*.sass"),
                (r'bootstrap', "*.js", "*.ts", "*.json"),
            ],
        }
        
        for framework_name, patterns in content_patterns.items():
            for pattern, *file_extensions in patterns:
                for ext in file_extensions:
                    matching_files = list(codebase_path.rglob(ext))
                    for file_path in matching_files:
                        # Skip common exclude directories
                        if any(exclude in str(file_path) for exclude in ['node_modules', '__pycache__', '.git', 'dist', 'build']):
                            continue
                        
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            if re.search(pattern, content, re.IGNORECASE):
                                inferred_frameworks.append(DetectedFramework(
                                    name=framework_name,
                                    version=None,
                                    confidence=0.5,  # Lower confidence for content-based inference
                                    files=[str(file_path)],
                                    metadata={
                                        "source": "inferred",
                                        "inferred": True,
                                        "inference_type": "content_pattern",
                                        "pattern": pattern,
                                        "framework_type": "content_based"
                                    },
                                    tags=self._get_framework_tags(framework_name)
                                ))
                                break  # Found one match, no need to check other files
                        except Exception as e:
                            continue
        
        return inferred_frameworks
    
    def _get_framework_tags(self, framework_name: str) -> List[str]:
        """
        Get classification tags for a framework.
        
        Args:
            framework_name: Name of the framework
            
        Returns:
            List of tags for the framework
        """
        # Clean the framework name (remove version info, brackets, etc.)
        clean_name = framework_name.lower()
        
        # Remove common suffixes and prefixes
        clean_name = re.sub(r'\[.*?\]', '', clean_name)  # Remove [standard], [all], etc.
        clean_name = clean_name.strip()
        
        # Check exact match first
        if clean_name in self.framework_tags:
            return self.framework_tags[clean_name]
        
        # Check for partial matches (for cases like "fastapi" vs "fastapi[standard]")
        for key, tags in self.framework_tags.items():
            if clean_name.startswith(key) or key in clean_name:
                return tags
        
        # Check for common patterns
        if any(pattern in clean_name for pattern in ["test", "pytest", "jest", "mocha", "junit"]):
            return ["testing"]
        elif any(pattern in clean_name for pattern in ["lint", "flake", "eslint", "pylint"]):
            return ["devtool", "linting"]
        elif any(pattern in clean_name for pattern in ["format", "black", "prettier"]):
            return ["devtool", "formatting"]
        elif any(pattern in clean_name for pattern in ["orm", "sqlalchemy", "prisma"]):
            return ["orm", "database"]
        elif any(pattern in clean_name for pattern in ["web", "http", "api"]):
            return ["web", "api"]
        
        return []
    
    # Parsing methods for different file types
    def _parse_requirements_txt(self, file_path: Path) -> List[DetectedFramework]:
        """Parse requirements.txt file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Handle different requirement formats
                if '==' in line:
                    name, version = line.split('==', 1)
                elif '>=' in line:
                    name, version = line.split('>=', 1)
                elif '<=' in line:
                    name, version = line.split('<=', 1)
                elif '~=' in line:
                    name, version = line.split('~=', 1)
                elif '!=' in line:
                    name, version = line.split('!=', 1)
                else:
                    name, version = line, None
                
                name = name.strip()
                if name:
                    detected.append(DetectedFramework(
                        name=name,
                        version=version.strip() if version else None,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "requirements.txt"},
                        tags=self._get_framework_tags(name)
                    ))
        
        return detected
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[DetectedFramework]:
        """Parse pyproject.toml file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = toml.loads(content)
            
            # Check dependencies
            if 'project' in data and 'dependencies' in data['project']:
                for dep in data['project']['dependencies']:
                    name, version = self._parse_dependency_string(dep)
                    detected.append(DetectedFramework(
                        name=name,
                        version=version,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "pyproject.toml"},
                        tags=self._get_framework_tags(name)
                    ))
            
            # Check optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group, deps in data['project']['optional-dependencies'].items():
                    for dep in deps:
                        name, version = self._parse_dependency_string(dep)
                        detected.append(DetectedFramework(
                            name=name,
                            version=version,
                            confidence=0.8,
                            files=[str(file_path)],
                            metadata={"source": "pyproject.toml", "group": group},
                            tags=self._get_framework_tags(name)
                        ))
                        
        except Exception as e:
            print(f"Error parsing pyproject.toml: {e}")
        
        return detected
    
    def _parse_setup_py(self, file_path: Path) -> List[DetectedFramework]:
        """Parse setup.py file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Simple regex-based parsing for common patterns
        install_requires_pattern = r'install_requires\s*=\s*\[(.*?)\]'
        match = re.search(install_requires_pattern, content, re.DOTALL)
        
        if match:
            deps_str = match.group(1)
            # Extract dependencies from the string
            deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
            for dep in deps:
                name, version = self._parse_dependency_string(dep)
                detected.append(DetectedFramework(
                    name=name,
                    version=version,
                    confidence=0.8,
                    files=[str(file_path)],
                    metadata={"source": "setup.py"},
                    tags=self._get_framework_tags(name)
                ))
        
        return detected
    
    def _parse_pipfile(self, file_path: Path) -> List[DetectedFramework]:
        """Parse Pipfile."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = toml.loads(content)
            
            # Check packages
            if 'packages' in data:
                for name, version_info in data['packages'].items():
                    version = version_info.get('version') if isinstance(version_info, dict) else str(version_info)
                    detected.append(DetectedFramework(
                        name=name,
                        version=version if version != '*' else None,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "Pipfile"},
                        tags=self._get_framework_tags(name)
                    ))
                        
        except Exception as e:
            print(f"Error parsing Pipfile: {e}")
        
        return detected
    
    def _parse_package_json(self, file_path: Path) -> List[DetectedFramework]:
        """Parse package.json file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = json.loads(content)
            
            # Check dependencies
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                if dep_type in data:
                    for name, version in data[dep_type].items():
                        detected.append(DetectedFramework(
                            name=name,
                            version=version if version != '*' else None,
                            confidence=0.9 if dep_type == 'dependencies' else 0.7,
                            files=[str(file_path)],
                            metadata={"source": "package.json", "type": dep_type},
                            tags=self._get_framework_tags(name)
                        ))
                        
        except Exception as e:
            print(f"Error parsing package.json: {e}")
        
        return detected
    
    def _parse_cargo_toml(self, file_path: Path) -> List[DetectedFramework]:
        """Parse Cargo.toml file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = toml.loads(content)
            
            # Check dependencies
            if 'dependencies' in data:
                for name, dep_info in data['dependencies'].items():
                    if isinstance(dep_info, dict):
                        version = dep_info.get('version')
                    else:
                        version = str(dep_info)
                    
                    detected.append(DetectedFramework(
                        name=name,
                        version=version if version != '*' else None,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "Cargo.toml"},
                        tags=self._get_framework_tags(name)
                    ))
                        
        except Exception as e:
            print(f"Error parsing Cargo.toml: {e}")
        
        return detected
    
    def _parse_go_mod(self, file_path: Path) -> List[DetectedFramework]:
        """Parse go.mod file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse require statements
        require_pattern = r'require\s+([^\s]+)\s+([^\s]+)'
        matches = re.findall(require_pattern, content)
        
        for name, version in matches:
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=0.9,
                files=[str(file_path)],
                metadata={"source": "go.mod"},
                tags=self._get_framework_tags(name)
            ))
        
        return detected
    
    def _parse_pom_xml(self, file_path: Path) -> List[DetectedFramework]:
        """Parse pom.xml file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Simple regex-based parsing for dependencies
        dependency_pattern = r'<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>.*?<version>([^<]+)</version>.*?</dependency>'
        matches = re.findall(dependency_pattern, content, re.DOTALL)
        
        for group_id, artifact_id, version in matches:
            name = f"{group_id}:{artifact_id}"
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=0.8,
                files=[str(file_path)],
                metadata={"source": "pom.xml", "groupId": group_id, "artifactId": artifact_id},
                tags=self._get_framework_tags(artifact_id)  # Use artifact_id for better tag matching
            ))
        
        return detected
    
    def _parse_build_gradle(self, file_path: Path) -> List[DetectedFramework]:
        """Parse build.gradle file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse implementation statements
        implementation_pattern = r'implementation\s+["\']([^"\']+)["\']'
        matches = re.findall(implementation_pattern, content)
        
        for dep in matches:
            if ':' in dep:
                name, version = dep.split(':', 1)
            else:
                name, version = dep, None
            
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=0.8,
                files=[str(file_path)],
                metadata={"source": "build.gradle"},
                tags=self._get_framework_tags(name)
            ))
        
        return detected
    
    def _parse_dependency_string(self, dep_string: str) -> Tuple[str, Optional[str]]:
        """Parse a dependency string and return name and version."""
        dep_string = dep_string.strip()
        
        # Handle different version specifiers
        for operator in ['==', '>=', '<=', '~=', '!=', '>', '<']:
            if operator in dep_string:
                parts = dep_string.split(operator, 1)
                return parts[0].strip(), parts[1].strip()
        
        # No version specified
        return dep_string, None
    
    # Ruby parsing methods
    def _parse_gemfile(self, file_path: Path) -> List[DetectedFramework]:
        """Parse Gemfile."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse gem statements
        gem_pattern = r'gem\s+["\']([^"\']+)["\'](?:,\s*["\']([^"\']+)["\'])?'
        matches = re.findall(gem_pattern, content)
        
        for match in matches:
            name = match[0]
            version = match[1] if match[1] else None
            
            # Determine confidence based on context
            confidence = 0.9
            if 'group :development' in content or 'group :test' in content:
                # Check if this gem is in a development/test group
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if f'gem "{name}"' in line or f"gem '{name}'" in line:
                        # Look for group context above this line
                        for j in range(max(0, i-10), i):
                            if 'group :development' in lines[j] or 'group :test' in lines[j]:
                                confidence = 0.7
                                break
            
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=confidence,
                files=[str(file_path)],
                metadata={"source": "Gemfile"},
                tags=self._get_framework_tags(name)
            ))
        
        return detected
    
    def _parse_gemfile_lock(self, file_path: Path) -> List[DetectedFramework]:
        """Parse Gemfile.lock."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse SPECS section
        specs_pattern = r'^\s+([^\s]+)\s+\(([^)]+)\)'
        matches = re.findall(specs_pattern, content, re.MULTILINE)
        
        for name, version in matches:
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=0.9,
                files=[str(file_path)],
                metadata={"source": "Gemfile.lock"},
                tags=self._get_framework_tags(name)
            ))
        
        return detected
    
    # PHP parsing methods
    def _parse_composer_json(self, file_path: Path) -> List[DetectedFramework]:
        """Parse composer.json file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = json.loads(content)
            
            # Check require and require-dev sections
            for section in ['require', 'require-dev']:
                if section in data:
                    confidence = 0.9 if section == 'require' else 0.7
                    for name, version in data[section].items():
                        detected.append(DetectedFramework(
                            name=name,
                            version=version if version != '*' else None,
                            confidence=confidence,
                            files=[str(file_path)],
                            metadata={"source": "composer.json", "type": section},
                            tags=self._get_framework_tags(name)
                        ))
                        
        except Exception as e:
            print(f"Error parsing composer.json: {e}")
        
        return detected
    
    def _parse_composer_lock(self, file_path: Path) -> List[DetectedFramework]:
        """Parse composer.lock file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = json.loads(content)
            
            # Parse packages
            if 'packages' in data:
                for package in data['packages']:
                    name = package.get('name', '')
                    version = package.get('version', '')
                    
                    detected.append(DetectedFramework(
                        name=name,
                        version=version,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "composer.lock"},
                        tags=self._get_framework_tags(name)
                    ))
                        
        except Exception as e:
            print(f"Error parsing composer.lock: {e}")
        
        return detected
    
    # .NET parsing methods
    def _parse_csproj(self, file_path: Path) -> List[DetectedFramework]:
        """Parse .csproj file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse PackageReference elements
        package_ref_pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
        matches = re.findall(package_ref_pattern, content)
        
        for name, version in matches:
            detected.append(DetectedFramework(
                name=name,
                version=version,
                confidence=0.9,
                files=[str(file_path)],
                metadata={"source": ".csproj"},
                tags=self._get_framework_tags(name)
            ))
        
        # Parse ProjectReference elements
        project_ref_pattern = r'<ProjectReference\s+Include="([^"]+)"'
        matches = re.findall(project_ref_pattern, content)
        
        for project_path in matches:
            # Extract project name from path
            project_name = Path(project_path).stem
            detected.append(DetectedFramework(
                name=project_name,
                version=None,
                confidence=0.8,
                files=[str(file_path)],
                metadata={"source": ".csproj", "type": "project_reference"},
                tags=self._get_framework_tags(project_name)
            ))
        
        return detected
    
    def _parse_global_json(self, file_path: Path) -> List[DetectedFramework]:
        """Parse global.json file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = json.loads(content)
            
            # Check SDK version
            if 'sdk' in data and 'version' in data['sdk']:
                detected.append(DetectedFramework(
                    name="dotnet-sdk",
                    version=data['sdk']['version'],
                    confidence=0.9,
                    files=[str(file_path)],
                    metadata={"source": "global.json"},
                    tags=self._get_framework_tags("dotnet-sdk")
                ))
                        
        except Exception as e:
            print(f"Error parsing global.json: {e}")
        
        return detected
    
    # Elixir parsing methods
    def _parse_mix_exs(self, file_path: Path) -> List[DetectedFramework]:
        """Parse mix.exs file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse deps function
        deps_pattern = r'defp\s+deps\s+do\s*\[(.*?)\]'
        match = re.search(deps_pattern, content, re.DOTALL)
        
        if match:
            deps_content = match.group(1)
            
            # Parse individual deps
            dep_pattern = r'\{:([^,]+)(?:,\s*["\']([^"\']+)["\'])?'
            matches = re.findall(dep_pattern, deps_content)
            
            for match in matches:
                name = match[0]
                version = match[1] if match[1] else None
                
                detected.append(DetectedFramework(
                    name=name,
                    version=version,
                    confidence=0.9,
                    files=[str(file_path)],
                    metadata={"source": "mix.exs"},
                    tags=self._get_framework_tags(name)
                ))
        
        return detected
    
    # Haskell parsing methods
    def _parse_stack_yaml(self, file_path: Path) -> List[DetectedFramework]:
        """Parse stack.yaml file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = toml.loads(content)
            
            # Parse dependencies
            if 'extra-deps' in data:
                for dep in data['extra-deps']:
                    if isinstance(dep, dict):
                        name = dep.get('name', '')
                        version = dep.get('version', '')
                    else:
                        # Handle string format like "package-name-1.2.3"
                        parts = str(dep).split('-')
                        if len(parts) >= 2:
                            name = '-'.join(parts[:-1])
                            version = parts[-1]
                        else:
                            name, version = str(dep), None
                    
                    detected.append(DetectedFramework(
                        name=name,
                        version=version,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": "stack.yaml"},
                        tags=self._get_framework_tags(name)
                    ))
                        
        except Exception as e:
            print(f"Error parsing stack.yaml: {e}")
        
        return detected
    
    def _parse_cabal_file(self, file_path: Path) -> List[DetectedFramework]:
        """Parse .cabal file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse build-depends sections
        build_depends_pattern = r'build-depends:\s*(.*?)(?=\n\S|\Z)'
        matches = re.findall(build_depends_pattern, content, re.DOTALL)
        
        for match in matches:
            # Split by commas and parse each dependency
            deps = [dep.strip() for dep in match.split(',')]
            for dep in deps:
                # Handle version constraints like "base >= 4.7 && < 5"
                if '>=' in dep or '==' in dep or '<=' in dep:
                    name = dep.split('>=')[0].split('==')[0].split('<=')[0].strip()
                    # Extract version from constraint
                    version_match = re.search(r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)', dep)
                    version = version_match.group(1) if version_match else None
                else:
                    name, version = dep.strip(), None
                
                if name:
                    detected.append(DetectedFramework(
                        name=name,
                        version=version,
                        confidence=0.9,
                        files=[str(file_path)],
                        metadata={"source": ".cabal"},
                        tags=self._get_framework_tags(name)
                    ))
        
        return detected
    
    # Docker parsing methods
    def _parse_dockerfile(self, file_path: Path) -> List[DetectedFramework]:
        """Parse Dockerfile."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        # Parse FROM statements to detect base images
        from_pattern = r'FROM\s+([^\s]+)(?::([^\s]+))?'
        matches = re.findall(from_pattern, content)
        
        for match in matches:
            image = match[0]
            tag = match[1] if match[1] else None
            
            detected.append(DetectedFramework(
                name=image,
                version=tag,
                confidence=0.9,
                files=[str(file_path)],
                metadata={"source": "Dockerfile", "type": "base_image"},
                tags=self._get_framework_tags(image)
            ))
        
        # Parse RUN statements for package managers
        run_pattern = r'RUN\s+(.+)'
        run_matches = re.findall(run_pattern, content)
        
        for run_cmd in run_matches:
            # Detect package managers
            if 'apt-get install' in run_cmd:
                # Extract package names from apt-get install
                packages = re.findall(r'apt-get install -y\s+([^&|]+)', run_cmd)
                for pkg_list in packages:
                    for pkg in pkg_list.split():
                        detected.append(DetectedFramework(
                            name=pkg,
                            version=None,
                            confidence=0.8,
                            files=[str(file_path)],
                            metadata={"source": "Dockerfile", "type": "apt_package"},
                            tags=self._get_framework_tags(pkg)
                        ))
            
            elif 'pip install' in run_cmd:
                # Extract package names from pip install
                packages = re.findall(r'pip install\s+([^&|]+)', run_cmd)
                for pkg_list in packages:
                    for pkg in pkg_list.split():
                        if pkg != 'pip' and not pkg.startswith('-'):
                            detected.append(DetectedFramework(
                                name=pkg,
                                version=None,
                                confidence=0.8,
                                files=[str(file_path)],
                                metadata={"source": "Dockerfile", "type": "pip_package"},
                                tags=self._get_framework_tags(pkg)
                            ))
        
        return detected
    
    def _parse_docker_compose(self, file_path: Path) -> List[DetectedFramework]:
        """Parse docker-compose.yml file."""
        detected = []
        content = file_path.read_text(encoding='utf-8')
        
        try:
            data = toml.loads(content)
            
            # Parse services
            if 'services' in data:
                for service_name, service_config in data['services'].items():
                    if isinstance(service_config, dict):
                        # Get image
                        image = service_config.get('image', '')
                        if image:
                            if ':' in image:
                                name, version = image.split(':', 1)
                            else:
                                name, version = image, None
                            
                            detected.append(DetectedFramework(
                                name=name,
                                version=version,
                                confidence=0.9,
                                files=[str(file_path)],
                                metadata={"source": "docker-compose.yml", "service": service_name},
                                tags=self._get_framework_tags(name)
                            ))
                        
                        # Get build context
                        build = service_config.get('build', '')
                        if build and isinstance(build, str):
                            detected.append(DetectedFramework(
                                name=f"{service_name}-build",
                                version=None,
                                confidence=0.8,
                                files=[str(file_path)],
                                metadata={"source": "docker-compose.yml", "type": "build_context", "service": service_name},
                                tags=self._get_framework_tags(service_name)
                            ))
                        
        except Exception as e:
            print(f"Error parsing docker-compose.yml: {e}")
        
        return detected
    
    def _scan_for_manifest_files(self, codebase_path: Path) -> Dict[str, List[Path]]:
        """Scan for manifest files that indicate framework usage."""
        found_manifests = {}
        
        for framework, manifest_files in self.supported_frameworks.items():
            found = []
            for manifest in manifest_files:
                found.extend(codebase_path.rglob(manifest))
            if found:
                found_manifests[framework] = found
        
        return found_manifests
    
    def _analyze_python_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Python-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "requirements.txt":
                    detected.extend(self._parse_requirements_txt(file_path))
                elif file_path.name == "pyproject.toml":
                    detected.extend(self._parse_pyproject_toml(file_path))
                elif file_path.name == "setup.py":
                    detected.extend(self._parse_setup_py(file_path))
                elif file_path.name == "Pipfile":
                    detected.extend(self._parse_pipfile(file_path))
            except Exception as e:
                # Log error but continue with other files
                print(f"Error parsing {file_path}: {e}")
        
        return detected
    
    def _analyze_node_frameworks(self, manifest_files: List[Path]) -> List[DetectedFramework]:
        """Analyze Node.js-specific frameworks."""
        detected = []
        
        for file_path in manifest_files:
            try:
                if file_path.name == "package.json":
                    detected.extend(self._parse_package_json(file_path))
            except Exception as e:
                # Log error but continue with other files
                print(f"Error parsing {file_path}: {e}")
        
        return detected 