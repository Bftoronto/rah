"""Create moderation tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы жалоб
    op.create_table('moderation_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы действий модераторов
    op.create_table('moderation_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('moderator_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы правил модерации
    op.create_table('moderation_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы фильтров контента
    op.create_table('content_filters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filter_type', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('replacement', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы доверия пользователей
    op.create_table('trust_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('level', sa.String(), nullable=True),
        sa.Column('warnings_count', sa.Integer(), nullable=True),
        sa.Column('reports_count', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов для оптимизации
    op.create_index(op.f('ix_moderation_reports_reporter_id'), 'moderation_reports', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_moderation_reports_target_type'), 'moderation_reports', ['target_type'], unique=False)
    op.create_index(op.f('ix_moderation_reports_target_id'), 'moderation_reports', ['target_id'], unique=False)
    op.create_index(op.f('ix_moderation_reports_status'), 'moderation_reports', ['status'], unique=False)
    op.create_index(op.f('ix_moderation_reports_created_at'), 'moderation_reports', ['created_at'], unique=False)
    
    op.create_index(op.f('ix_moderation_actions_report_id'), 'moderation_actions', ['report_id'], unique=False)
    op.create_index(op.f('ix_moderation_actions_moderator_id'), 'moderation_actions', ['moderator_id'], unique=False)
    op.create_index(op.f('ix_moderation_actions_action'), 'moderation_actions', ['action'], unique=False)
    
    op.create_index(op.f('ix_moderation_rules_is_active'), 'moderation_rules', ['is_active'], unique=False)
    op.create_index(op.f('ix_moderation_rules_severity'), 'moderation_rules', ['severity'], unique=False)
    
    op.create_index(op.f('ix_content_filters_filter_type'), 'content_filters', ['filter_type'], unique=False)
    op.create_index(op.f('ix_content_filters_is_active'), 'content_filters', ['is_active'], unique=False)
    
    op.create_index(op.f('ix_trust_scores_user_id'), 'trust_scores', ['user_id'], unique=True)
    op.create_index(op.f('ix_trust_scores_level'), 'trust_scores', ['level'], unique=False)
    
    # Добавление внешних ключей
    op.create_foreign_key('fk_moderation_reports_reporter_id', 'moderation_reports', 'users', ['reporter_id'], ['id'])
    op.create_foreign_key('fk_moderation_actions_report_id', 'moderation_actions', 'moderation_reports', ['report_id'], ['id'])
    op.create_foreign_key('fk_moderation_actions_moderator_id', 'moderation_actions', 'users', ['moderator_id'], ['id'])
    op.create_foreign_key('fk_trust_scores_user_id', 'trust_scores', 'users', ['user_id'], ['id'])


def downgrade():
    # Удаление внешних ключей
    op.drop_constraint('fk_trust_scores_user_id', 'trust_scores', type_='foreignkey')
    op.drop_constraint('fk_moderation_actions_moderator_id', 'moderation_actions', type_='foreignkey')
    op.drop_constraint('fk_moderation_actions_report_id', 'moderation_actions', type_='foreignkey')
    op.drop_constraint('fk_moderation_reports_reporter_id', 'moderation_reports', type_='foreignkey')
    
    # Удаление индексов
    op.drop_index(op.f('ix_trust_scores_level'), table_name='trust_scores')
    op.drop_index(op.f('ix_trust_scores_user_id'), table_name='trust_scores')
    op.drop_index(op.f('ix_content_filters_is_active'), table_name='content_filters')
    op.drop_index(op.f('ix_content_filters_filter_type'), table_name='content_filters')
    op.drop_index(op.f('ix_moderation_rules_severity'), table_name='moderation_rules')
    op.drop_index(op.f('ix_moderation_rules_is_active'), table_name='moderation_rules')
    op.drop_index(op.f('ix_moderation_actions_action'), table_name='moderation_actions')
    op.drop_index(op.f('ix_moderation_actions_moderator_id'), table_name='moderation_actions')
    op.drop_index(op.f('ix_moderation_actions_report_id'), table_name='moderation_actions')
    op.drop_index(op.f('ix_moderation_reports_created_at'), table_name='moderation_reports')
    op.drop_index(op.f('ix_moderation_reports_status'), table_name='moderation_reports')
    op.drop_index(op.f('ix_moderation_reports_target_id'), table_name='moderation_reports')
    op.drop_index(op.f('ix_moderation_reports_target_type'), table_name='moderation_reports')
    op.drop_index(op.f('ix_moderation_reports_reporter_id'), table_name='moderation_reports')
    
    # Удаление таблиц
    op.drop_table('trust_scores')
    op.drop_table('content_filters')
    op.drop_table('moderation_rules')
    op.drop_table('moderation_actions')
    op.drop_table('moderation_reports') 