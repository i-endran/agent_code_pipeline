"""
Agents API Routes

Agent configuration retrieval and management.
"""

from fastapi import APIRouter

from app.services.agent_config import (
    get_agent_configs,
    get_agent_config,
    calculate_token_estimate
)

router = APIRouter()


@router.get("/status")
async def list_agents():
    """
    Get all agent configurations.
    
    Returns configuration for all 6 agents including models, 
    hyperparameters, and token estimates.
    """
    configs = get_agent_configs()
    estimates = calculate_token_estimate(list(configs.keys()))
    
    agents = {}
    for agent_id, config in configs.items():
        agents[agent_id] = {
            "name": config["name"],
            "description": config.get("description", ""),
            "model": config["model"],
            "provider": config["provider"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "estimated_tokens": estimates["agents"].get(agent_id, {}).get("tokens", 0)
        }
    
    return {
        "agents": agents,
        "total_estimated_tokens": estimates["total_tokens"],
        "total_estimated_cost": estimates["total_cost"]
    }


@router.get("/activity")
async def get_agent_activity():
    """
    Get real-time activity status for all agents.
    
    Returns what each agent is currently doing and what's next in their queue.
    """
    from app.services.status_service import status_service
    return status_service.get_all_statuses()


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get configuration for a specific agent.
    
    Agent IDs: scribe, architect, forge, herald, sentinel, phoenix
    """
    config = get_agent_config(agent_id)
    if not config:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    return {
        "id": agent_id,
        **config
    }


@router.get("/{agent_id}/prompt")
async def get_agent_prompt(agent_id: str):
    """
    Get the system prompt for a specific agent.
    
    Useful for debugging and understanding agent behavior.
    """
    config = get_agent_config(agent_id)
    if not config:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    
    return {
        "id": agent_id,
        "name": config["name"],
        "system_prompt": config.get("system_prompt", "")
    }
