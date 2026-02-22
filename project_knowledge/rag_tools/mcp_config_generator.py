#!/usr/bin/env python3
"""Generate MCP configuration files for AI coding tools."""

import argparse
import json
from pathlib import Path


# Supported tools and their config formats
SUPPORTED_TOOLS = [
    "claude-code",
    "claude-desktop",
    "vscode",
    "cursor",
    "windsurf",
    "zed",
]


def generate_sse_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate SSE-based MCP configuration.

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        MCP configuration dictionary.
    """
    return {
        "mcpServers": {
            "project-docs": {
                "type": "sse",
                "url": f"http://localhost:{haystack_port}/sse",
                "description": "Haystack RAG for project documentation (REF, BRD, PRD, SPEC, etc.)",
            },
            "research-kb": {
                "type": "sse",
                "url": f"http://localhost:{lightrag_port}/sse",
                "description": "LightRAG for research and cross-document analysis",
            },
        }
    }


def generate_claude_desktop_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
    lightrag_api_key: str = "lightragsecretkey",
    pipelines_dir: str | None = None,
) -> dict:
    """Generate Claude Desktop MCP configuration (stdio transport).

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.
        lightrag_api_key: LightRAG API key.
        pipelines_dir: Path to Haystack pipelines directory.

    Returns:
        MCP configuration dictionary.
    """
    if pipelines_dir is None:
        pipelines_dir = str(Path(__file__).parent.parent / "haystack" / "pipelines")

    return {
        "mcpServers": {
            "project-docs": {
                "command": "hayhooks",
                "args": ["mcp", "--host", "localhost", "--port", str(haystack_port)],
                "env": {
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}",
                    "PG_CONN_STR": "postgresql://raguser:ragpass@localhost:5432/ragdb",
                },
                "description": "Haystack RAG for project documentation",
            },
            "research-kb": {
                "command": "python",
                "args": ["-m", "daniel_lightrag_mcp"],
                "env": {
                    "LIGHTRAG_BASE_URL": f"http://localhost:{lightrag_port}",
                    "LIGHTRAG_API_KEY": lightrag_api_key,
                    "LIGHTRAG_TIMEOUT": "60",
                },
                "description": "LightRAG for research and analysis",
            },
        }
    }


def generate_vscode_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate VS Code settings.json MCP configuration.

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        VS Code settings dictionary.
    """
    return {
        "claude.mcpServers": {
            "project-docs": {
                "url": f"http://localhost:{haystack_port}/sse",
                "transport": "sse",
            },
            "research-kb": {
                "url": f"http://localhost:{lightrag_port}/sse",
                "transport": "sse",
            },
        }
    }


def generate_cursor_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate Cursor IDE MCP configuration.

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        MCP configuration dictionary.
    """
    return {
        "mcpServers": {
            "project-docs": {
                "url": f"http://localhost:{haystack_port}/sse",
                "transport": "sse",
                "description": "Haystack RAG for project documentation",
            },
            "research-kb": {
                "url": f"http://localhost:{lightrag_port}/sse",
                "transport": "sse",
                "description": "LightRAG for research and analysis",
            },
        }
    }


def generate_windsurf_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate Windsurf (Codeium) MCP configuration.

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        MCP configuration dictionary.
    """
    return {
        "mcpServers": {
            "project-docs": {
                "serverUrl": f"http://localhost:{haystack_port}/sse",
                "transport": "sse",
                "description": "Haystack RAG for project documentation",
            },
            "research-kb": {
                "serverUrl": f"http://localhost:{lightrag_port}/sse",
                "transport": "sse",
                "description": "LightRAG for research and analysis",
            },
        }
    }


