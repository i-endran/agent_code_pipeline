from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import MCPServer, Tool
from app.schemas.schemas import MCPServerCreate, MCPServerResponse, ToolResponse
from app.services.mcp_service import mcp_service

router = APIRouter()

@router.post("/servers", response_model=MCPServerResponse, status_code=201)
async def create_mcp_server(
    server: MCPServerCreate,
    db: Session = Depends(get_db)
):
    """Register a new MCP server."""
    db_server = MCPServer(
        name=server.name,
        url=server.url,
        auth_token=server.auth_token,
        is_active=server.is_active
    )
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    
    # Auto-refresh tools upon registration
    await mcp_service.refresh_tools(db_server.id, db)
    db.refresh(db_server)
    
    return db_server

@router.get("/servers", response_model=List[MCPServerResponse])
async def list_mcp_servers(db: Session = Depends(get_db)):
    """List all configured MCP servers."""
    return db.query(MCPServer).all()

@router.post("/servers/{server_id}/refresh")
async def refresh_server_tools(server_id: int, db: Session = Depends(get_db)):
    """Manually refresh tools for a specific MCP server."""
    return await mcp_service.refresh_tools(server_id, db)

@router.get("/tools", response_model=List[ToolResponse])
async def list_all_tools(db: Session = Depends(get_db)):
    """List all available tools across all servers."""
    return db.query(Tool).all()

@router.delete("/servers/{server_id}", status_code=204)
async def delete_mcp_server(server_id: int, db: Session = Depends(get_db)):
    """Delete an MCP server and its associated tools."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    db.query(Tool).filter(Tool.mcp_server_id == server_id).delete()
    db.delete(server)
    db.commit()
    return None
