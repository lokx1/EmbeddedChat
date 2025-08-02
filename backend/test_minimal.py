#!/usr/bin/env python3
"""
Minimal test for workflow_logs router
"""
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    print("Testing individual components...")
    
    # Test APIRouter
    from fastapi import APIRouter
    print("✅ APIRouter imported")
    
    # Test database
    from src.core.database import get_db
    print("✅ get_db imported")
    
    # Test basic models import
    print("Testing models...")
    from src.models import workflow
    print("✅ workflow module imported")
    
    # Test specific model classes
    from src.models.workflow import WorkflowTaskLog
    print("✅ WorkflowTaskLog imported")
    
    from src.models.workflow import WorkflowExecutionStep  
    print("✅ WorkflowExecutionStep imported")
    
    # Test schemas
    print("Testing schemas...")
    from src.schemas import workflow_logs
    print("✅ workflow_logs schema module imported")
    
    from src.schemas.workflow_logs import WorkflowTaskLogResponse
    print("✅ WorkflowTaskLogResponse imported")
    
    # Now test the actual router import
    print("Testing router...")
    from src.api.routes.workflow_logs import router
    print("✅ Router imported successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
