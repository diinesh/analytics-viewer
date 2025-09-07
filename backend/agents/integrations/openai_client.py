import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv


class OpenAIClient:
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client with API key from environment"""
        # Load environment variables
        load_dotenv()
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
            print("OpenAI client initialized successfully")
        else:
            print("ERROR: OPENAI_API_KEY not found in environment")
    
    def is_available(self) -> bool:
        """Check if OpenAI client is available"""
        return self.client is not None
    
    async def generate_completion(self, prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0) -> str:
        """
        Generate completion using OpenAI API
        
        Args:
            prompt: The prompt to send to OpenAI
            model: Model to use (default: gpt-3.5-turbo)
            temperature: Randomness of output (default: 0 for deterministic)
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If OpenAI client is not available or API call fails
        """
        if not self.client:
            raise Exception("OpenAI client not initialized - check API key")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {type(e).__name__}: {str(e)}")
            raise

    async def generate_completion_with_system(self, system_message: str, user_message: str, model: str = "gpt-3.5-turbo", temperature: float = 0) -> str:
        """
        Generate completion using OpenAI API with separate system and user messages
        
        Args:
            system_message: The system role/context message
            user_message: The user's actual request/data
            model: Model to use (default: gpt-3.5-turbo)
            temperature: Randomness of output (default: 0 for deterministic)
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If OpenAI client is not available or API call fails
        """
        if not self.client:
            raise Exception("OpenAI client not initialized - check API key")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {type(e).__name__}: {str(e)}")
            raise


# Global instance
openai_client = OpenAIClient()