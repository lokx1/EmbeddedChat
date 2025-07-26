# Chat Service with Memory Management
import asyncio
import json
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
import openai
import anthropic
import httpx

from ...models.conversation import Conversation
from ...models.message import Message, MessageType
from ...models.ai_provider import AIProvider, AIModel
from ...models.user import User
from ...utils.logger import get_logger

logger = get_logger(__name__)

class ChatMemoryManager:
    """Manages conversation memory and context"""
    
    def __init__(self, max_context_messages: int = 20, max_tokens: int = 4000):
        self.max_context_messages = max_context_messages
        self.max_tokens = max_tokens
    
    async def get_conversation_context(self, db: AsyncSession, conversation_id: int) -> List[Dict[str, str]]:
        """Get conversation context for AI model"""
        try:
            # Get recent messages
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(self.max_context_messages)
            )
            messages = result.scalars().all()
            
            # Convert to AI model format
            context = []
            for message in reversed(messages):  # Reverse to chronological order
                role = "user" if message.message_type == MessageType.USER else "assistant"
                context.append({
                    "role": role,
                    "content": message.content
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    async def summarize_old_messages(self, db: AsyncSession, conversation_id: int, ai_client) -> Optional[str]:
        """Summarize old messages to maintain context within token limits"""
        try:
            # Get older messages that aren't in current context
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .offset(self.max_context_messages)
                .limit(50)  # Summarize up to 50 older messages
            )
            old_messages = result.scalars().all()
            
            if not old_messages:
                return None
            
            # Create summary prompt
            messages_text = "\\n".join([
                f"{msg.message_type.value}: {msg.content}"
                for msg in reversed(old_messages)
            ])
            
            summary_prompt = f"""
            Please summarize the following conversation history in a concise way that preserves the key information, decisions, and context:

            {messages_text}

            Summary:
            """
            
            # Use the AI client to create summary (this would need to be implemented per provider)
            # For now, return a simple summary
            return f"Previous conversation included {len(old_messages)} messages covering various topics."
            
        except Exception as e:
            logger.error(f"Error summarizing old messages: {e}")
            return None

class ChatService:
    """Main chat service with AI provider integration"""
    
    def __init__(self):
        self.memory_manager = ChatMemoryManager()
    
    async def create_conversation(self, db: AsyncSession, user_id: int, title: str, 
                                provider_id: Optional[int] = None) -> Optional[Conversation]:
        """Create a new conversation"""
        try:
            conversation = Conversation(
                title=title,
                user_id=user_id,
                ai_provider_id=provider_id,
                system_prompt="You are a helpful AI assistant.",
                conversation_settings={
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": True
                }
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            await db.rollback()
            return None
    
    async def get_user_conversations(self, db: AsyncSession, user_id: int) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            result = await db.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .where(Conversation.is_active == True)
                .order_by(desc(Conversation.updated_at))
                .options(selectinload(Conversation.messages))
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    async def get_conversation_messages(self, db: AsyncSession, conversation_id: int) -> List[Message]:
        """Get all messages in a conversation"""
        try:
            result = await db.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    async def send_message(self, db: AsyncSession, conversation_id: int, user_id: int, 
                          content: str) -> Optional[Message]:
        """Send a user message and get AI response"""
        try:
            # Get conversation with provider info
            result = await db.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.ai_provider))
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                logger.error(f"Conversation {conversation_id} not found")
                return None
            
            # Save user message
            user_message = Message(
                content=content,
                message_type=MessageType.USER,
                conversation_id=conversation_id,
                user_id=user_id,
                processing_status="completed"
            )
            db.add(user_message)
            await db.commit()
            
            # Generate AI response
            ai_response = await self._generate_ai_response(db, conversation, content)
            
            if ai_response:
                # Save AI message
                ai_message = Message(
                    content=ai_response["content"],
                    message_type=MessageType.ASSISTANT,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    ai_provider_id=conversation.ai_provider_id,
                    model_used=ai_response.get("model_used"),
                    tokens_used=ai_response.get("tokens_used"),
                    response_time=ai_response.get("response_time"),
                    processing_status="completed"
                )
                db.add(ai_message)
                
                # Update conversation
                await db.execute(
                    update(Conversation)
                    .where(Conversation.id == conversation_id)
                    .values(
                        last_message_at=ai_message.created_at,
                        total_tokens_used=Conversation.total_tokens_used + (ai_response.get("tokens_used", 0))
                    )
                )
                
                await db.commit()
                return ai_message
            
            return user_message
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await db.rollback()
            return None
    
    async def stream_message(self, db: AsyncSession, conversation_id: int, user_id: int, 
                           content: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream AI response in real-time"""
        try:
            # Get conversation
            result = await db.execute(
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.ai_provider))
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation or not conversation.ai_provider:
                yield {"error": "Invalid conversation or provider"}
                return
            
            # Save user message
            user_message = Message(
                content=content,
                message_type=MessageType.USER,
                conversation_id=conversation_id,
                user_id=user_id,
                processing_status="completed"
            )
            db.add(user_message)
            await db.commit()
            
            yield {"type": "user_message", "content": content, "message_id": user_message.id}
            
            # Stream AI response
            full_response = ""
            start_time = time.time()
            
            async for chunk in self._stream_ai_response(conversation, content):
                if "content" in chunk:
                    full_response += chunk["content"]
                yield chunk
            
            # Save complete AI response
            response_time = int((time.time() - start_time) * 1000)
            ai_message = Message(
                content=full_response,
                message_type=MessageType.ASSISTANT,
                conversation_id=conversation_id,
                user_id=user_id,
                ai_provider_id=conversation.ai_provider_id,
                response_time=response_time,
                processing_status="completed"
            )
            db.add(ai_message)
            await db.commit()
            
            yield {"type": "complete", "message_id": ai_message.id}
            
        except Exception as e:
            logger.error(f"Error streaming message: {e}")
            yield {"error": str(e)}
    
    async def _generate_ai_response(self, db: AsyncSession, conversation: Conversation, 
                                  user_message: str) -> Optional[Dict[str, Any]]:
        """Generate AI response based on provider"""
        try:
            provider = conversation.ai_provider
            if not provider or not provider.is_available:
                return None
            
            # Get conversation context
            context = await self.memory_manager.get_conversation_context(db, conversation.id)
            
            # Add system prompt
            messages = []
            if conversation.system_prompt:
                messages.append({"role": "system", "content": conversation.system_prompt})
            
            messages.extend(context)
            messages.append({"role": "user", "content": user_message})
            
            start_time = time.time()
            
            if provider.name == "openai":
                response = await self._call_openai(provider, messages, conversation.conversation_settings)
            elif provider.name == "claude":
                response = await self._call_claude(provider, messages, conversation.conversation_settings)
            elif provider.name == "ollama":
                response = await self._call_ollama(provider, messages, conversation.conversation_settings)
            else:
                return None
            
            response_time = int((time.time() - start_time) * 1000)
            response["response_time"] = response_time
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    async def _stream_ai_response(self, conversation: Conversation, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream AI response based on provider"""
        try:
            provider = conversation.ai_provider
            if not provider or not provider.is_available:
                yield {"error": "Provider not available"}
                return
            
            if provider.name == "openai":
                async for chunk in self._stream_openai(provider, user_message):
                    yield chunk
            elif provider.name == "claude":
                async for chunk in self._stream_claude(provider, user_message):
                    yield chunk
            elif provider.name == "ollama":
                async for chunk in self._stream_ollama(provider, user_message):
                    yield chunk
            
        except Exception as e:
            logger.error(f"Error streaming AI response: {e}")
            yield {"error": str(e)}
    
    async def _call_openai(self, provider: AIProvider, messages: List[Dict], settings: Dict) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            client = openai.AsyncOpenAI(api_key=provider.api_key)
            
            response = await client.chat.completions.create(
                model=provider.model_name or "gpt-3.5-turbo",
                messages=messages,
                temperature=settings.get("temperature", 0.7),
                max_tokens=settings.get("max_tokens", 2000)
            )
            
            return {
                "content": response.choices[0].message.content,
                "model_used": response.model,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _call_claude(self, provider: AIProvider, messages: List[Dict], settings: Dict) -> Dict[str, Any]:
        """Call Claude API"""
        try:
            client = anthropic.AsyncAnthropic(api_key=provider.api_key)
            
            # Filter out system messages for Claude
            claude_messages = [m for m in messages if m["role"] != "system"]
            system_prompt = next((m["content"] for m in messages if m["role"] == "system"), None)
            
            response = await client.messages.create(
                model=provider.model_name or "claude-3-sonnet-20240229",
                messages=claude_messages,
                system=system_prompt,
                max_tokens=settings.get("max_tokens", 2000)
            )
            
            return {
                "content": response.content[0].text,
                "model_used": response.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def _call_ollama(self, provider: AIProvider, messages: List[Dict], settings: Dict) -> Dict[str, Any]:
        """Call Ollama API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{provider.base_url}/api/chat",
                    json={
                        "model": provider.model_name or "llama2",
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": settings.get("temperature", 0.7),
                            "num_predict": settings.get("max_tokens", 2000)
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "content": data["message"]["content"],
                        "model_used": data["model"],
                        "tokens_used": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                    }
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def _stream_openai(self, provider: AIProvider, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream OpenAI response"""
        try:
            client = openai.AsyncOpenAI(api_key=provider.api_key)
            
            stream = await client.chat.completions.create(
                model=provider.model_name or "gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "content": chunk.choices[0].delta.content
                    }
                    
        except Exception as e:
            yield {"error": str(e)}
    
    async def _stream_claude(self, provider: AIProvider, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream Claude response"""
        try:
            client = anthropic.AsyncAnthropic(api_key=provider.api_key)
            
            async with client.messages.stream(
                model=provider.model_name or "claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": message}],
                max_tokens=2000
            ) as stream:
                async for text in stream.text_stream:
                    yield {
                        "type": "content", 
                        "content": text
                    }
                    
        except Exception as e:
            yield {"error": str(e)}
    
    async def _stream_ollama(self, provider: AIProvider, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream Ollama response"""
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{provider.base_url}/api/chat",
                    json={
                        "model": provider.model_name or "llama2",
                        "messages": [{"role": "user", "content": message}],
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield {
                                        "type": "content",
                                        "content": data["message"]["content"]
                                    }
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield {"error": str(e)}

# Global instance
chat_service = ChatService()
