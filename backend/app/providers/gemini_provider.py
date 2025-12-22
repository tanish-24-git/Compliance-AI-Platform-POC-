import google.generativeai as genai
from app.providers.llm_provider import LLMProvider
from app.core.config import settings
from typing import Dict, List, Optional
import json
import asyncio


class GeminiProvider(LLMProvider):
    """Gemini AI provider implementation"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """Generate text using Gemini"""
        try:
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Generate in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            )
            
            return {
                "content": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                }
            }
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Generate structured JSON output using Gemini"""
        try:
            # Add JSON formatting instruction
            json_instruction = "\n\nRespond ONLY with valid JSON matching this structure. No markdown, no explanations."
            if response_schema:
                json_instruction += f"\nExpected schema: {json.dumps(response_schema)}"
            
            full_prompt = f"{system_prompt}{json_instruction}\n\n{prompt}" if system_prompt else f"{json_instruction}\n\n{prompt}"
            
            # Generate
            result = await self.generate(full_prompt, temperature=0.3, max_tokens=2000)
            
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
            raise Exception(f"Failed to parse JSON from Gemini response: {str(e)}\nContent: {result.get('content', '')}")
        except Exception as e:
            raise Exception(f"Gemini structured generation failed: {str(e)}")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using Gemini embedding model"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Gemini embedding failed: {str(e)}")
