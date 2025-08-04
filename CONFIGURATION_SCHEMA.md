# LLMContext Configuration Schema

This document describes the expected schema for the `.llmcontext.json` configuration file used by LLMContext.

## Overview

The `.llmcontext.json` file is the central configuration file for LLMContext projects. It defines which tools and frameworks to track, their versions, and various project settings.

## File Location

The configuration file should be placed in the root directory of your project:
```
your-project/
├── .llmcontext.json    # Configuration file
├── package.json
├── requirements.txt
└── ...
```

## Current Schema (Simplified)

The current implementation uses a simplified schema focused on tool tracking:

```json
{
  "stack": [
    "react@18",
    "tailwind@3.3",
    "fastapi@0.104.0",
    "django@4.2"
  ]
}
```

### Stack Array

The `stack` array contains the tools and frameworks to track. Each entry can be:

- **Tool name only**: `"react"` (uses latest version)
- **Tool with version**: `"react@18"` (specific version)
- **Tool with semantic version**: `"react@18.2.0"` (exact version)

## Extended Schema (Future Implementation)

The following schema represents the planned full configuration structure:

```json
{
  "version": "1.0.0",
  "project": {
    "name": "my-project",
    "description": "A modern web application",
    "frameworks": [],
    "documentation_dir": "docs",
    "cache_dir": ".llmcontext_cache",
    "ignore_patterns": [
      "node_modules/**",
      "venv/**",
      ".git/**",
      "dist/**",
      "build/**"
    ]
  },
  "settings": {
    "auto_detect": true,
    "include_dev_dependencies": false,
    "compression_level": "medium",
    "embedding_model": "text-embedding-3-large",
    "max_context_length": 4000,
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "similarity_threshold": 0.5,
    "max_concurrent_requests": 5
  },
  "api": {
    "host": "127.0.0.1",
    "port": 8001,
    "enable_cors": true,
    "rate_limit": 100,
    "timeout": 30
  },
  "stack": [
    "react@18",
    "tailwind@3.3",
    "fastapi@0.104.0",
    "django@4.2"
  ],
  "tools": {
    "enabled": ["react", "tailwind", "fastapi", "django"],
    "ignored": ["lodash", "moment", "jquery"],
    "tool_configs": {
      "react": {
        "version": "18.2.0",
        "detection_patterns": [
          "package.json",
          "src/**/*.jsx",
          "src/**/*.tsx",
          "*.jsx",
          "*.tsx"
        ],
        "documentation_sources": [
          "https://react.dev",
          "https://react.dev/reference"
        ],
        "priority": "high",
        "auto_update": true,
        "custom_prompts": {
          "summarization": "Custom prompt for React summarization",
          "context_extraction": "Custom prompt for React context"
        }
      },
      "tailwind": {
        "version": "3.3.0",
        "detection_patterns": [
          "tailwind.config.js",
          "tailwind.config.ts",
          "*.css"
        ],
        "documentation_sources": [
          "https://tailwindcss.com/docs"
        ],
        "priority": "medium",
        "auto_update": false
      }
    }
  },
  "detection": {
    "enabled": true,
    "scan_on_init": true,
    "auto_add_detected": false,
    "confidence_threshold": 0.7,
    "file_patterns": {
      "javascript": ["*.js", "*.jsx", "*.ts", "*.tsx"],
      "python": ["*.py", "*.pyx"],
      "ruby": ["*.rb", "Gemfile"],
      "php": ["*.php", "composer.json"],
      "dotnet": ["*.csproj", "*.vbproj"],
      "elixir": ["mix.exs", "*.ex", "*.exs"],
      "haskell": ["*.cabal", "stack.yaml"]
    }
  },
  "documentation": {
    "collection": {
      "enabled": true,
      "auto_collect": false,
      "force_refresh": false,
      "sources": {
        "official_docs": true,
        "github": true,
        "npm_packages": true,
        "pypi_packages": true
      }
    },
    "processing": {
      "chunk_strategy": "hybrid",
      "target_chunk_size": 1000,
      "min_chunk_size": 800,
      "max_chunk_size": 1200,
      "chunk_overlap": 100,
      "preserve_formatting": true
    },
    "summarization": {
      "enabled": true,
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "max_tokens": 4000,
      "concurrent_requests": 5,
      "retry_attempts": 3
    }
  },
  "embeddings": {
    "model": "text-embedding-3-large",
    "batch_size": 100,
    "dimensions": 3072,
    "storage": {
      "type": "chromadb",
      "persist_directory": "chroma_db",
      "collection_name": "llmcontext_docs"
    }
  },
  "context_cache": {
    "enabled": true,
    "directory": ".llmcontext/context",
    "auto_save": true,
    "max_cache_size": "1GB",
    "cleanup_interval": "7d"
  },
  "sidecar": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8001,
    "auto_start": false,
    "reload": true,
    "log_level": "info"
  }
}
```

