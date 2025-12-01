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

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


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

OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

DEFAULT_SYSTEM_PROMPT = """You are an assistant that generates proposal content in Markdown for MD2Angebot.

Follow these rules:
- Produce only the proposal body; do not add headers, footers, quotation numbers, dates, or client/company contact blocks.
- Do not create sections such as "Client Information", acceptance/signature areas, payment instructions, or validity/expiry dates unless they already exist in the provided context.
- Do not ask for or include client information—the application supplies required metadata.
- Preserve any "+++" markers exactly; they represent page breaks and must never be removed.
- Output must be clean Markdown content only, without assistant chatter, questions, or explanations.
- Do NOT enclose the output in markdown code blocks (e.g., ```markdown ... ```). Return raw markdown text directly.
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
        messages = self._prepare_messages(user_prompt, context)
        config = self.get_config()
        
        if not config.api_key:
            raise LLMError("API key not configured. Please set your API key in Settings → LLM.")
            
        return self._make_request(config, messages, stream=False)

    def generate_stream(self, user_prompt: str, context: str = ''):
        """
        Generate content using the configured LLM with streaming.
        
        Args:
            user_prompt: The user's instruction/request
            context: Current editor content
            
        Yields:
            Chunks of generated text
        """
        messages = self._prepare_messages(user_prompt, context)
        config = self.get_config()
        
        if not config.api_key:
            raise LLMError("API key not configured. Please set your API key in Settings → LLM.")
            
        yield from self._make_request(config, messages, stream=True)

    def _prepare_messages(self, user_prompt: str, context: str) -> list:
        """Helper to prepare message list."""
        config = self.get_config()
        messages = [
            {"role": "system", "content": config.system_prompt}
        ]
        
        if context and context.strip():
            messages.append({
                "role": "user",
                "content": f"Here is the current document content for context:\n\n```markdown\n{context}\n```"
            })
            messages.append({
                "role": "assistant", 
                "content": "I understand the current document. What would you like me to help with?"
            })
        
        messages.append({
            "role": "user",
            "content": user_prompt
        })
        return messages
    
    def _make_request(self, config: LLMConfig, messages: list, stream: bool = False):
        """
        Make the actual API request.
        
        Args:
            config: LLM configuration
            messages: List of message dicts for the chat completion
            stream: Whether to stream the response
            
        Returns:
            The generated text content (if stream=False)
            OR a generator yielding text chunks (if stream=True)
            
        Raises:
            LLMError: If the request fails
        """
        if config.provider == 'openai':
            url = OPENAI_API_URL
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}'
            }
        else:
            url = OPENROUTER_API_URL
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {config.api_key}',
                'HTTP-Referer': 'https://github.com/md2angebot',
                'X-Title': 'MD2Angebot'
            }
        
        body = {
            'model': config.model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 4096,
            'stream': stream
        }
        
        try:
            data = json.dumps(body).encode('utf-8')
            request = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            if stream:
                return self._handle_streaming_response(request)
            
            with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
                result = json.loads(response.read().decode('utf-8'))
                
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
            if isinstance(e, LLMError):
                raise e
            raise LLMError(f"Unexpected error: {e}")

    def _handle_streaming_response(self, request):
        """Helper to yield chunks from a streaming response."""
        try:
            with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
                for line in response:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue
                        
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            if isinstance(e, urllib.error.HTTPError):
                error_body = e.read().decode('utf-8') if e.fp else ''
                raise LLMError(f"Streaming API error ({e.code}): {error_body or str(e)}")
            raise LLMError(f"Streaming error: {e}")

