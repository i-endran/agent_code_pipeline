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
        """Wrapper for calling Gemini with retry logic and error handling."""
        self.logger.info(f"Calling LLM ({self.model_name}) for task {self.task_id}")
        
        full_context = f"CONTEXT:\n{json.dumps(context, indent=2)}\n\n" if context else ""
        system_prompt = self._get_system_prompt()
        
        try:
            # Use a chat session for system instruction simulation
            chat = self.model.start_chat(history=[])
            response = await chat.send_message_async(
                f"{system_prompt}\n\n{full_context}\nUSER REQUEST: {user_prompt}"
            )
            
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
