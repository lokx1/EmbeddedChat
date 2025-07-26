import anthropic
import asyncio
import json
from typing import Dict, Any, List, AsyncGenerator, Optional
from .base_provider import BaseAIProvider

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url', 'https://api.anthropic.com')
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize Anthropic client"""
        try:
            if not self.api_key:
                print("Anthropic API key not provided")
                return False
                
            self.client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # Test connection with a simple completion
            test_response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            self.is_available = bool(test_response.content)
            return self.is_available
            
        except Exception as e:
            print(f"Anthropic initialization failed: {e}")
            self.is_available = False
            return False
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available Anthropic models"""
        # Anthropic doesn't have a models endpoint, so we return known models
        models = [
            {
                'id': 'claude-3-opus-20240229',
                'name': 'Claude 3 Opus',
                'provider': 'anthropic',
                'context_length': 200000,
                'description': 'Most capable model for complex tasks'
            },
            {
                'id': 'claude-3-sonnet-20240229', 
                'name': 'Claude 3 Sonnet',
                'provider': 'anthropic',
                'context_length': 200000,
                'description': 'Balanced performance and speed'
            },
            {
                'id': 'claude-3-haiku-20240307',
                'name': 'Claude 3 Haiku', 
                'provider': 'anthropic',
                'context_length': 200000,
                'description': 'Fastest model for simple tasks'
            },
            {
                'id': 'claude-3-5-sonnet-20241022',
                'name': 'Claude 3.5 Sonnet',
                'provider': 'anthropic', 
                'context_length': 200000,
                'description': 'Latest and most advanced model'
            }
        ]
        
        return models if self.is_available else []
    
    async def validate_model(self, model: str) -> bool:
        """Validate if model exists"""
        models = await self.get_available_models()
        return any(m['id'] == model for m in models)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate response using Anthropic Claude"""
        
        if not self.client or not self.is_available:
            yield "Error: Anthropic service not available"
            return
            
        # Format messages for Anthropic format
        formatted_messages = self._format_messages_for_anthropic(messages)
        
        try:
            if stream:
                async with self.client.messages.stream(
                    model=model,
                    messages=formatted_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
                        
            else:
                response = await self.client.messages.create(
                    model=model,
                    messages=formatted_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                for content in response.content:
                    if content.type == "text":
                        yield content.text
                        
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    def _format_messages_for_anthropic(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for Anthropic's expected format"""
        formatted = []
        system_message = ""
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                system_message += content + "\n"
            else:
                # Anthropic expects alternating user/assistant messages
                formatted.append({
                    "role": "user" if role == "user" else "assistant",
                    "content": content
                })
        
        # If we have a system message, prepend it to first user message
        if system_message and formatted and formatted[0]["role"] == "user":
            formatted[0]["content"] = f"{system_message.strip()}\n\n{formatted[0]['content']}"
        
        return formatted
    
    async def get_thinking_steps(self, prompt: str, context: str = "") -> List[str]:
        """Generate Claude-style thinking steps"""
        base_steps = await super().get_thinking_steps(prompt, context)
        
        claude_steps = [
            "Initializing Claude reasoning process...",
            "Analyzing request with constitutional AI principles...",
            "Accessing relevant knowledge and context...",
            "Applying multi-step reasoning and verification...",
            "Generating thoughtful, nuanced response...",
            "Reviewing for accuracy and helpfulness..."
        ]
        
        return claude_steps
    
    async def extract_memory(self, content: str, context: str) -> Dict[str, Any]:
        """Enhanced memory extraction using Claude's reasoning"""
        base_memory = await super().extract_memory(content, context)
        
        # Use Claude to extract insights if available
        if self.client and len(content) > 50:
            try:
                response = await self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=300,
                    messages=[{
                        "role": "user",
                        "content": f"""Analyze this conversation and extract key insights that should be remembered:

Context: {context}
Content: {content}

Please provide:
1. Main topic/theme
2. Key facts or decisions
3. User preferences revealed
4. Important context for future conversations

Format as JSON with keys: topic, facts, preferences, context"""
                    }]
                )
                
                if response.content:
                    try:
                        insights = json.loads(response.content[0].text)
                        base_memory.update({
                            "insights": insights,
                            "relevance_score": 0.95,
                            "extraction_method": "claude_analysis"
                        })
                    except:
                        pass
                        
            except Exception as e:
                print(f"Claude memory extraction error: {e}")
        
        return base_memory
    
    async def generate_thinking_display(self, prompt: str, context: str = "") -> str:
        """Generate Claude-style thinking display"""
        if not self.client:
            return "Claude thinking process not available..."
            
        try:
            thinking_prompt = f"""<thinking>
The user asked: {prompt}

Given context: {context}

Let me think through this step by step:
1. Understanding the request
2. Considering relevant information
3. Planning my response approach
4. Ensuring I provide helpful, accurate information
</thinking>"""
            
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"Show your thinking process for: {prompt}\nContext: {context}"
                }]
            )
            
            if response.content:
                return response.content[0].text
                
        except Exception as e:
            print(f"Thinking generation error: {e}")
            
        return "Analyzing request and formulating comprehensive response..."