def generate_zed_config(
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate Zed editor MCP configuration.

    Args:
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        Zed settings dictionary.
    """
    return {
        "language_models": {
            "mcp": {
                "servers": {
                    "project-docs": {
                        "url": f"http://localhost:{haystack_port}/sse",
                        "transport": "sse",
                    },
                    "research-kb": {
                        "url": f"http://localhost:{lightrag_port}/sse",
                        "transport": "sse",
                    },
                }
            }
        }
    }


def get_config_paths() -> dict[str, Path]:
    """Get standard configuration file paths.

    Returns:
        Dictionary of config type to path.
    """
    home = Path.home()

    paths = {
        "claude-code": home / ".claude" / "mcp.json",
        "claude-desktop (macOS)": home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        "claude-desktop (Linux)": home / ".config" / "Claude" / "claude_desktop_config.json",
        "claude-desktop (Windows)": home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        "vscode (user)": home / ".config" / "Code" / "User" / "settings.json",
        "vscode (project)": Path(".vscode") / "settings.json",
        "cursor": home / ".cursor" / "mcp.json",
        "windsurf": home / ".windsurf" / "mcp.json",
        "zed": home / ".config" / "zed" / "settings.json",
    }

    return paths


def generate_config(
    tool: str,
    haystack_port: int = 1416,
    lightrag_port: int = 9621,
) -> dict:
    """Generate configuration for specified tool.

    Args:
        tool: Tool name.
        haystack_port: Haystack API port.
        lightrag_port: LightRAG API port.

    Returns:
        Configuration dictionary.
    """
    generators = {
        "claude-code": generate_sse_config,
        "claude-desktop": generate_claude_desktop_config,
        "vscode": generate_vscode_config,
        "cursor": generate_cursor_config,
        "windsurf": generate_windsurf_config,
        "zed": generate_zed_config,
    }

    generator = generators.get(tool)
    if not generator:
        raise ValueError(f"Unknown tool: {tool}. Supported: {SUPPORTED_TOOLS}")

    return generator(haystack_port=haystack_port, lightrag_port=lightrag_port)


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP configuration files for AI coding tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Claude Code config
  python mcp_config_generator.py --tool claude-code > ~/.claude/mcp.json

  # Generate VS Code settings
  python mcp_config_generator.py --tool vscode > .vscode/settings.json

  # Generate all configs to mcp/ directory
  python mcp_config_generator.py --all --output-dir ./mcp/

  # Show standard config paths
  python mcp_config_generator.py --show-paths
""",
    )
    parser.add_argument(
        "--tool", "-t",
        choices=SUPPORTED_TOOLS,
        help="Target tool to generate config for",
    )
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--output-dir", help="Output directory for --all")
    parser.add_argument("--all", action="store_true", help="Generate configs for all tools")
    parser.add_argument("--haystack-port", type=int, default=1416)
    parser.add_argument("--lightrag-port", type=int, default=9621)
    parser.add_argument("--show-paths", action="store_true", help="Show config file paths")
    args = parser.parse_args()

    if args.show_paths:
        print("Standard MCP configuration paths:\n")
        for name, path in get_config_paths().items():
            exists = "✓" if path.exists() else "✗"
            print(f"  {exists} {name}: {path}")
        return 0

    if args.all:
        output_dir = Path(args.output_dir) if args.output_dir else Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)

        filenames = {
            "claude-code": "claude_code_config.json",
            "claude-desktop": "claude_desktop_config.json",
            "vscode": "vscode_settings.json",
            "cursor": "cursor_config.json",
            "windsurf": "windsurf_config.json",
            "zed": "zed_settings.json",
        }

        for tool in SUPPORTED_TOOLS:
            config = generate_config(
                tool,
                haystack_port=args.haystack_port,
                lightrag_port=args.lightrag_port,
            )
            output_path = output_dir / filenames[tool]
            output_path.write_text(json.dumps(config, indent=2))
            print(f"Generated: {output_path}")

        return 0

    if not args.tool:
        parser.error("--tool is required (or use --all)")

    # Generate single config
    config = generate_config(
        args.tool,
        haystack_port=args.haystack_port,
        lightrag_port=args.lightrag_port,
    )

    output_json = json.dumps(config, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json)
        print(f"Configuration written to: {output_path}")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    exit(main())
