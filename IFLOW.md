# Project Context for iFlow CLI

## Project Type
This is a Python-based AI chat client testing tool that supports multiple AI providers. The project uses a modular architecture with uv as the package manager.

## Directory Overview
The project is structured as follows:
- Root directory: Contains main entry point, configuration files, and project metadata
- dify_chat_tester/: Core module containing AI provider implementations and utilities
- Configuration files: Uses config.env for runtime configuration
- Template files: Includes Excel template for batch testing

## Key Files and Their Purpose

### Root Directory
- `main.py`: Main program entry point with CLI interface and orchestration logic
- `pyproject.toml`: Project metadata, dependencies, and build configuration
- `uv.toml`: uv package manager configuration with PyPI mirror settings
- `config.env.example`: Template for runtime configuration
- `README.md`: Project documentation with usage instructions
- `dify_chat_tester_template.xlsx`: Excel template for batch testing mode

### dify_chat_tester/ Module
- `ai_providers.py`: Abstract base class and implementations for AI providers (Dify, OpenAI, iFlow)
- `config_loader.py`: Configuration management system that loads settings from config.env
- `terminal_ui.py`: Terminal UI utilities with Rich library for beautiful CLI interfaces
- `README.md`: Module-specific documentation

## Supported AI Providers

### 1. Dify
- Professional LLM application development platform
- Supports private deployment
- API key format: `app-xxxxx`
- Features: Application ID extraction, redirect handling

### 2. OpenAI Compatible
- Universal adapter for any OpenAI-format API
- Supports custom base URLs
- Custom model names supported
- Features: Conversation history management

### 3. iFlow
- Multi-model AI platform
- Pre-configured base URL: `https://apis.iflow.cn/v1`
- Built-in models: qwen3-max, kimi-k2-0905, glm-4.6, deepseek-v3.2
- Features: Automatic streaming fallback to non-streaming

## Running the Application

### Prerequisites
- Python 3.7+
- uv package manager (recommended)

### Installation and Setup
```bash
# Install dependencies
uv sync

# Copy configuration template
cp config.env.example config.env

# Edit configuration as needed
# (Set AI provider keys, roles, etc.)
```

### Running the Program
```bash
# Run with uv (recommended)
uv run python main.py

# Or activate virtual environment first
source .venv/bin/activate  # Linux/macOS
python main.py
```

### Testing
```bash
# Run tests (if implemented)
uv run pytest

# Code quality checks
uv run ruff check .
```

## Configuration

The application uses `config.env` for configuration. Key settings include:
- `ROLES`: Comma-separated list of available roles
- `AI_PROVIDERS`: Supported AI providers configuration
- `BATCH_REQUEST_INTERVAL`: Delay between batch requests (seconds)
- `CHAT_LOG_FILE_NAME`: Output file for chat logs
- Model lists for each provider

## Usage Patterns

### Interactive Chat Mode
- Real-time conversation with AI
- Multi-turn dialogue support
- Commands: `exit` to quit, `/new` to reset context

### Batch Query Mode
- Process questions from Excel files
- Real-time result writing
- Detailed logging with timestamps
- Configurable request intervals

## Development Conventions

### Code Style
- Uses ruff for linting and formatting
- Type hints with Optional typing
- Abstract base classes for extensibility
- Thread-safe operations for streaming

### Error Handling
- Comprehensive exception handling
- Graceful fallbacks for API issues
- User-friendly error messages
- Detailed logging for debugging

### Security
- API keys hidden during input
- No hardcoded credentials
- Secure password entry with getpass
- Config files in .gitignore

## Architecture Notes

### Modular Design
- Clear separation of concerns
- Provider abstraction for easy extension
- Configuration-driven behavior
- Reusable UI components

### Key Features
- Streaming responses with indicators
- Excel integration for batch processing
- Multi-provider support
- Rich terminal UI experience

## Common Tasks

### Adding a New AI Provider
1. Create new provider class in `ai_providers.py`
2. Inherit from `AIProvider` abstract base class
3. Implement required methods: `get_models()` and `send_message()`
4. Update provider configuration in config.env

### Modifying UI Elements
- Edit `terminal_ui.py` for CLI interface changes
- Uses Rich library for styling and layouts
- Icons and colors defined in Icons class

### Configuration Changes
- Edit `config.env.example` for new defaults
- Update `config_loader.py` for new config types
- Restart application for changes to take effect