## Schema Reference

### Root Level Properties

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `version` | string | No | "1.0.0" | Configuration schema version |
| `project` | object | No | - | Project metadata and settings |
| `settings` | object | No | - | Global application settings |
| `api` | object | No | - | API server configuration |
| `stack` | array | Yes | [] | List of tools to track |
| `tools` | object | No | - | Detailed tool configurations |
| `detection` | object | No | - | Framework detection settings |
| `documentation` | object | No | - | Documentation processing settings |
| `embeddings` | object | No | - | Embedding generation settings |
| `context_cache` | object | No | - | Context caching settings |
| `sidecar` | object | No | - | Sidecar server settings |

### Project Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `name` | string | No | - | Project name |
| `description` | string | No | - | Project description |
| `frameworks` | array | No | [] | Legacy frameworks array |
| `documentation_dir` | string | No | "docs" | Documentation output directory |
| `cache_dir` | string | No | ".llmcontext_cache" | Cache directory |
| `ignore_patterns` | array | No | [] | Glob patterns to ignore |

### Settings Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `auto_detect` | boolean | No | true | Enable automatic framework detection |
| `include_dev_dependencies` | boolean | No | false | Include dev dependencies in detection |
| `compression_level` | string | No | "medium" | Documentation compression level |
| `embedding_model` | string | No | "text-embedding-3-large" | OpenAI embedding model |
| `max_context_length` | integer | No | 4000 | Maximum context length in tokens |
| `chunk_size` | integer | No | 1000 | Default chunk size in tokens |
| `chunk_overlap` | integer | No | 100 | Default chunk overlap in tokens |
| `similarity_threshold` | number | No | 0.5 | Default similarity threshold |
| `max_concurrent_requests` | integer | No | 5 | Maximum concurrent API requests |

### API Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `host` | string | No | "127.0.0.1" | API server host |
| `port` | integer | No | 8001 | API server port |
| `enable_cors` | boolean | No | true | Enable CORS |
| `rate_limit` | integer | No | 100 | Rate limit per minute |
| `timeout` | integer | No | 30 | Request timeout in seconds |

### Stack Array

The `stack` array contains tool entries in the format:
- `"toolname"` - Tool without version (uses latest)
- `"toolname@version"` - Tool with specific version
- `"toolname@major.minor.patch"` - Tool with exact version

### Tools Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `enabled` | array | No | [] | List of enabled tools |
| `ignored` | array | No | [] | List of ignored packages |
| `tool_configs` | object | No | {} | Detailed tool configurations |

### Tool Config Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `version` | string | No | - | Tool version |
| `detection_patterns` | array | No | [] | File patterns for detection |
| `documentation_sources` | array | No | [] | Documentation source URLs |
| `priority` | string | No | "normal" | Processing priority |
| `auto_update` | boolean | No | false | Auto-update documentation |
| `custom_prompts` | object | No | {} | Custom prompts for processing |

### Detection Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `enabled` | boolean | No | true | Enable framework detection |
| `scan_on_init` | boolean | No | true | Scan on initialization |
| `auto_add_detected` | boolean | No | false | Auto-add detected frameworks |
| `confidence_threshold` | number | No | 0.7 | Minimum confidence for detection |
| `file_patterns` | object | No | {} | File patterns by language |

