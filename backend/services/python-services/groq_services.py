# backend/services/python-services/services/groq_service.py
import logging
import os
from typing import Any

from groq import Groq

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY environment variable not set!")
            raise ValueError("GROQ_API_KEY is required")

        self.client = Groq(api_key=self.api_key)

        # Available Groq models
        self.available_models = {
            "llama3-8b-8192": "Meta Llama 3 8B",
            "llama3-70b-8192": "Meta Llama 3 70B",
            "mixtral-8x7b-32768": "Mixtral 8x7B",
            "gemma-7b-it": "Google Gemma 7B",
        }

        logger.info(
            f"Groq service initialized with {len(self.available_models)} models"
        )

    async def get_completion(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        system_message: str | None = None,
    ) -> dict[str, Any]:
        """
        Get completion from Groq API
        """
        try:
            # Default model if none specified
            if not model or model not in self.available_models:
                model = "llama3-8b-8192"  # Fast default model

            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})

            messages.append({"role": "user", "content": prompt})

            # Make API call
            logger.info(f"Making Groq API call with model: {model}")

            completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                stream=False,
            )

            # Extract response
            response_text = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens

            logger.info(f"Groq completion successful. Tokens used: {tokens_used}")

            return {
                "completion": response_text,
                "tokens_used": tokens_used,
                "model": model,
                "model_name": self.available_models.get(model, model),
                "finish_reason": completion.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return {"completion": "", "tokens_used": 0, "model": model, "error": str(e)}

    async def get_streaming_completion(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        system_message: str | None = None,
    ):
        """
        Get streaming completion from Groq (for real-time responses)
        """
        try:
            if not model or model not in self.available_models:
                model = "llama3-8b-8192"

            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                messages=messages,
                model=model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Groq streaming error: {str(e)}")
            yield f"Error: {str(e)}"

    def get_available_models(self) -> dict[str, str]:
        """Return available models"""
        return self.available_models

    async def validate_connection(self) -> bool:
        """Test if Groq connection is working"""
        try:
            result = await self.get_completion(
                prompt="Say 'connection test successful'", max_tokens=10
            )
            return "error" not in result
        except Exception as e:
            logger.error(f"Groq connection validation failed: {e}")
            return False
