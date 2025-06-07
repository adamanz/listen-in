"""Entry point for running Listen-in as a module."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()