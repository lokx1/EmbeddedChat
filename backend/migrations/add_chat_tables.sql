-- Migration: Add Chat Conversation and Message Tables
-- PostgreSQL version - Creates tables for modern chat functionality with conversation management

-- Chat Conversations Table
CREATE TABLE IF NOT EXISTS chat_conversations (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL DEFAULT 'New Chat',
    user_id INTEGER NOT NULL,
    
    -- AI Provider settings for this conversation
    ai_provider VARCHAR(50) NOT NULL DEFAULT 'openai',
    ai_model VARCHAR(100) NOT NULL DEFAULT 'gpt-4o',
    system_prompt TEXT DEFAULT 'You are a helpful AI assistant.',
    temperature INTEGER DEFAULT 70,  -- Stored as int (0.7 * 100)
    max_tokens INTEGER DEFAULT 2000,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    
    -- Statistics
    message_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    
    -- Foreign key constraint
    CONSTRAINT fk_chat_conversations_user_id 
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    
    -- Message content
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- AI Response metadata (for assistant messages)
    ai_provider VARCHAR(50),
    ai_model VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    response_time_ms INTEGER,
    
    -- File attachments (JSON array)
    attachments JSONB,  -- PostgreSQL native JSON format
    
    -- Message status
    is_edited BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Foreign key constraint
    CONSTRAINT fk_chat_messages_conversation_id 
        FOREIGN KEY (conversation_id) REFERENCES chat_conversations (id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_updated_at ON chat_conversations(updated_at);
CREATE INDEX IF NOT EXISTS idx_chat_conversations_is_archived ON chat_conversations(is_archived);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages(role);

-- PostgreSQL Function for updating conversation timestamp
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_conversations 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PostgreSQL Function for incrementing message count
CREATE OR REPLACE FUNCTION increment_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_conversations 
    SET message_count = message_count + 1 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PostgreSQL Function for decrementing message count
CREATE OR REPLACE FUNCTION decrement_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_deleted = TRUE AND OLD.is_deleted = FALSE THEN
        UPDATE chat_conversations 
        SET message_count = message_count - 1 
        WHERE id = NEW.conversation_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS trigger_update_conversation_updated_at ON chat_messages;
CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();

DROP TRIGGER IF EXISTS trigger_increment_message_count ON chat_messages;
CREATE TRIGGER trigger_increment_message_count
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION increment_message_count();

DROP TRIGGER IF EXISTS trigger_decrement_message_count ON chat_messages;
CREATE TRIGGER trigger_decrement_message_count
    AFTER UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION decrement_message_count();
