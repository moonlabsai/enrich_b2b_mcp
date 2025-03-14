# MCP Template Server

A template server implementing the Model Context Protocol (MCP) with OpenAI and Anthropic integration.

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
└── server.py           # MCP server implementation
```

## Usage

1. Start the server
2. Connect using any MCP client
3. Use the provided tools and resources:
   - `config://app` - Get server configuration
   - `gpt4_completion` - Generate text using GPT-4
   - `claude_completion` - Generate text using Claude
   - `analysis_prompt` - Template for text analysis

## Development

To add new features:

1. Add new tools using the `@mcp.tool()` decorator
2. Add new resources using the `@mcp.resource()` decorator
3. Add new prompts using the `@mcp.prompt()` decorator

## License

MIT 