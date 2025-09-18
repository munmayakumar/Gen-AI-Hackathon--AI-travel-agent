# setup_mcp_servers.py
import subprocess
import os
import sys

def install_mcp_servers():
    """Install the required MCP servers for the travel planner"""
    servers = [
        "@modelcontextprotocol/server-airbnb",
        "@modelcontextprotocol/server-booking",
        "@modelcontextprotocol/server-expedia",
        "@modelcontextprotocol/server-skyscanner",
        "@modelcontextprotocol/server-google-flights",
        "@modelcontextprotocol/server-viator",
        "@modelcontextprotocol/server-getyourguide",
    ]
    
    print("Installing MCP servers...")
    for server in servers:
        try:
            subprocess.run(["npm", "install", "-g", server], check=True)
            print(f"✓ Installed {server}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {server}: {e}")
    
    print("MCP server installation completed.")

if __name__ == "__main__":
    install_mcp_servers()