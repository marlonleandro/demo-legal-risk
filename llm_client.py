"""
Cliente para interactuar con APIs de LLM (Anthropic y OpenAI)
"""

import os
from typing import Optional, Dict
import anthropic
import openai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """Cliente unificado para múltiples proveedores de LLM"""
    
    def __init__(self, provider: str = "anthropic", model: str = None):
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "anthropic":
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
            self.model = model or "claude-sonnet-4-6"
        elif self.provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None
            self.model = model or "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    def is_configured(self) -> bool:
        """Verifica si el cliente está configurado correctamente"""
        return self.api_key is not None and self.client is not None
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, any]:
        """
        Genera una respuesta usando el LLM configurado
        """
        if not self.is_configured():
            raise Exception(f"API key no configurada para {self.provider}")
        
        try:
            if self.provider == "anthropic":
                return self._generate_anthropic(
                    system_prompt, user_prompt, temperature, max_tokens
                )
            elif self.provider == "openai":
                return self._generate_openai(
                    system_prompt, user_prompt, temperature, max_tokens
                )
        except Exception as e:
            raise Exception(f"Error al generar respuesta: {str(e)}")
    
    def _generate_anthropic(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, any]:
        """Genera respuesta usando Anthropic Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "content": response.content[0].text,
            "model": self.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    def _generate_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, any]:
        """Genera respuesta usando OpenAI GPT"""
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": self.model,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }
    
    def count_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto
        """
        # Estimación simple: ~4 caracteres por token
        return len(text) // 4
    
    @staticmethod
    def get_available_models(provider: str) -> list:
        """Retorna lista de modelos disponibles por proveedor"""
        models = {
            "anthropic": [
                "claude-sonnet-4-6",
                "claude-opus-4-20250514",
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
        }
        return models.get(provider.lower(), [])
