#!/usr/bin/env python3
"""
Test workflow_logs router import
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("Testing workflow_logs import...")
    
    # Test step by step imports
    print("1. Importing APIRouter...")
    from fastapi import APIRouter
    
    print("2. Importing database dependencies...")
    from src.core.database import get_db
    
    print("3. Importing models...")
    from src.models.workflow import WorkflowTaskLog, WorkflowExecutionStep
    
    print("4. Importing schemas...")
    from src.schemas.workflow_logs import WorkflowTaskLogResponse, LogSummaryResponse
    
    print("5. Importing workflow_logs router...")
    from src.api.routes.workflow_logs import router
    
    print(f"✅ Router imported successfully!")
    print(f"   Prefix: {router.prefix}")
    print(f"   Tags: {router.tags}")
    print(f"   Routes count: {len(router.routes)}")
    
    for route in router.routes:
        print(f"   - {list(route.methods)} {route.path}")
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
