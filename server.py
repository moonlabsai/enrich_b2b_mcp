"""
MCP Server Template with OpenAI, Anthropic, and EnrichB2B integration.
"""
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from openai import OpenAI
from anthropic import Anthropic
from enrichb2b import EnrichB2BConfig, EnrichB2BClient, ContactRequest, ContactActivitiesRequest

# Load environment variables
load_dotenv()

# Initialize API clients
openai_client = OpenAI()
anthropic_client = Anthropic()
enrichb2b_config = EnrichB2BConfig(os.getenv("ENRICHB2B_API_KEY", ""))
enrichb2b_client = EnrichB2BClient(enrichb2b_config)

@dataclass
class AppContext:
    """Application context with API clients"""
    openai: OpenAI
    anthropic: Anthropic
    enrichb2b: EnrichB2BClient

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    print("Starting MCP server...", file=sys.stderr)
    try:
        print("Initializing API clients...", file=sys.stderr)
        yield AppContext(
            openai=openai_client,
            anthropic=anthropic_client,
            enrichb2b=enrichb2b_client
        )
        print("API clients initialized successfully", file=sys.stderr)
    except Exception as e:
        print(f"Error during initialization: {str(e)}", file=sys.stderr)
        raise
    finally:
        print("Shutting down MCP server...", file=sys.stderr)

# Create MCP server with dependencies
mcp = FastMCP(
    "LinkedIn Research",
    dependencies=["openai", "anthropic", "enrichb2b"],
    description="A server for LinkedIn research and analysis",
    lifespan=app_lifespan
)

@mcp.resource("profile://{linkedin_url}")
async def get_profile_resource(linkedin_url: str) -> str:
    """Get LinkedIn profile data as a resource."""
    request = ContactRequest(linkedin_url=linkedin_url)
    result = enrichb2b_client.search_contact(request)
    return str(result)

@mcp.tool()
async def get_profile_details(
    ctx: Context,
    linkedin_url: str,
    include_company_details: bool = True,
    include_followers_count: bool = True
) -> str:
    """
    Get detailed profile information for a LinkedIn user.
    
    Args:
        linkedin_url: LinkedIn profile URL of the contact
        include_company_details: Whether to include company information
        include_followers_count: Whether to include follower count
    """
    enrichb2b = ctx.request_context.lifespan_context.enrichb2b
    request = ContactRequest(linkedin_url=linkedin_url)
    
    ctx.info(f"Fetching profile details for {linkedin_url}")
    result = enrichb2b.search_contact(
        request,
        include_company_details=include_company_details,
        include_followers_count=include_followers_count
    )
    return str(result)

@mcp.tool()
async def get_contact_activities(
    ctx: Context,
    linkedin_url: str,
    pages: int = 1,
    comments_per_post: int = 1
) -> str:
    """
    Get recent activities and posts from a LinkedIn profile.
    
    Args:
        linkedin_url: LinkedIn profile URL of the contact
        pages: Number of pages of activities to fetch (1-50)
        comments_per_post: Number of comment pages per post (0-50)
    """
    enrichb2b = ctx.request_context.lifespan_context.enrichb2b
    request = ContactActivitiesRequest(
        linkedin_url=linkedin_url,
        how_many_pages=pages,
        how_many_pages_comments_per_post=comments_per_post
    )
    
    ctx.info(f"Fetching activities for {linkedin_url}")
    await ctx.report_progress(0, 1)
    result = enrichb2b.search_contact_activities(request)
    await ctx.report_progress(1, 1)
    return str(result)

@mcp.prompt()
def research_profile(linkedin_url: str) -> str:
    """Create a prompt for researching a LinkedIn profile."""
    return f"""Please research this LinkedIn profile:

{linkedin_url}

Use the available tools to:
1. Get detailed profile information
2. Analyze their recent activities
3. Summarize key findings about their professional background and engagement"""

@mcp.prompt()
def analyze_activities(linkedin_url: str) -> str:
    """Create a prompt for analyzing LinkedIn activities."""
    return f"""Please analyze the recent activities of this LinkedIn profile:

{linkedin_url}

Focus on:
1. Types of content shared
2. Engagement patterns
3. Key topics and interests
4. Professional network interactions"""

if __name__ == "__main__":
    mcp.run() 