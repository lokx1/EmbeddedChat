"""
Script to add sample workflow data for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.core.database import get_db_session
from src.models.workflow import WorkflowTemplate, WorkflowInstance
import uuid
from datetime import datetime

def create_sample_data():
    """Create sample workflow templates and instances"""
    db = get_db_session()
    
    try:
        # Create sample template
        template = WorkflowTemplate(
            id=str(uuid.uuid4()),
            name="Google Sheets to PDF Automation",
            description="Automate processing Google Sheets data and generate PDF reports",
            template_data={
                "nodes": [
                    {"id": "1", "type": "input", "position": {"x": 100, "y": 100}, "data": {"label": "Google Sheets Input", "type": "sheets"}},
                    {"id": "2", "type": "ai", "position": {"x": 300, "y": 100}, "data": {"label": "AI Processing", "type": "openai"}},
                    {"id": "3", "type": "output", "position": {"x": 500, "y": 100}, "data": {"label": "Generate PDF", "type": "pdf"}}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2"},
                    {"id": "e2-3", "source": "2", "target": "3"}
                ]
            },
            category="automation",
            is_public=True
        )
        
        db.add(template)
        
        # Create sample instances
        instance1 = WorkflowInstance(
            id=str(uuid.uuid4()),
            name="Product Description Generation",
            template_id=template.id,
            workflow_data=template.template_data,
            status="completed",
            input_data={
                "sheets_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                "ai_prompt": "Generate product descriptions",
                "output_format": "pdf"
            },
            output_data={
                "generated_files": ["https://drive.google.com/file/d/example1/view"],
                "processed_rows": 25,
                "success_rate": 96.0
            },
            started_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        instance2 = WorkflowInstance(
            id=str(uuid.uuid4()),
            name="Marketing Content Creation",
            template_id=template.id,
            workflow_data=template.template_data,
            status="draft",
            input_data={
                "sheets_id": "1234567890abcdef",
                "ai_prompt": "Create marketing copy",
                "output_format": "pdf"
            }
        )
        
        instance3 = WorkflowInstance(
            id=str(uuid.uuid4()),
            name="Customer Survey Analysis",
            workflow_data={
                "nodes": [
                    {"id": "1", "type": "input", "position": {"x": 100, "y": 100}, "data": {"label": "Survey Data", "type": "sheets"}},
                    {"id": "2", "type": "ai", "position": {"x": 300, "y": 100}, "data": {"label": "Sentiment Analysis", "type": "claude"}},
                    {"id": "3", "type": "output", "position": {"x": 500, "y": 100}, "data": {"label": "Analytics Report", "type": "report"}}
                ],
                "edges": [
                    {"id": "e1-2", "source": "1", "target": "2"},
                    {"id": "e2-3", "source": "2", "target": "3"}
                ]
            },
            status="running",
            input_data={
                "sheets_id": "survey_data_2025",
                "analysis_type": "sentiment",
                "output_format": "dashboard"
            },
            started_at=datetime.now()
        )
        
        db.add_all([instance1, instance2, instance3])
        db.commit()
        
        print("✅ Sample workflow data created successfully!")
        print(f"   - 1 Template: {template.name}")
        print(f"   - 3 Instances:")
        print(f"     • {instance1.name} (completed)")
        print(f"     • {instance2.name} (draft)")
        print(f"     • {instance3.name} (running)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
