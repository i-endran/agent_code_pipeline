import logging
import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.models import MCPServer, Tool

logger = logging.getLogger(__name__)

class MCPService:
    """
    Service for Model Context Protocol (MCP) integrations.
    Managed connections to MCP servers and tool execution.
    """
    
    async def refresh_tools(self, server_id: int, db: Session) -> List[Dict[str, Any]]:
        """Fetch tools from MCP server and update local registry."""
        server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
        if not server:
            raise ValueError(f"MCP Server {server_id} not found")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Simplified MCP 'list_tools' call
                response = await client.post(f"{server.url}/tools/list", headers={
                    "Authorization": f"Bearer {server.auth_token}" if server.auth_token else ""
                })
                
                if response.status_code != 200:
                    logger.error(f"Failed to fetch tools from {server.name}: {response.text}")
                    return []
                
                tools_data = response.json().get("tools", [])
                
                # Update local DB
                # First remove old tools for this server
                db.query(Tool).filter(Tool.mcp_server_id == server_id).delete()
                
                registered_tools = []
                for t in tools_data:
                    new_tool = Tool(
                        name=t["name"],
                        description=t.get("description"),
                        parameters=t.get("parameters"),
                        mcp_server_id=server_id
                    )
                    db.add(new_tool)
                    registered_tools.append(t)
                
                db.commit()
                return registered_tools
            except Exception as e:
                logger.error(f"MCP refresh failed for {server.name}: {e}")
                return []

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], db: Session) -> Any:
        """Execute a tool via its MCP server."""
        tool = db.query(Tool).filter(Tool.name == tool_name).first()
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        server = tool.mcp_server
        if not server or not server.is_active:
            raise ValueError(f"MCP Server for tool {tool_name} is inactive or missing")
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{server.url}/tools/execute",
                json={"name": tool_name, "arguments": arguments},
                headers={"Authorization": f"Bearer {server.auth_token}" if server.auth_token else ""}
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"MCP Execution failed: {response.text}")
                
            return response.json().get("result")

mcp_service = MCPService()
