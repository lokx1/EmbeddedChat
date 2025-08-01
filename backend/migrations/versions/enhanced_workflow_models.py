"""
Enhanced workflow models migration
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'enhanced_workflow_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create workflow_execution_steps table
    op.create_table('workflow_execution_steps',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_instance_id', sa.String(), nullable=False),
        sa.Column('step_name', sa.String(255), nullable=False),
        sa.Column('step_type', sa.String(100), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['workflow_instance_id'], ['workflow_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_execution_steps_workflow_instance_id'), 'workflow_execution_steps', ['workflow_instance_id'], unique=False)
    op.create_index(op.f('ix_workflow_execution_steps_status'), 'workflow_execution_steps', ['status'], unique=False)
    op.create_index(op.f('ix_workflow_execution_steps_step_type'), 'workflow_execution_steps', ['step_type'], unique=False)

    # Add new columns to existing workflow_instances table if they don't exist
    try:
        op.add_column('workflow_instances', sa.Column('execution_logs', sa.JSON(), nullable=True))
    except Exception:
        # Column might already exist
        pass

    # Create indexes for better performance
    op.create_index('ix_workflow_instances_status', 'workflow_instances', ['status'], unique=False)
    op.create_index('ix_workflow_instances_created_by', 'workflow_instances', ['created_by'], unique=False)
    op.create_index('ix_workflow_templates_category', 'workflow_templates', ['category'], unique=False)
    op.create_index('ix_workflow_templates_is_public', 'workflow_templates', ['is_public'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('ix_workflow_templates_is_public', table_name='workflow_templates')
    op.drop_index('ix_workflow_templates_category', table_name='workflow_templates')
    op.drop_index('ix_workflow_instances_created_by', table_name='workflow_instances')
    op.drop_index('ix_workflow_instances_status', table_name='workflow_instances')
    
    # Drop execution_logs column
    try:
        op.drop_column('workflow_instances', 'execution_logs')
    except Exception:
        pass
    
    # Drop workflow_execution_steps table
    op.drop_index(op.f('ix_workflow_execution_steps_step_type'), table_name='workflow_execution_steps')
    op.drop_index(op.f('ix_workflow_execution_steps_status'), table_name='workflow_execution_steps')
    op.drop_index(op.f('ix_workflow_execution_steps_workflow_instance_id'), table_name='workflow_execution_steps')
    op.drop_table('workflow_execution_steps')
