# Unit tests for models
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.database import Base
from src.models.user import User
from src.models.conversation import Conversation  
from src.models.message import Message, MessageType
from src.models.document import Document, DocumentStatus


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def async_session():
    """Create async test database session"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_user_model(async_session: AsyncSession):
    """Test User model creation"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_conversation_model(async_session: AsyncSession):
    """Test Conversation model creation"""
    # Create user first
    user = User(
        username="testuser",
        email="test@example.com", 
        hashed_password="hashed_password"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Create conversation
    conversation = Conversation(
        title="Test Conversation",
        description="A test conversation",
        user_id=user.id
    )
    
    async_session.add(conversation)
    await async_session.commit()
    await async_session.refresh(conversation)
    
    assert conversation.id is not None
    assert conversation.title == "Test Conversation"
    assert conversation.user_id == user.id
    assert conversation.is_active is True


@pytest.mark.asyncio
async def test_message_model(async_session: AsyncSession):
    """Test Message model creation"""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Create conversation
    conversation = Conversation(
        title="Test Conversation",
        user_id=user.id
    )
    async_session.add(conversation)
    await async_session.commit()
    await async_session.refresh(conversation)
    
    # Create message
    message = Message(
        content="Hello, world!",
        message_type=MessageType.USER,
        conversation_id=conversation.id,
        user_id=user.id
    )
    
    async_session.add(message)
    await async_session.commit()
    await async_session.refresh(message)
    
    assert message.id is not None
    assert message.content == "Hello, world!"
    assert message.message_type == MessageType.USER
    assert message.conversation_id == conversation.id
    assert message.user_id == user.id
    assert message.is_edited is False


@pytest.mark.asyncio
async def test_document_model(async_session: AsyncSession):
    """Test Document model creation"""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Create document
    document = Document(
        filename="test.pdf",
        original_filename="test_document.pdf",
        file_path="/uploads/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        user_id=user.id,
        status=DocumentStatus.UPLOADING
    )
    
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)
    
    assert document.id is not None
    assert document.filename == "test.pdf"
    assert document.original_filename == "test_document.pdf"
    assert document.file_size == 1024
    assert document.status == DocumentStatus.UPLOADING
    assert document.user_id == user.id
    assert document.chunk_count == 0


@pytest.mark.asyncio
async def test_user_conversation_relationship(async_session: AsyncSession):
    """Test User-Conversation relationship"""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Create conversations
    conv1 = Conversation(title="Conv 1", user_id=user.id)
    conv2 = Conversation(title="Conv 2", user_id=user.id)
    
    async_session.add_all([conv1, conv2])
    await async_session.commit()
    
    # Refresh and check relationships
    await async_session.refresh(user)
    assert len(user.conversations) == 2


@pytest.mark.asyncio 
async def test_conversation_message_relationship(async_session: AsyncSession):
    """Test Conversation-Message relationship"""
    # Create user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    
    # Create conversation
    conversation = Conversation(title="Test", user_id=user.id)
    async_session.add(conversation)
    await async_session.commit()
    await async_session.refresh(conversation)
    
    # Create messages
    msg1 = Message(
        content="Message 1",
        message_type=MessageType.USER,
        conversation_id=conversation.id,
        user_id=user.id
    )
    msg2 = Message(
        content="Message 2", 
        message_type=MessageType.ASSISTANT,
        conversation_id=conversation.id,
        user_id=user.id
    )
    
    async_session.add_all([msg1, msg2])
    await async_session.commit()
    
    # Refresh and check relationships
    await async_session.refresh(conversation)
    assert len(conversation.messages) == 2
