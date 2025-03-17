# MCP Template Server

A template server implementing the Model Context Protocol (MCP) with OpenAI, Anthropic, and EnrichB2B integration.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Running the Server

Development mode:
```bash
python server.py
```

Or using MCP CLI:
```bash
mcp dev server.py
```

## Features

- OpenAI GPT-4 integration
- Anthropic Claude integration
- EnrichB2B LinkedIn data integration
- FastAPI and Uvicorn server
- Environment configuration
- Example resources and tools
- Structured project layout

## Project Structure

```
.
├── .env.example          # Template for environment variables
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── enrichb2b.py        # EnrichB2B API client
└── server.py           # MCP server implementation
```

## Usage

1. Start the server
2. Connect using any MCP client
3. Use the provided tools and resources:
   - `config://app` - Get server configuration
   - `get_profile_details` - Get LinkedIn profile information
   - `get_contact_activities` - Get LinkedIn user's recent activities and posts
   - `gpt4_completion` - Generate text using GPT-4
   - `claude_completion` - Generate text using Claude
   - `analysis_prompt` - Template for text analysis

### EnrichB2B Tools

#### get_profile_details
Get detailed information about a LinkedIn profile:
```python
result = await get_profile_details(
    linkedin_url="https://www.linkedin.com/in/username",
    include_company_details=True,
    include_followers_count=True
)
```

#### get_contact_activities
Get recent activities and posts from a LinkedIn profile:
```python
result = await get_contact_activities(
    linkedin_url="https://www.linkedin.com/in/username",
    pages=1,  # Number of pages (1-50)
    comments_per_post=1,  # Comments per post (0-50)
    likes_per_post=None  # Likes per post (0-50)
)
```

## Development

To add new features:

1. Add new tools using the `@mcp.tool()` decorator
2. Add new resources using the `@mcp.resource()` decorator
3. Add new prompts using the `@mcp.prompt()` decorator

## License

MIT 