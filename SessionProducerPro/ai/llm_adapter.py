# Author: Tresslers Group

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMAdapter:
    """
    Adapter for communicating with an LLM Provider (Default: Ollama).
    """
    
    def __init__(self, model: str = "llama3:latest", 
                 api_base: str = "http://localhost:11434/api/generate"):
        self.model = model
        self.api_base = api_base
        self.system_prompt = (
            "You are a professional music producer assistant. "
            "Output ONLY valid JSON. "
            "Do not write preamble or explanations."
        )

    def generate(self, prompt: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a query to the LLM and expect a JSON response.
        """
        full_prompt = f"{self.system_prompt}\n\nUser: {prompt}\n\nResponse (JSON):"
        
        # If schema is provided, we could append it to prompt to guide structure
        # For now, we rely on the system prompt and specific instructions in 'prompt'
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "format": "json" # Ollama supports json mode
        }
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(self.api_base, data=data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                # Ollama returns 'response' field
                response_text = result.get("response", "{}")
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode LLM response: {response_text}")
                    return {"error": "Invalid JSON from LLM"}
                    
        except urllib.error.URLError as e:
            logger.error(f"LLM Connection Error: {e}")
            return {"error": "Connection Failed", "details": str(e)}
        except Exception as e:
             logger.error(f"LLM Error: {e}")
             return {"error": "Unknown Error"}

if __name__ == "__main__":
    adapter = LLMAdapter()
    # Test
    # print(adapter.query("Generate a drum pattern description"))

