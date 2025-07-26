from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, and_
import json
import asyncio
import psutil
import time

from ...models.database import get_db
from ...models.conversation import Conversation
from ...models.message import Message
from ...models.document import Document
from ...models.user import User
from ...services.ai.service_manager import ai_service_manager
from ...services.dashboard.stats_service import DashboardStatsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

class DashboardStats(BaseModel):
    total_conversations: int
    total_messages: int
    total_documents: int
    total_users: int
    active_conversations_today: int
    messages_today: int
    avg_messages_per_conversation: float
    most_active_day: str
    ai_providers_status: Dict[str, Any]

class ConversationStats(BaseModel):
    id: str
    title: str
    message_count: int
    last_activity: datetime
    duration_minutes: Optional[float]
    ai_provider_used: Optional[str]
    has_documents: bool

class ActivityData(BaseModel):
    date: str
    conversations: int
    messages: int
    documents_uploaded: int

class AIProviderStats(BaseModel):
    provider: str
    status: str
    total_requests: int
    avg_response_time: float
    success_rate: float
    models_available: int
    last_used: Optional[datetime]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    try:
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Basic counts
        total_conversations = db.query(Conversation).count()
        total_messages = db.query(Message).count()
        total_documents = db.query(Document).count()
        total_users = db.query(User).count()
        
        # Today's activity
        active_conversations_today = db.query(Conversation).filter(
            Conversation.updated_at >= today_start
        ).count()
        
        messages_today = db.query(Message).filter(
            Message.created_at >= today_start
        ).count()
        
        # Average messages per conversation
        avg_messages = db.query(func.avg(
            db.query(Message).filter(
                Message.conversation_id == Conversation.id
            ).count()
        )).scalar() or 0.0
        
        # Most active day
        most_active_day_data = db.query(
            func.date(Message.created_at).label('date'),
            func.count(Message.id).label('count')
        ).filter(
            Message.created_at >= start_date
        ).group_by(
            func.date(Message.created_at)
        ).order_by(
            desc('count')
        ).first()
        
        most_active_day = most_active_day_data.date.strftime('%Y-%m-%d') if most_active_day_data else "No data"
        
        # AI providers status
        ai_status = await ai_service_manager.health_check()
        
        return DashboardStats(
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_documents=total_documents,
            total_users=total_users,
            active_conversations_today=active_conversations_today,
            messages_today=messages_today,
            avg_messages_per_conversation=round(avg_messages, 2),
            most_active_day=most_active_day,
            ai_providers_status=ai_status
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard stats: {str(e)}")

@router.get("/activity")
async def get_activity_data(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get daily activity data for charts"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily conversation counts
        conversation_data = db.query(
            func.date(Conversation.created_at).label('date'),
            func.count(Conversation.id).label('count')
        ).filter(
            Conversation.created_at >= start_date
        ).group_by(
            func.date(Conversation.created_at)
        ).all()
        
        # Get daily message counts
        message_data = db.query(
            func.date(Message.created_at).label('date'),
            func.count(Message.id).label('count')
        ).filter(
            Message.created_at >= start_date
        ).group_by(
            func.date(Message.created_at)
        ).all()
        
        # Get daily document uploads
        document_data = db.query(
            func.date(Document.created_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            Document.created_at >= start_date
        ).group_by(
            func.date(Document.created_at)
        ).all()
        
        # Combine data by date
        activity_dict = {}
        
        # Initialize with conversation data
        for item in conversation_data:
            date_str = item.date.strftime('%Y-%m-%d')
            activity_dict[date_str] = {
                'date': date_str,
                'conversations': item.count,
                'messages': 0,
                'documents_uploaded': 0
            }
        
        # Add message data
        for item in message_data:
            date_str = item.date.strftime('%Y-%m-%d')
            if date_str in activity_dict:
                activity_dict[date_str]['messages'] = item.count
            else:
                activity_dict[date_str] = {
                    'date': date_str,
                    'conversations': 0,
                    'messages': item.count,
                    'documents_uploaded': 0
                }
        
        # Add document data
        for item in document_data:
            date_str = item.date.strftime('%Y-%m-%d')
            if date_str in activity_dict:
                activity_dict[date_str]['documents_uploaded'] = item.count
            else:
                activity_dict[date_str] = {
                    'date': date_str,
                    'conversations': 0,
                    'messages': 0,
                    'documents_uploaded': item.count
                }
        
        # Convert to list and sort by date
        activity_list = sorted(activity_dict.values(), key=lambda x: x['date'])
        
        return {
            "activity_data": activity_list,
            "period_days": days,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activity data: {str(e)}")

@router.get("/conversations")
async def get_recent_conversations(
    limit: int = Query(20, description="Number of conversations to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get recent conversations with statistics"""
    try:
        conversations = db.query(Conversation).order_by(
            desc(Conversation.updated_at)
        ).limit(limit).all()
        
        conversation_stats = []
        
        for conv in conversations:
            # Count messages
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            # Check for documents
            has_documents = db.query(Document).filter(
                Document.conversation_id == conv.id
            ).first() is not None
            
            # Calculate duration
            duration_minutes = None
            if conv.created_at and conv.updated_at:
                duration = conv.updated_at - conv.created_at
                duration_minutes = duration.total_seconds() / 60
            
            conversation_stats.append(ConversationStats(
                id=conv.id,
                title=conv.title or f"Conversation {conv.id[:8]}",
                message_count=message_count,
                last_activity=conv.updated_at,
                duration_minutes=duration_minutes,
                ai_provider_used=conv.ai_provider,
                has_documents=has_documents
            ))
        
        return {
            "conversations": conversation_stats,
            "total_returned": len(conversation_stats),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@router.get("/ai-providers")
async def get_ai_provider_stats():
    """Get AI provider statistics and status"""
    try:
        providers_info = await ai_service_manager.get_available_providers()
        health_check = await ai_service_manager.health_check()
        
        provider_stats = []
        
        for provider in providers_info:
            # Note: In a real implementation, you'd track these metrics in database
            provider_stats.append(AIProviderStats(
                provider=provider["name"],
                status=provider["status"],
                total_requests=0,  # Would come from tracking table
                avg_response_time=0.0,  # Would come from tracking table
                success_rate=100.0 if provider["status"] == "healthy" else 0.0,
                models_available=provider["models_count"],
                last_used=None  # Would come from tracking table
            ))
        
        return {
            "providers": provider_stats,
            "health_summary": health_check,
            "default_provider": ai_service_manager.default_provider,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI provider stats: {str(e)}")

@router.get("/system-health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """Get overall system health status"""
    try:
        # Database health
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
            db_error = None
        except Exception as e:
            db_status = "unhealthy"
            db_error = str(e)
        
        # AI service health
        ai_health = await ai_service_manager.health_check()
        
        # Memory usage (basic check)
        import psutil
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disk usage
        disk_usage = psutil.disk_usage('/').percent
        
        system_health = {
            "overall_status": "healthy" if all([
                db_status == "healthy",
                ai_health.get("overall_status") == "healthy",
                memory_percent < 90,
                cpu_percent < 90,
                disk_usage < 90
            ]) else "degraded",
            "components": {
                "database": {
                    "status": db_status,
                    "error": db_error
                },
                "ai_service": ai_health,
                "system_resources": {
                    "memory_usage_percent": memory_percent,
                    "cpu_usage_percent": cpu_percent,
                    "disk_usage_percent": disk_usage,
                    "status": "healthy" if all([
                        memory_percent < 90,
                        cpu_percent < 90,
                        disk_usage < 90
                    ]) else "degraded"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return system_health
    
    except Exception as e:
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/export/conversations")
async def export_conversations(
    format: str = Query("json", description="Export format: json, csv"),
    days: int = Query(30, description="Number of days to export"),
    db: AsyncSession = Depends(get_db)
):
    """Export conversation data"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conversations = db.query(Conversation).filter(
            Conversation.created_at >= start_date
        ).all()
        
        export_data = []
        for conv in conversations:
            messages = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).all()
            
            conv_data = {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                "message_count": len(messages),
                "messages": [
                    {
                        "id": msg.id,
                        "content": msg.content,
                        "role": msg.role,
                        "created_at": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in messages
                ]
            }
            export_data.append(conv_data)
        
        if format.lower() == "csv":
            # For CSV, flatten the structure
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow([
                "conversation_id", "conversation_title", "conversation_created",
                "message_id", "message_content", "message_role", "message_created"
            ])
            
            # Write data
            for conv in export_data:
                for msg in conv["messages"]:
                    writer.writerow([
                        conv["id"], conv["title"], conv["created_at"],
                        msg["id"], msg["content"], msg["role"], msg["created_at"]
                    ])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "format": "csv",
                "data": csv_content,
                "count": len(export_data),
                "exported_at": datetime.now().isoformat()
            }
        
        else:  # JSON format
            return {
                "format": "json",
                "data": export_data,
                "count": len(export_data),
                "exported_at": datetime.now().isoformat()
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")


@router.get("/realtime")
async def realtime_dashboard_updates():
    """Real-time dashboard updates via Server-Sent Events"""
    
    async def generate_updates():
        while True:
            try:
                # Get fresh data every 10 seconds
                db = next(get_db())
                
                # Get updated stats
                stats_data = await get_dashboard_stats(db=db)
                yield f"data: {json.dumps({'type': 'stats', 'data': stats_data.dict()})}\n\n"
                
                # Get system health
                health_data = await get_system_health(db=db)
                yield f"data: {json.dumps({'type': 'health', 'data': health_data})}\n\n"
                
                # Get AI provider stats
                ai_providers_data = await get_ai_provider_stats(db=db)
                yield f"data: {json.dumps({'type': 'ai_providers', 'data': {'providers': ai_providers_data}})}\n\n"
                
                # Wait 10 seconds before next update
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"Error in real-time updates: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                await asyncio.sleep(5)
    
    return StreamingResponse(
        generate_updates(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.post("/trigger-update")
async def trigger_dashboard_update(update_type: str, data: Dict[str, Any]):
    """Trigger a dashboard update manually (for testing)"""
    try:
        # This could be used to manually trigger updates
        # For example, when a new message is created, conversation starts, etc.
        
        if update_type == "new_message":
            # Could emit a real-time update about new message
            pass
        elif update_type == "new_conversation":
            # Could emit a real-time update about new conversation
            pass
        elif update_type == "system_alert":
            # Could emit a system alert
            pass
            
        return {"status": "update_triggered", "type": update_type}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering update: {str(e)}")


# Helper functions for real-time data
async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
    """Get fresh dashboard stats"""
    try:
        # Count totals
        total_conversations = db.query(Conversation).count()
        total_messages = db.query(Message).count()
        total_documents = db.query(Document).count()
        total_users = db.query(User).count()
        
        # Today's activity
        today = datetime.now().date()
        active_conversations_today = db.query(Conversation).filter(
            func.date(Conversation.created_at) == today
        ).count()
        
        messages_today = db.query(Message).filter(
            func.date(Message.created_at) == today
        ).count()
        
        # Average messages per conversation
        avg_messages = db.query(func.avg(
            db.query(Message).filter(
                Message.conversation_id == Conversation.id
            ).count()
        )).scalar() or 0
        
        # Most active day (simplified)
        most_active_day = datetime.now().strftime("%Y-%m-%d")
        
        # AI providers status
        ai_providers_status = {}
        try:
            providers = await ai_service_manager.get_available_providers()
            for provider_name in providers:
                provider = ai_service_manager.get_provider(provider_name)
                if provider:
                    models = await provider.get_available_models()
                    ai_providers_status[provider_name] = {
                        "status": "healthy",
                        "models": len(models)
                    }
        except Exception as e:
            ai_providers_status = {"error": str(e)}
        
        return DashboardStats(
            total_conversations=total_conversations,
            total_messages=total_messages,
            total_documents=total_documents,
            total_users=total_users,
            active_conversations_today=active_conversations_today,
            messages_today=messages_today,
            avg_messages_per_conversation=float(avg_messages),
            most_active_day=most_active_day,
            ai_providers_status=ai_providers_status
        )
        
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return DashboardStats(
            total_conversations=0,
            total_messages=0,
            total_documents=0,
            total_users=0,
            active_conversations_today=0,
            messages_today=0,
            avg_messages_per_conversation=0.0,
            most_active_day="",
            ai_providers_status={}
        )


# New simplified dashboard endpoints using DashboardStatsService
@router.get("/stats/overview")
async def get_overview_stats_new(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get overview statistics using new service"""
    try:
        stats_service = DashboardStatsService(db)
        return await stats_service.get_overview_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overview stats: {str(e)}")


@router.get("/stats/performance") 
async def get_performance_stats_new(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get system performance statistics using new service"""
    try:
        stats_service = DashboardStatsService(db)
        return await stats_service.get_system_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")


@router.get("/stats/all")
async def get_all_dashboard_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive dashboard statistics using new service"""
    try:
        stats_service = DashboardStatsService(db)
        
        # Get all dashboard data
        overview = await stats_service.get_overview_stats()
        performance = await stats_service.get_system_performance()
        activity = await stats_service.get_recent_activity()
        analytics = await stats_service.get_usage_analytics()
        documents = await stats_service.get_document_stats()
        
        return {
            "overview": overview,
            "performance": performance,
            "recent_activity": activity,
            "analytics": analytics,
            "documents": documents,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")
