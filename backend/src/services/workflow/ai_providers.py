"""
AI Provider Services for Workflow
"""
import asyncio
import base64
import io
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

import openai
import anthropic
import ollama
from PIL import Image
import requests
# Note: moviepy import is commented out as it's not currently used in the implementation
# from moviepy.editor import AudioFileClip


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def generate_content(
        self, 
        prompt: str, 
        output_format: str,
        model_name: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content based on prompt and output format"""
        pass
    
    @abstractmethod
    def process_with_assets(
        self,
        description: str,
        asset_urls: List[str],
        output_format: str,
        model_name: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Process content with input assets"""
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider for content generation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_content(
        self, 
        prompt: str, 
        output_format: str,
        model_name: str = "gpt-4o",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content using OpenAI"""
        try:
            if output_format.upper() in ["PNG", "JPG", "JPEG"]:
                return await self._generate_image(prompt, output_format, **kwargs)
            elif output_format.upper() == "MP3":
                return await self._generate_audio(prompt, **kwargs)
            else:
                return await self._generate_text(prompt, model_name, **kwargs)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def _generate_image(self, prompt: str, output_format: str, **kwargs) -> Dict[str, Any]:
        """Generate image using DALL-E"""
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json"
        )
        
        image_data = base64.b64decode(response.data[0].b64_json)
        
        return {
            "success": True,
            "content": image_data,
            "content_type": f"image/{output_format.lower()}",
            "metadata": {
                "model": "dall-e-3",
                "prompt": prompt,
                "revised_prompt": response.data[0].revised_prompt
            }
        }
    
    async def _generate_audio(self, text: str, **kwargs) -> Dict[str, Any]:
        """Generate audio using OpenAI TTS"""
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="mp3"
        )
        
        audio_data = b""
        async for chunk in response.iter_bytes():
            audio_data += chunk
        
        return {
            "success": True,
            "content": audio_data,
            "content_type": "audio/mp3",
            "metadata": {
                "model": "tts-1",
                "voice": "alloy",
                "input_text": text
            }
        }
    
    async def _generate_text(self, prompt: str, model_name: str, **kwargs) -> Dict[str, Any]:
        """Generate text using GPT models"""
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "content_type": "text/plain",
            "metadata": {
                "model": model_name,
                "usage": response.usage.model_dump() if response.usage else None
            }
        }
    
    async def process_with_assets(
        self,
        description: str,
        asset_urls: List[str],
        output_format: str,
        model_name: str = "gpt-4o",
        **kwargs
    ) -> Dict[str, Any]:
        """Process content with input assets using GPT-4 Vision"""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": description}
                    ]
                }
            ]
            
            # Add images to the message
            for url in asset_urls:
                if self._is_image_url(url):
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": url}
                    })
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                **kwargs
            )
            
            generated_content = response.choices[0].message.content
            
            # If output format is image/audio, use the generated content as prompt
            if output_format.upper() in ["PNG", "JPG", "JPEG", "MP3"]:
                return await self.generate_content(generated_content, output_format, **kwargs)
            
            return {
                "success": True,
                "content": generated_content,
                "content_type": "text/plain",
                "metadata": {
                    "model": "gpt-4o",
                    "input_assets": asset_urls,
                    "usage": response.usage.model_dump() if response.usage else None
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def _is_image_url(self, url: str) -> bool:
        """Check if URL is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)


class ClaudeProvider(BaseAIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_content(
        self, 
        prompt: str, 
        output_format: str,
        model_name: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content using Claude"""
        try:
            # Claude doesn't generate images/audio directly, so we generate text descriptions
            if output_format.upper() in ["PNG", "JPG", "JPEG"]:
                enhanced_prompt = f"Create a detailed image description for: {prompt}. Be very specific about visual elements, style, composition, and details."
            elif output_format.upper() == "MP3":
                enhanced_prompt = f"Create a detailed script or text content for audio generation based on: {prompt}"
            else:
                enhanced_prompt = prompt
            
            response = await self.client.messages.create(
                model=model_name,
                max_tokens=4000,
                messages=[{"role": "user", "content": enhanced_prompt}],
                **kwargs
            )
            
            content = response.content[0].text
            
            return {
                "success": True,
                "content": content,
                "content_type": "text/plain",
                "metadata": {
                    "model": model_name,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def process_with_assets(
        self,
        description: str,
        asset_urls: List[str],
        output_format: str,
        model_name: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> Dict[str, Any]:
        """Process content with input assets using Claude Vision"""
        try:
            content_parts = [{"type": "text", "text": description}]
            
            # Add images to the message
            for url in asset_urls:
                if self._is_image_url(url):
                    # Download and encode image
                    image_data = await self._download_and_encode_image(url)
                    if image_data:
                        content_parts.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        })
            
            response = await self.client.messages.create(
                model=model_name,
                max_tokens=4000,
                messages=[{"role": "user", "content": content_parts}],
                **kwargs
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "content_type": "text/plain",
                "metadata": {
                    "model": model_name,
                    "input_assets": asset_urls,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    async def _download_and_encode_image(self, url: str) -> Optional[str]:
        """Download image and encode to base64"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
        except Exception:
            return None
    
    def _is_image_url(self, url: str) -> bool:
        """Check if URL is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)


class OllamaProvider(BaseAIProvider):
    """Ollama provider for local AI models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        super().__init__(base_url=base_url)
        self.client = ollama.AsyncClient(host=base_url)
    
    def generate_content(
        self, 
        prompt: str, 
        output_format: str,
        model_name: str = "llama3.2",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate content using Ollama"""
        try:
            if output_format.upper() in ["PNG", "JPG", "JPEG"]:
                enhanced_prompt = f"Create a detailed image description for: {prompt}. Be very specific about visual elements, style, composition, and details."
            elif output_format.upper() == "MP3":
                enhanced_prompt = f"Create a detailed script or text content for audio generation based on: {prompt}"
            else:
                enhanced_prompt = prompt
            
            # Use sync ollama client for simplicity
            import ollama
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": enhanced_prompt}]
            )
            
            return {
                "success": True,
                "content": response['message']['content'],
                "content_type": "text/plain",
                "metadata": {
                    "model": model_name,
                    "eval_count": response.get('eval_count'),
                    "eval_duration": response.get('eval_duration')
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def process_with_assets(
        self,
        description: str,
        asset_urls: List[str],
        output_format: str,
        model_name: str = "llama3.2-vision",  # Use vision model if available
        **kwargs
    ) -> Dict[str, Any]:
        """Process content with input assets using Ollama vision models"""
        try:
            # For Ollama, we'll use the description and asset information
            asset_context = f"\nInput assets: {', '.join(asset_urls)}" if asset_urls else ""
            full_prompt = f"{description}{asset_context}"
            
            # Use sync ollama client for simplicity
            import ollama
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return {
                "success": True,
                "content": response['message']['content'],
                "content_type": "text/plain",
                "metadata": {
                    "model": model_name,
                    "input_assets": asset_urls,
                    "eval_count": response.get('eval_count'),
                    "eval_duration": response.get('eval_duration')
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }


class AIProviderFactory:
    """Factory for creating AI providers"""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> BaseAIProvider:
        """Create an AI provider instance"""
        if provider_type.lower() == "openai":
            return OpenAIProvider(kwargs.get("api_key"))
        elif provider_type.lower() == "claude":
            return ClaudeProvider(kwargs.get("api_key"))
        elif provider_type.lower() == "ollama":
            return OllamaProvider(kwargs.get("base_url", "http://localhost:11434"))
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
