"""
Database initialization script for workflow tables
Run this to create the workflow tables in your database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from src.core.config import settings
from src.models.workflow import Base
from src.core.database import sync_engine

def create_workflow_tables():
    """Create workflow tables in the database"""
    try:
        print("Creating workflow tables...")
        
        # Create all tables defined in workflow models
        Base.metadata.create_all(bind=sync_engine)
        
        print("✅ Workflow tables created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_workflow_tables()
