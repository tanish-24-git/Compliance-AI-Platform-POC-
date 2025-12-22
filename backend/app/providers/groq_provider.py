from groq import Groq
from app.providers.llm_provider import LLMProvider
from app.core.config import settings
from typing import Dict, List, Optional
import json
import asyncio


class GroqProvider(LLMProvider):
    """Groq AI provider implementation"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Updated to latest supported model
        
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """Generate text using Groq"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Generate in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            
            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            }
        except Exception as e:
            raise Exception(f"Groq generation failed: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Generate structured JSON output using Groq"""
        try:
            # Add JSON formatting instruction
            json_instruction = "Respond ONLY with valid JSON. No markdown, no explanations."
            if response_schema:
                json_instruction += f"\nExpected schema: {json.dumps(response_schema)}"
            
            # Combine system prompt with JSON instruction
            full_system = f"{system_prompt}\n\n{json_instruction}" if system_prompt else json_instruction
            
            # Generate
            result = await self.generate(prompt, system_prompt=full_system, temperature=0.3, max_tokens=2000)
            
            # Parse JSON from response
            content = result["content"].strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed = json.loads(content)
            return parsed
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON from Groq response: {str(e)}\nContent: {result.get('content', '')}")
        except Exception as e:
            raise Exception(f"Groq structured generation failed: {str(e)}")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Groq doesn't provide embeddings, use Gemini fallback"""
        # For embeddings, we'll use Gemini as Groq doesn't provide this
        from app.providers.gemini_provider import GeminiProvider
        gemini = GeminiProvider()
        return await gemini.create_embedding(text)
