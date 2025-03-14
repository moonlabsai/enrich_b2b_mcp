"""
MCP Server Template with OpenAI and Anthropic integration.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from mcp.server.fastmcp import Context, FastMCP, Image, types
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize API clients
openai_client = OpenAI()
anthropic_client = Anthropic()

# Create FastAPI app
app = FastAPI(title="MCP Template Server")

# Create MCP server
mcp = FastMCP(
    "MCP Template",
    dependencies=["openai", "anthropic", "pandas"],
    description="A template MCP server with OpenAI and Anthropic integration"
)

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage application lifecycle."""
    # Initialize resources on startup
    print("Starting MCP server...")
    try:
        yield {
            "openai_client": openai_client,
            "anthropic_client": anthropic_client
        }
    finally:
        # Cleanup on shutdown
        print("Shutting down MCP server...")

# Pass lifespan to server
mcp = FastMCP("MCP Template", lifespan=app_lifespan)

# Example Resource
@mcp.resource("config://app")
def get_config() -> str:
    """Get application configuration."""
    return "Template MCP Server Configuration"

# Example Tool - OpenAI Integration
@mcp.tool()
async def gpt4_completion(ctx: Context, prompt: str) -> str:
    """Generate text using GPT-4."""
    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# Example Tool - Anthropic Integration
@mcp.tool()
async def claude_completion(ctx: Context, prompt: str) -> str:
    """Generate text using Claude."""
    message = anthropic_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    return message.content[0].text

# Example Prompt
@mcp.prompt()
def analysis_prompt(text: str) -> str:
    """Create an analysis prompt template."""
    return f"Please analyze the following text:\n\n{text}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development"
    ) 