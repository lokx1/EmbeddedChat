"""
Chat Service (Async Version)
Handles conversation and message management with AsyncSession
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, func
from datetime import datetime

from ..models.chat_conversation import ChatConversation, ChatMessage
from ..models.user import User

class ChatService:
    """Service for managing chat conversations and messages"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(
        self, 
        user_id: int,
        title: str = "New Chat",
        ai_provider: str = "openai",
        ai_model: str = "gpt-4o",
        system_prompt: str = "You are a helpful AI assistant.",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> ChatConversation:
        """Create a new conversation"""
        conversation = ChatConversation(
            title=title,
            user_id=user_id,
            ai_provider=ai_provider,
            ai_model=ai_model,
            system_prompt=system_prompt,
            temperature=int(temperature * 100),  # Store as integer
            max_tokens=max_tokens
        )
        
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation
    
    async def get_user_conversations(
        self, 
        user_id: int, 
        limit: int = 50,
        include_archived: bool = False
    ) -> List[ChatConversation]:
        """Get conversations for a user"""
        query = select(ChatConversation).filter(
            ChatConversation.user_id == user_id
        )
        
        if not include_archived:
            query = query.filter(ChatConversation.is_archived == False)
        
        query = query.order_by(desc(ChatConversation.updated_at)).limit(limit)
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        return conversations
    
    async def get_conversation_by_id(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[ChatConversation]:
        """Get a specific conversation"""
        query = select(ChatConversation).filter(
            and_(
                ChatConversation.id == conversation_id,
                ChatConversation.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        **updates
    ) -> Optional[ChatConversation]:
        """Update conversation settings"""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        # Handle temperature conversion
        if 'temperature' in updates:
            updates['temperature'] = int(updates['temperature'] * 100)
        
        for key, value in updates.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        
        conversation.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(conversation)
        
        return conversation
    
    async def delete_conversation(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> bool:
        """Delete a conversation"""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        await self.db.delete(conversation)
        await self.db.commit()
        
        return True
    
    async def archive_conversation(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> bool:
        """Archive a conversation"""
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.is_archived = True
        conversation.updated_at = datetime.utcnow()
        await self.db.commit()
        
        return True
    
    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        attachments: Optional[List[Dict]] = None
    ) -> ChatMessage:
        """Add a message to a conversation"""
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            ai_provider=ai_provider,
            ai_model=ai_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_time_ms=response_time_ms,
            attachments=attachments
        )
        
        self.db.add(message)
        
        # Update conversation stats
        conv_query = select(ChatConversation).filter(
            ChatConversation.id == conversation_id
        )
        conv_result = await self.db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if conversation:
            conversation.message_count += 1
            if total_tokens:
                conversation.total_tokens_used += total_tokens
            conversation.updated_at = datetime.utcnow()
            
            # Auto-update title if it's the first user message
            if conversation.message_count == 1 and role == "user" and conversation.title == "New Chat":
                conversation.title = content[:50] + "..." if len(content) > 50 else content
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get messages for a conversation"""
        # Verify user has access to this conversation
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []
        
        query = select(ChatMessage).filter(
            and_(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(ChatMessage.created_at)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_conversations(
        self,
        user_id: int,
        search_term: str,
        limit: int = 20
    ) -> List[ChatConversation]:
        """Search conversations by title or content"""
        # Search by title
        query = select(ChatConversation).filter(
            and_(
                ChatConversation.user_id == user_id,
                ChatConversation.title.ilike(f"%{search_term}%"),
                ChatConversation.is_archived == False
            )
        ).order_by(desc(ChatConversation.updated_at)).limit(limit)
        
        result = await self.db.execute(query)
        conversations = result.scalars().all()
        
        return conversations
    
    async def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        # Total conversations
        total_query = select(func.count()).select_from(ChatConversation).filter(
            ChatConversation.user_id == user_id
        )
        total_result = await self.db.execute(total_query)
        total_conversations = total_result.scalar()
        
        # Active conversations
        active_query = select(func.count()).select_from(ChatConversation).filter(
            and_(
                ChatConversation.user_id == user_id,
                ChatConversation.is_archived == False
            )
        )
        active_result = await self.db.execute(active_query)
        active_conversations = active_result.scalar()
        
        # Total messages
        messages_query = select(func.count()).select_from(ChatMessage).join(ChatConversation).filter(
            ChatConversation.user_id == user_id
        )
        messages_result = await self.db.execute(messages_query)
        total_messages = messages_result.scalar()
        
        # Total tokens
        tokens_query = select(func.sum(ChatConversation.total_tokens_used)).filter(
            ChatConversation.user_id == user_id
        )
        tokens_result = await self.db.execute(tokens_query)
        total_tokens = tokens_result.scalar() or 0
        
        return {
            "total_conversations": total_conversations or 0,
            "active_conversations": active_conversations or 0,
            "total_messages": total_messages or 0,
            "total_tokens_used": total_tokens
        }
