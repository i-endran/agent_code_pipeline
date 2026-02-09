"""
Agent Configuration Service

Loads and provides access to agent configurations from agents.yaml.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from functools import lru_cache


def get_config_path() -> Path:
    """Get the path to agents.yaml configuration file."""
    # Look for config relative to backend directory
    backend_dir = Path(__file__).parent.parent.parent
    config_path = backend_dir / "config" / "agents.yaml"
    return config_path


@lru_cache()
def load_agent_configs() -> Dict[str, Any]:
    """
    Load agent configurations from YAML file.
    
    Cached for performance.
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(f"Agent config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config


def get_agent_configs() -> Dict[str, Any]:
    """Get all agent configurations."""
    config = load_agent_configs()
    return config.get("agents", {})


def get_agent_config(agent_id: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific agent."""
    agents = get_agent_configs()
    return agents.get(agent_id)


def get_token_estimates() -> Dict[str, int]:
    """Get token estimation values for each agent."""
    config = load_agent_configs()
    return config.get("token_estimates", {})


def get_model_pricing() -> Dict[str, Dict[str, float]]:
    """Get model pricing information."""
    config = load_agent_configs()
    return config.get("model_pricing", {})


def calculate_token_estimate(enabled_agents: List[str]) -> Dict[str, Any]:
    """
    Calculate total token and cost estimates for enabled agents.
    
    Args:
        enabled_agents: List of agent IDs to include
        
    Returns:
        Dict with agent estimates, total tokens, and total cost
    """
    agents = get_agent_configs()
    token_estimates = get_token_estimates()
    model_pricing = get_model_pricing()
    
    result = {
        "agents": {},
        "total_tokens": 0,
        "total_cost": 0.0
    }
    
    for agent_id in enabled_agents:
        if agent_id not in agents:
            continue
        
        agent_config = agents[agent_id]
        estimated_tokens = token_estimates.get(agent_id, 2000)
        
        # Get model pricing
        model = agent_config.get("model", "gpt-4o")
        pricing = model_pricing.get(model, {"input": 0.01, "output": 0.03})
        
        # Estimate cost (assume 50% input, 50% output tokens)
        input_tokens = estimated_tokens // 2
        output_tokens = estimated_tokens // 2
        
        estimated_cost = (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
        
        result["agents"][agent_id] = {
            "name": agent_config["name"],
            "model": model,
            "tokens": estimated_tokens,
            "cost": round(estimated_cost, 4)
        }
        
        result["total_tokens"] += estimated_tokens
        result["total_cost"] += estimated_cost
    
    result["total_cost"] = round(result["total_cost"], 4)
    
    return result


def reload_configs():
    """Clear config cache and reload from file."""
    load_agent_configs.cache_clear()
