# Database seeding script
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
import random
from sqlalchemy import select
from src.models.database import AsyncSessionLocal
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.document import Document


async def seed_database():
    """Seed database with sample data"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if we already have data
            result = await db.execute(select(User))
            existing_users = result.fetchall()
            
            # Check documents separately 
            doc_result = await db.execute(select(Document))
            existing_docs = doc_result.fetchall()
            
            if len(existing_users) > 5 and len(existing_docs) > 5:
                print("Database already has sufficient data. Skipping seed...")
                return
            
            print("Seeding database with sample data...")
            
            # Get existing users if they exist
            if len(existing_users) >= 5:
                users = existing_users[:5]
                print(f"Using existing {len(users)} users")
            else:
                # Create sample users
                users = []
                for i in range(5):
                    user = User(
                        username=f"user{i+1}",
                        email=f"user{i+1}@example.com",
                        hashed_password="$2b$12$dummy_hash_for_demo",
                        is_active=True
                    )
                    db.add(user)
                    users.append(user)
                
                await db.commit()
                
                # Refresh to get IDs
                for user in users:
                    await db.refresh(user)
            
            # Create sample conversations and messages
            conv_result = await db.execute(select(Conversation))
            existing_convs = conv_result.fetchall()
            
            if len(existing_convs) < 10:
                conversations = []
                for i in range(15):
                    user = random.choice(users)
                    
                    # Create conversation with varying dates (last 30 days)
                    days_ago = random.randint(0, 30)
                    created_at = datetime.utcnow() - timedelta(days=days_ago)
                    
                    conversation = Conversation(
                        title=f"Chat about {random.choice(['AI', 'Programming', 'Data Science', 'Web Development', 'Machine Learning'])}",
                        user_id=user.id,
                        created_at=created_at,
                        updated_at=created_at
                    )
                    db.add(conversation)
                    conversations.append(conversation)
                
                await db.commit()
                
                # Refresh conversations to get IDs
                for conv in conversations:
                    await db.refresh(conv)
            else:
                conversations = existing_convs
                print(f"Using existing {len(conversations)} conversations")
            
            # Create sample messages
            message_templates = [
                "Hello, I need help with {topic}",
                "Can you explain {topic} to me?",
                "I'm working on a project involving {topic}",
                "What are the best practices for {topic}?",
                "I'm having trouble understanding {topic}",
                "Could you provide an example of {topic}?",
                "How do I implement {topic} in my code?",
                "What are the advantages of {topic}?",
                "I found an error in my {topic} implementation",
                "Thanks for your help with {topic}!"
            ]
            
            topics = [
                "machine learning", "web development", "database design", 
                "API development", "React components", "Python functions",
                "data visualization", "algorithm optimization", "security",
                "performance tuning"
            ]
            
            for conv in conversations:
                # Random number of messages per conversation (2-10)
                num_messages = random.randint(2, 10)
                
                for j in range(num_messages):
                    # Alternate between user and assistant messages
                    is_user = j % 2 == 0
                    
                    if is_user:
                        content = random.choice(message_templates).format(
                            topic=random.choice(topics)
                        )
                        message_type = "user"
                    else:
                        content = f"I'd be happy to help you with that! Here's a detailed explanation of {random.choice(topics)}..."
                        message_type = "assistant"
                    
                    # Messages within the conversation timeframe
                    message_time = conv.created_at + timedelta(minutes=j*5)
                    
                    message = Message(
                        content=content,
                        message_type=message_type,
                        conversation_id=conv.id,
                        user_id=conv.user_id,
                        created_at=message_time
                    )
                    db.add(message)
            
            # Create sample documents
            document_names = [
                "API Documentation.pdf",
                "User Guide.docx", 
                "Technical Specifications.md",
                "Database Schema.sql",
                "Project Requirements.txt",
                "Installation Guide.pdf",
                "Troubleshooting Manual.docx",
                "Code Examples.py",
                "Architecture Overview.md",
                "Security Guidelines.pdf"
            ]
            
            categories = ["Technical", "Business", "Personal", "Documentation"]
            
            for i, doc_name in enumerate(document_names):
                # Random upload date (last 60 days)
                days_ago = random.randint(0, 60)
                uploaded_at = datetime.utcnow() - timedelta(days=days_ago)
                
                document = Document(
                    filename=doc_name,
                    original_filename=doc_name,
                    file_path=f"/uploads/{doc_name.lower().replace(' ', '_')}",
                    file_size=random.randint(1024, 5242880),  # 1KB to 5MB
                    mime_type="application/pdf" if doc_name.endswith('.pdf') else "text/plain",
                    user_id=random.choice(users).id,
                    status="processed",
                    category=random.choice(categories),
                    created_at=uploaded_at
                )
                db.add(document)
            
            await db.commit()
            print("Database seeded successfully!")
            
            # Print summary
            user_count = await db.execute(select(User))
            conv_count = await db.execute(select(Conversation))
            msg_count = await db.execute(select(Message))
            doc_count = await db.execute(select(Document))
            
            print(f"Created:")
            print(f"- {len(user_count.fetchall())} users")
            print(f"- {len(conv_count.fetchall())} conversations") 
            print(f"- {len(msg_count.fetchall())} messages")
            print(f"- {len(doc_count.fetchall())} documents")
        
        except Exception as e:
            print(f"Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
