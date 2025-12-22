import sys
import os
sys.path.append(os.getcwd())

from app.providers.groq_provider import GroqProvider
import asyncio

async def test():
    print("Initializing GroqProvider...")
    try:
        p = GroqProvider()
        print("Provider initialized.")
        print("Model:", p.model)
        
        print("Generating content...")
        res = await p.generate("Hello, are you working?")
        print("Generation result:", res)
    except Exception as e:
        print("ERROR CAUGHT:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
