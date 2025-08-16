"""
Chat Service
Handles conversation and message management
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
    
    def get_conversation_by_id(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[ChatConversation]:
        """Get a specific conversation"""
        return self.db.query(ChatConversation).filter(
            and_(
                ChatConversation.id == conversation_id,
                ChatConversation.user_id == user_id
            )
        ).first()
    
    def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        **updates
    ) -> Optional[ChatConversation]:
        """Update conversation settings"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None
        
        # Handle temperature conversion
        if 'temperature' in updates:
            updates['temperature'] = int(updates['temperature'] * 100)
        
        for key, value in updates.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def delete_conversation(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> bool:
        """Delete a conversation"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        return True
    
    def archive_conversation(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> bool:
        """Archive a conversation"""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False
        
        conversation.is_archived = True
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        
        return True
    
    def add_message(
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
        conversation = self.db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id
        ).first()
        
        if conversation:
            conversation.message_count += 1
            if total_tokens:
                conversation.total_tokens_used += total_tokens
            conversation.updated_at = datetime.utcnow()
            
            # Auto-update title if it's the first user message
            if conversation.message_count == 1 and role == "user" and conversation.title == "New Chat":
                conversation.title = content[:50] + "..." if len(content) > 50 else content
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get messages for a conversation"""
        # Verify user has access to this conversation
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []
        
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.is_deleted == False
            )
        ).order_by(ChatMessage.created_at)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def search_conversations(
        self,
        user_id: int,
        search_term: str,
        limit: int = 20
    ) -> List[ChatConversation]:
        """Search conversations by title or content"""
        # Search by title
        conversations = self.db.query(ChatConversation).filter(
            and_(
                ChatConversation.user_id == user_id,
                ChatConversation.title.ilike(f"%{search_term}%"),
                ChatConversation.is_archived == False
            )
        ).order_by(desc(ChatConversation.updated_at)).limit(limit).all()
        
        return conversations
    
    def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        total_conversations = self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).count()
        
        active_conversations = self.db.query(ChatConversation).filter(
            and_(
                ChatConversation.user_id == user_id,
                ChatConversation.is_archived == False
            )
        ).count()
        
        total_messages = self.db.query(ChatMessage).join(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).count()
        
        total_tokens = self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).with_entities(
            self.db.func.sum(ChatConversation.total_tokens_used)
        ).scalar() or 0
        
        return {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "total_messages": total_messages,
            "total_tokens_used": total_tokens
        }
