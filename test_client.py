import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_linkedin_tools():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            response = await session.list_tools()
            print("\nAvailable tools:", [tool.name for tool in response.tools])
            
            # Test profile lookup
            try:
                profile = await session.call_tool(
                    "get_profile_details",
                    {
                        "linkedin_url": "https://www.linkedin.com/in/davidstubbss",
                        "include_company_details": True
                    }
                )
                print("\nProfile:", profile.content)
            except Exception as e:
                print("\nError fetching profile:", str(e))
            
            # Test activities lookup
            try:
                activities = await session.call_tool(
                    "get_contact_activities",
                    {
                        "linkedin_url": "https://www.linkedin.com/in/davidstubbss",
                        "pages": 1
                    }
                )
                print("\nActivities:", activities.content)
            except Exception as e:
                print("\nError fetching activities:", str(e))

if __name__ == "__main__":
    asyncio.run(test_linkedin_tools()) 