### Documentation Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `collection` | object | No | - | Documentation collection settings |
| `processing` | object | No | - | Documentation processing settings |
| `summarization` | object | No | - | Summarization settings |

### Embeddings Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `model` | string | No | "text-embedding-3-large" | OpenAI embedding model |
| `batch_size` | integer | No | 100 | Batch size for embedding generation |
| `dimensions` | integer | No | 3072 | Embedding dimensions |
| `storage` | object | No | - | Storage configuration |

### Context Cache Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `enabled` | boolean | No | true | Enable context caching |
| `directory` | string | No | ".llmcontext/context" | Cache directory |
| `auto_save` | boolean | No | true | Auto-save context chunks |
| `max_cache_size` | string | No | "1GB" | Maximum cache size |
| `cleanup_interval` | string | No | "7d" | Cache cleanup interval |

### Sidecar Object

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `enabled` | boolean | No | true | Enable sidecar server |
| `host` | string | No | "127.0.0.1" | Sidecar host |
| `port` | integer | No | 8001 | Sidecar port |
| `auto_start` | boolean | No | false | Auto-start sidecar |
| `reload` | boolean | No | true | Enable auto-reload |
| `log_level` | string | No | "info" | Log level |

## Supported Tools

### Web Frameworks
- `react` - React.js
- `vue` - Vue.js
- `angular` - Angular
- `svelte` - Svelte
- `nextjs` - Next.js
- `nuxt` - Nuxt.js
- `remix` - Remix
- `astro` - Astro

### CSS Frameworks
- `tailwind` - Tailwind CSS
- `bootstrap` - Bootstrap
- `bulma` - Bulma
- `foundation` - Foundation

### Backend Frameworks
- `fastapi` - FastAPI
- `django` - Django
- `flask` - Flask
- `express` - Express.js
- `laravel` - Laravel
- `rails` - Ruby on Rails
- `spring` - Spring Boot
- `gin` - Gin (Go)
- `actix` - Actix (Rust)

### Infrastructure & Cloud
- `docker` - Docker
- `kubernetes` - Kubernetes
- `terraform` - Terraform
- `aws` - AWS
- `azure` - Azure
- `gcp` - Google Cloud Platform

### Additional Ecosystems
- `ruby` - Ruby
- `php` - PHP
- `dotnet` - .NET
- `elixir` - Elixir
- `haskell` - Haskell

## Examples

### Minimal Configuration
```json
{
  "stack": ["react", "tailwind"]
}
```

### Basic Configuration
```json
{
  "version": "1.0.0",
  "project": {
    "name": "my-react-app",
    "description": "A React application with Tailwind CSS"
  },
  "stack": [
    "react@18",
    "tailwind@3.3",
    "fastapi@0.104.0"
  ],
  "settings": {
    "auto_detect": true,
    "include_dev_dependencies": false
  }
}
```

