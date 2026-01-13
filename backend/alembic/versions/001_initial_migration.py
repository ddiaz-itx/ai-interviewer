"""Initial migration - create interviews and messages tables

Revision ID: 001
Revises: 
Create Date: 2026-01-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('resume_path', sa.String(length=500), nullable=True),
        sa.Column('role_path', sa.String(length=500), nullable=True),
        sa.Column('job_offering_path', sa.String(length=500), nullable=True),
        sa.Column('match_analysis_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_questions', sa.Integer(), nullable=False),
        sa.Column('difficulty_start', sa.Integer(), nullable=False),
        sa.Column('candidate_link_token', sa.String(length=255), nullable=True),
        sa.Column('report_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_id'), 'interviews', ['id'], unique=False)
    op.create_index(op.f('ix_interviews_status'), 'interviews', ['status'], unique=False)
    op.create_index(op.f('ix_interviews_candidate_link_token'), 'interviews', ['candidate_link_token'], unique=True)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.Float(), nullable=True),
        sa.Column('answer_quality_score', sa.Integer(), nullable=True),
        sa.Column('cheat_certainty', sa.Float(), nullable=True),
        sa.Column('telemetry', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.create_index(op.f('ix_messages_interview_id'), 'messages', ['interview_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_interview_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_interviews_candidate_link_token'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_status'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_id'), table_name='interviews')
    op.drop_table('interviews')
