# Dashboard statistics service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, text
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psutil
import asyncio
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.document import Document
from src.models.user import User
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DashboardStatsService:
    """Service for collecting and providing dashboard statistics"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_overview_stats(self) -> Dict[str, Any]:
        """Get main dashboard overview statistics"""
        try:
            # Total conversations
            total_chats_query = select(func.count(Conversation.id))
            total_chats_result = await self.db.execute(total_chats_query)
            total_chats = total_chats_result.scalar() or 0
            
            # Active users (users with activity in last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            active_users_query = select(func.count(func.distinct(Message.user_id))).where(
                Message.created_at >= yesterday
            )
            active_users_result = await self.db.execute(active_users_query)
            active_users = active_users_result.scalar() or 0
            
            # Total documents
            total_docs_query = select(func.count(Document.id))
            total_docs_result = await self.db.execute(total_docs_query)
            total_docs = total_docs_result.scalar() or 0
            
            # System status (simplified)
            system_status = "Healthy"
            
            return {
                "total_chats": total_chats,
                "active_users": active_users,
                "total_documents": total_docs,
                "system_status": system_status
            }
        except Exception as e:
            # Return default values if database is not available
            return {
                "total_chats": 0,
                "active_users": 0,
                "total_documents": 0,
                "system_status": "Unknown"
            }
    
    async def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # Get system metrics using psutil
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Calculate uptime (simplified - using process uptime)
            import time
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = int(uptime_seconds // 3600)
            uptime_minutes = int((uptime_seconds % 3600) // 60)
            uptime_secs = int(uptime_seconds % 60)
            uptime_str = f"{uptime_hours}:{uptime_minutes:02d}:{uptime_secs:02d}"
            
            return {
                "memory_usage": {
                    "percent": memory.percent,
                    "used_gb": round(memory.used / (1024**3), 2),
                    "total_gb": round(memory.total / (1024**3), 2)
                },
                "cpu_usage": {
                    "percent": cpu_percent
                },
                "uptime": uptime_str
            }
        except Exception:
            return {
                "memory_usage": {"percent": 0, "used_gb": 0, "total_gb": 0},
                "cpu_usage": {"percent": 0},
                "uptime": "0:00:00"
            }
    
    async def get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        try:
            # Recent messages/conversations
            recent_messages_query = select(
                Message.content,
                Message.created_at,
                User.username
            ).join(User).order_by(Message.created_at.desc()).limit(10)
            
            result = await self.db.execute(recent_messages_query)
            recent_messages = result.fetchall()
            
            activities = []
            for msg in recent_messages:
                time_diff = datetime.utcnow() - msg.created_at
                if time_diff.seconds < 3600:
                    time_str = f"{time_diff.seconds // 60} minutes ago"
                elif time_diff.seconds < 86400:
                    time_str = f"{time_diff.seconds // 3600} hours ago"
                else:
                    time_str = f"{time_diff.days} days ago"
                
                activities.append({
                    "action": "New message",
                    "details": f"Message from {msg.username}: {msg.content[:50]}...",
                    "time": time_str,
                    "type": "message"
                })
            
            return activities[:5]  # Return last 5 activities
        except Exception:
            return []
    
    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics for charts"""
        try:
            # Messages per day for last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            daily_messages_query = select(
                func.date(Message.created_at).label('date'),
                func.count(Message.id).label('count')
            ).where(
                Message.created_at >= thirty_days_ago
            ).group_by(
                func.date(Message.created_at)
            ).order_by('date')
            
            result = await self.db.execute(daily_messages_query)
            daily_data = result.fetchall()
            
            # Convert to chart format
            chart_data = []
            for day in daily_data:
                chart_data.append({
                    "date": day.date.strftime("%Y-%m-%d"),
                    "messages": day.count
                })
            
            return {
                "daily_messages": chart_data,
                "total_period": len(chart_data)
            }
        except Exception:
            return {
                "daily_messages": [],
                "total_period": 0
            }
    
    async def get_document_stats(self) -> Dict[str, Any]:
        """Get document-related statistics with vector store integration"""
        try:
            # Import services here to avoid circular imports
            from ...services.document.storage_service import storage_service
            from ...services.rag.vector_store import vector_store
            
            # Get comprehensive storage stats
            storage_stats = await storage_service.get_storage_stats(self.db)
            
            # Get vector store stats
            try:
                vector_stats = await vector_store.get_collection_stats()
            except Exception as e:
                logger.warning(f"Could not get vector store stats: {e}")
                vector_stats = {"total_documents": 0}
            
            # Document status breakdown
            status_query = select(
                Document.status,
                func.count(Document.id).label('count')
            ).group_by(Document.status)
            status_result = await self.db.execute(status_query)
            status_breakdown = {row.status: row.count for row in status_result}
            
            return {
                "total_documents": storage_stats["total_documents"],
                "storage_used": storage_stats["storage_used"],
                "storage_bytes": storage_stats["storage_bytes"],
                "indexed": storage_stats["indexed"],
                "categories": storage_stats["categories"],
                "vector_store_docs": vector_stats.get("total_documents", 0),
                "status_breakdown": status_breakdown,
                "processing_queue": status_breakdown.get("processing", 0),
                "failed_uploads": status_breakdown.get("error", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get document stats: {e}")
            return {
                "total_documents": 0,
                "storage_used": "0 GB",
                "storage_bytes": 0,
                "indexed": 0,
                "categories": 0,
                "vector_store_docs": 0,
                "status_breakdown": {},
                "processing_queue": 0,
                "failed_uploads": 0
            }