### Advanced Configuration
```json
{
  "version": "1.0.0",
  "project": {
    "name": "full-stack-app",
    "description": "Full-stack application with React frontend and FastAPI backend",
    "documentation_dir": "docs",
    "cache_dir": ".llmcontext_cache",
    "ignore_patterns": [
      "node_modules/**",
      "venv/**",
      ".git/**"
    ]
  },
  "settings": {
    "auto_detect": true,
    "include_dev_dependencies": true,
    "compression_level": "high",
    "embedding_model": "text-embedding-3-large",
    "max_context_length": 4000,
    "similarity_threshold": 0.7
  },
  "stack": [
    "react@18.2.0",
    "tailwind@3.3.0",
    "fastapi@0.104.0",
    "django@4.2.0"
  ],
  "tools": {
    "enabled": ["react", "tailwind", "fastapi", "django"],
    "ignored": ["lodash", "moment"],
    "tool_configs": {
      "react": {
        "version": "18.2.0",
        "detection_patterns": ["package.json", "src/**/*.jsx"],
        "documentation_sources": ["https://react.dev"],
        "priority": "high",
        "auto_update": true
      }
    }
  },
  "detection": {
    "enabled": true,
    "scan_on_init": true,
    "auto_add_detected": false,
    "confidence_threshold": 0.8
  },
  "documentation": {
    "collection": {
      "enabled": true,
      "auto_collect": false,
      "force_refresh": false
    },
    "processing": {
      "chunk_strategy": "hybrid",
      "target_chunk_size": 1000,
      "chunk_overlap": 100
    },
    "summarization": {
      "enabled": true,
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "concurrent_requests": 5
    }
  },
  "embeddings": {
    "model": "text-embedding-3-large",
    "batch_size": 100,
    "storage": {
      "type": "chromadb",
      "persist_directory": "chroma_db",
      "collection_name": "llmcontext_docs"
    }
  },
  "context_cache": {
    "enabled": true,
    "directory": ".llmcontext/context",
    "auto_save": true,
    "max_cache_size": "1GB"
  },
  "sidecar": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8001,
    "auto_start": false,
    "reload": true
  }
}
```

## Migration Guide

### From Current to Extended Schema

1. **Backup your current configuration**:
   ```bash
   cp .llmcontext.json .llmcontext.json.backup
   ```

2. **Convert stack to extended format**:
   ```json
   // Current
   {
     "stack": ["react@18", "tailwind@3.3"]
   }
   
   // Extended
   {
     "version": "1.0.0",
     "project": {
       "name": "my-project"
     },
     "stack": ["react@18", "tailwind@3.3"],
     "tools": {
       "enabled": ["react", "tailwind"],
       "tool_configs": {
         "react": {
           "version": "18"
         },
         "tailwind": {
           "version": "3.3"
         }
       }
     }
   }
   ```

3. **Add additional settings as needed**:
   - Configure detection patterns
   - Set up documentation sources
   - Adjust processing parameters
   - Configure caching behavior

## Validation

The configuration file should be valid JSON. You can validate it using:

```bash
# Using Python
python -m json.tool .llmcontext.json

# Using jq (if installed)
jq '.' .llmcontext.json

# Using online JSON validators
# https://jsonlint.com/
```

## Environment Variables

Some settings can be overridden using environment variables:

| Environment Variable | Config Property | Description |
|---------------------|-----------------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key for embeddings and summarization |
| `LLMCONTEXT_HOST` | `api.host` | API server host |
| `LLMCONTEXT_PORT` | `api.port` | API server port |
| `LLMCONTEXT_CACHE_DIR` | `context_cache.directory` | Context cache directory |
| `LLMCONTEXT_DOCS_DIR` | `project.documentation_dir` | Documentation directory |

## Best Practices

1. **Version Control**: Include `.llmcontext.json` in version control
2. **Sensitive Data**: Don't include API keys in the config file
3. **Team Sharing**: Use consistent tool versions across team
4. **Regular Updates**: Keep tool versions up to date
5. **Backup**: Regularly backup your configuration
6. **Validation**: Validate JSON syntax before committing
7. **Documentation**: Add comments to complex configurations
8. **Testing**: Test configuration changes in development first

## Troubleshooting

### Common Issues

1. **Invalid JSON**: Use a JSON validator to check syntax
2. **Missing Tools**: Ensure tools are in the supported list
3. **Version Conflicts**: Check for version compatibility
4. **Path Issues**: Use absolute paths for external directories
5. **Permission Errors**: Check file and directory permissions

### Debug Mode

Enable debug logging by setting the log level:

```json
{
  "sidecar": {
    "log_level": "debug"
  }
}
```

### Reset Configuration

To reset to default configuration:

```bash
rm .llmcontext.json
llmcontext init
```

## Support

For issues with configuration:

1. Check the [LLMContext documentation](https://github.com/your-repo/llmcontext)
2. Validate your JSON syntax
3. Review the schema reference above
4. Check environment variables
5. Enable debug logging
6. Open an issue on GitHub with your configuration 