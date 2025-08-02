"""
Check workflow execution logs in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.workflow import WorkflowExecutionStep
from src.core.config import settings

def check_execution_logs():
    """Check latest workflow execution logs"""
    print("🔍 Checking workflow execution logs...")
    
    try:
        # Create database connection
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get latest execution steps
        steps = db.query(WorkflowExecutionStep).order_by(
            WorkflowExecutionStep.created_at.desc()
        ).limit(10).all()
        
        print(f"📊 Found {len(steps)} recent execution steps:")
        
        for i, step in enumerate(steps, 1):
            print(f"\n📝 Step {i}:")
            print(f"   ID: {step.id}")
            print(f"   Node ID: {step.node_id}")
            print(f"   Step Type: {step.step_type}")
            print(f"   Status: {step.status}")
            print(f"   Created: {step.created_at}")
            print(f"   Error: {step.error_message}")
            
            if step.input_data:
                print(f"   Input Data: {step.input_data}")
            if step.output_data:
                print(f"   Output Data: {step.output_data}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_execution_logs()
