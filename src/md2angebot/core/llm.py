"""
LLM Service for MD2Angebot.

Provides integration with OpenRouter and OpenAI APIs for generating
and editing quotation content.
"""

import json
import ssl
import urllib.request
import urllib.error
from typing import Optional
from dataclasses import dataclass

# Try to use certifi for SSL certificates (fixes macOS certificate issues)
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    # Fall back to default SSL context if certifi is not installed
    SSL_CONTEXT = ssl.create_default_context()


# Available models for each provider
OPENROUTER_MODELS = {
    'anthropic/claude-sonnet-4': 'Claude Sonnet 4',
    'anthropic/claude-sonnet-4.5': 'Claude Sonnet 4.5',
    'anthropic/claude-3.5-sonnet': 'Claude 3.5 Sonnet',
    'openai/gpt-4o': 'GPT-4o',
    'openai/gpt-4o-mini': 'GPT-4o Mini',
    'google/gemini-2.0-flash-001': 'Gemini 2.0 Flash',
    'meta-llama/llama-3.3-70b-instruct': 'Llama 3.3 70B',
}

OPENAI_MODELS = {
    'gpt-4o': 'GPT-4o',
    'gpt-4o-mini': 'GPT-4o Mini',
    'gpt-4-turbo': 'GPT-4 Turbo',
    'gpt-3.5-turbo': 'GPT-3.5 Turbo',
}

# API endpoints
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are an assistant that generates proposal content in Markdown for MD2Angebot.

Follow these rules:
- Produce only the proposal body; do not add headers, footers, quotation numbers, dates, or client/company contact blocks.
- Do not create sections such as "Client Information", acceptance/signature areas, payment instructions, or validity/expiry dates unless they already exist in the provided context.
- Do not ask for or include client information—the application supplies required metadata.
- Preserve any "+++" markers exactly; they represent page breaks and must never be removed.
- Output must be clean Markdown content only, without assistant chatter, questions, or explanations.
- Use clear, professional language with concise sections and bullet points; include scope, deliverables, and timelines when relevant."""


@dataclass
class LLMConfig:
    """Configuration for LLM service."""
    provider: str = 'openrouter'
    api_key: str = ''
    model: str = 'anthropic/claude-sonnet-4'
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


class LLMService:
    """
    Service for interacting with LLM APIs.
    
    Supports OpenRouter and OpenAI as providers.
    """
    
    def __init__(self, config_loader):
        """
        Initialize the LLM service.
        
        Args:
            config_loader: The application's ConfigLoader instance
        """
        self.config_loader = config_loader
    
    def get_config(self) -> LLMConfig:
        """Get current LLM configuration from the config loader."""
        llm_config = self.config_loader.get('llm', {})
        return LLMConfig(
            provider=llm_config.get('provider', 'openrouter'),
            api_key=llm_config.get('api_key', ''),
            model=llm_config.get('model', 'anthropic/claude-sonnet-4'),
            system_prompt=llm_config.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
        )
    
    def is_configured(self) -> bool:
        """Check if the LLM service is properly configured with an API key."""
        config = self.get_config()
        return bool(config.api_key and config.api_key.strip())
    
    def get_available_models(self, provider: Optional[str] = None) -> dict:
        """
        Get available models for the specified provider.
        
        Args:
            provider: 'openrouter' or 'openai'. If None, uses current config.
            
        Returns:
            Dictionary of model_id -> display_name
        """
        if provider is None:
            provider = self.get_config().provider
        
        if provider == 'openai':
            return OPENAI_MODELS
        return OPENROUTER_MODELS
    
    def generate(self, user_prompt: str, context: str = '') -> str:
        """
        Generate content using the configured LLM.
        
        Args:
            user_prompt: The user's instruction/request
            context: Current editor content to provide as context (can be empty)
            
        Returns:
            Generated text content
            
        Raises:
            LLMError: If the API call fails or returns an error
        """
        config = self.get_config()
        
        if not config.api_key:
            raise LLMError("API key not configured. Please set your API key in Settings → LLM.")
        
        # Build the messages
        messages = [
            {"role": "system", "content": config.system_prompt}
        ]
        
        # Add context if provided
        if context and context.strip():
            messages.append({
                "role": "user",
                "content": f"Here is the current document content for context:\n\n```markdown\n{context}\n```"
            })
            messages.append({
                "role": "assistant", 
                "content": "I understand the current document. What would you like me to help with?"
            })
        
        # Add the user's instruction
        messages.append({
            "role": "user",
            "content": user_prompt
        })
        
        # Make the API request
        return self._make_request(config, messages)
    
    def _make_request(self, config: LLMConfig, messages: list) -> str:
        """
        Make the actual API request.
        
        Args:
            config: LLM configuration
            messages: List of message dicts for the chat completion
            
        Returns:
            The generated text content
            
        Raises:
            LLMError: If the request fails
        """
        # Determine endpoint and headers based on provider
        if config.provider == 'openai':
            url = OPENAI_API_URL
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}'
            }
        else:  # openrouter
            url = OPENROUTER_API_URL
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}',
                'HTTP-Referer': 'https://github.com/md2angebot',
                'X-Title': 'MD2Angebot'
            }
        
        # Build request body
        body = {
            'model': config.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 4096
        }
        
        try:
            data = json.dumps(body).encode('utf-8')
            request = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            # Extract the generated content
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                elif 'text' in choice:
                    return choice['text']
            
            raise LLMError("Unexpected API response format")
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ''
            try:
                error_data = json.loads(error_body)
                error_message = error_data.get('error', {}).get('message', str(e))
            except json.JSONDecodeError:
                error_message = error_body or str(e)
            
            if e.code == 401:
                raise LLMError(f"Authentication failed. Please check your API key.\n{error_message}")
            elif e.code == 429:
                raise LLMError(f"Rate limit exceeded. Please try again later.\n{error_message}")
            elif e.code == 400:
                raise LLMError(f"Invalid request: {error_message}")
            else:
                raise LLMError(f"API error ({e.code}): {error_message}")
                
        except urllib.error.URLError as e:
            raise LLMError(f"Network error: {e.reason}. Please check your internet connection.")
            
        except json.JSONDecodeError as e:
            raise LLMError(f"Failed to parse API response: {e}")
            
        except Exception as e:
            raise LLMError(f"Unexpected error: {e}")
