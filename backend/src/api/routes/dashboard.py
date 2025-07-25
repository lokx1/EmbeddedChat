# Dashboard API routes for statistics and activity
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.models.database import get_db
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.document import Document
from src.api.middleware.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class DashboardStats(BaseModel):
    active_chats: int
    total_documents: int
    total_workflows: int
    team_members: int
    chat_growth: str
    document_growth: str
    workflow_growth: str
    member_growth: str

class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    status: str
    user_id: int = None
    user_name: str = None

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics"""
    try:
        # Get current stats
        active_chats_result = await db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == current_user.id
            )
        )
        active_chats = active_chats_result.scalar() or 0

        documents_result = await db.execute(
            select(func.count(Document.id)).where(
                Document.user_id == current_user.id
            )
        )
        total_documents = documents_result.scalar() or 0

        # For now, workflows and team members are placeholder
        total_workflows = 0  # Will implement when workflow feature is added
        team_members = 1     # Current user

        # Calculate growth (compare with last week)
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Chat growth
        old_chats_result = await db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == current_user.id,
                Conversation.created_at < week_ago
            )
        )
        old_chats = old_chats_result.scalar() or 0
        
        if old_chats > 0:
            chat_growth_pct = ((active_chats - old_chats) / old_chats) * 100
            chat_growth = f"+{chat_growth_pct:.0f}%" if chat_growth_pct > 0 else f"{chat_growth_pct:.0f}%"
        else:
            chat_growth = f"+{active_chats}" if active_chats > 0 else "No data"

        # Document growth
        old_docs_result = await db.execute(
            select(func.count(Document.id)).where(
                Document.user_id == current_user.id,
                Document.created_at < week_ago
            )
        )
        old_docs = old_docs_result.scalar() or 0
        
        if old_docs > 0:
            doc_growth_pct = ((total_documents - old_docs) / old_docs) * 100
            document_growth = f"+{doc_growth_pct:.0f}%" if doc_growth_pct > 0 else f"{doc_growth_pct:.0f}%"
        else:
            document_growth = f"+{total_documents}" if total_documents > 0 else "No data"

        return DashboardStats(
            active_chats=active_chats,
            total_documents=total_documents,
            total_workflows=total_workflows,
            team_members=team_members,
            chat_growth=chat_growth,
            document_growth=document_growth,
            workflow_growth="No data",
            member_growth="No change"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")

@router.get("/activity", response_model=List[ActivityItem])
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    """Get recent activity for the dashboard"""
    try:
        activities = []

        # Get recent conversations
        conversations_result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(desc(Conversation.created_at))
            .limit(5)
        )
        conversations = conversations_result.scalars().all()

        for conv in conversations:
            activities.append(ActivityItem(
                id=f"conv_{conv.id}",
                type="chat",
                title="New chat session started",
                description=f"Conversation: {conv.title or 'Untitled'}",
                timestamp=conv.created_at.isoformat(),
                status="success",
                user_id=current_user.id,
                user_name=current_user.username
            ))

        # Get recent documents
        documents_result = await db.execute(
            select(Document)
            .where(Document.user_id == current_user.id)
            .order_by(desc(Document.created_at))
            .limit(5)
        )
        documents = documents_result.scalars().all()

        for doc in documents:
            activities.append(ActivityItem(
                id=f"doc_{doc.id}",
                type="document",
                title="Document uploaded",
                description=f"{doc.filename} processed successfully",
                timestamp=doc.created_at.isoformat(),
                status="success",
                user_id=current_user.id,
                user_name=current_user.username
            ))

        # Sort by timestamp (most recent first)
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        
        return activities[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity: {str(e)}")

@router.get("/user-info")
async def get_dashboard_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get additional user info for dashboard"""
    try:
        # Get user's message count
        messages_result = await db.execute(
            select(func.count(Message.id))
            .join(Conversation)
            .where(Conversation.user_id == current_user.id)
        )
        total_messages = messages_result.scalar() or 0

        # Get user's last activity
        last_activity_result = await db.execute(
            select(Message.created_at)
            .join(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_activity = last_activity_result.scalar()

        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "total_messages": total_messages,
            "last_activity": last_activity.isoformat() if last_activity else None,
            "member_since": current_user.created_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user info: {str(e)}")
