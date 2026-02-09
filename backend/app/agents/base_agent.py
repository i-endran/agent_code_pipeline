import logging
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from app.config import settings
from app.services.logging_service import get_task_logger

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents in the pipeline."""
    
    def __init__(self, agent_config: Dict[str, Any], task_id: str):
        self.config = agent_config
        self.task_id = task_id
        self.logger = get_task_logger(task_id)
        
        # Initialize Gemini
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in settings")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        self.model_name = self.config.get("model", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.config.get("temperature", 0.3),
                "max_output_tokens": self.config.get("max_tokens", 8000),
            }
        )
        
        # Capture agent state for audit trail
        from app.services.audit_service import audit_service
        self.state_id = audit_service.capture_agent_state(
            agent_name=self.config.get('name', 'unknown'),
            agent_config=self.config,
            task_id=task_id,
            user_prompt=self.config.get('user_prompt')
        )
        self.logger.info(f"Agent state captured: {self.state_id}")

    def _get_system_prompt(self) -> str:
        """Combines enforcement prompt and guardrails into a system prompt."""
        guardrails = "\n".join([f"- {g}" for g in self.config.get("guardrails", [])])
        prompt = f"""
You are the {self.config.get('name', 'AI')} agent.
{self.config.get('enforcement_prompt', '')}

GUARDRAILS:
{guardrails}

Always respond in valid JSON format where appropriate, or clear structured markdown as requested.
"""
        return prompt

    async def call_llm(self, user_prompt: str, context: Optional[Dict] = None) -> str:
        """Wrapper for calling Gemini with tool support and retry logic."""
        self.logger.info(f"Calling LLM ({self.model_name}) for task {self.task_id}")
        
        # 1. Fetch Tools for this agent
        tools_list = []
        try:
            from app.db.database import SessionLocal
            from app.models.models import Tool
            db = SessionLocal()
            try:
                # Get tools assigned to this agent in config
                agent_tools = self.config.get("tools", [])
                db_tools = db.query(Tool).filter(Tool.name.in_(agent_tools)).all()
                
                # Convert to Gemini tool format (simplified)
                # In a real app, you'd handle complex nested parameters
                for t in db_tools:
                    tools_list.append({
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": t.parameters or {"type": "object", "properties": {}}
                    })
            finally:
                db.close()
        except Exception as e:
            self.logger.warning(f"Could not load tools: {e}")

        full_context = f"CONTEXT:\n{json.dumps(context, indent=2)}\n\n" if context else ""
        system_prompt = self._get_system_prompt()
        
        try:
            # Re-initialize model with tools if any
            if tools_list:
                # In Gemini Pro/Flash, tools are passed to the model
                # Note: This is an simplified implementation of tool loop
                model_with_tools = genai.GenerativeModel(
                    model_name=self.model_name,
                    tools=[{"function_declarations": tools_list}],
                    generation_config=self.model._generation_config
                )
                chat = model_with_tools.start_chat(history=[])
            else:
                chat = self.model.start_chat(history=[])
                
            response = await chat.send_message_async(
                f"{system_prompt}\n\n{full_context}\nUSER REQUEST: {user_prompt}"
            )
            
            # Simple Tool Loop (1 level deep for now)
            while response.candidates[0].content.parts[0].function_call:
                fc = response.candidates[0].content.parts[0].function_call
                tool_name = fc.name
                args = {k: v for k, v in fc.args.items()}
                
                self.logger.info(f"Agent {self.config.get('name')} calling tool: {tool_name}")
                
                # Execute Tool via MCPService
                from app.services.mcp_service import mcp_service
                db = SessionLocal()
                try:
                    result = await mcp_service.execute_tool(tool_name, args, db)
                    response = await chat.send_message_async(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={'result': result}
                                )
                            )]
                        )
                    )
                finally:
                    db.close()
            
            return response.text
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic for the agent."""
        pass

    def validate_output(self, output: str) -> bool:
        """Validates agent output against policies."""
        # TODO: Implement basic validation (e.g. check for PII, required sections)
        return True
