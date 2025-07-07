"""Create notification tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы логов уведомлений
    op.create_table('notification_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('telegram_response', sqlite.JSON, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание таблицы настроек уведомлений
    op.create_table('notification_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ride_notifications', sa.Boolean(), nullable=True),
        sa.Column('system_notifications', sa.Boolean(), nullable=True),
        sa.Column('reminder_notifications', sa.Boolean(), nullable=True),
        sa.Column('marketing_notifications', sa.Boolean(), nullable=True),
        sa.Column('quiet_hours_start', sa.String(), nullable=True),
        sa.Column('quiet_hours_end', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов для оптимизации
    op.create_index(op.f('ix_notification_logs_user_id'), 'notification_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_notification_logs_notification_type'), 'notification_logs', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notification_logs_sent_at'), 'notification_logs', ['sent_at'], unique=False)
    op.create_index(op.f('ix_notification_settings_user_id'), 'notification_settings', ['user_id'], unique=True)


def downgrade():
    # Удаление индексов
    op.drop_index(op.f('ix_notification_settings_user_id'), table_name='notification_settings')
    op.drop_index(op.f('ix_notification_logs_sent_at'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_notification_type'), table_name='notification_logs')
    op.drop_index(op.f('ix_notification_logs_user_id'), table_name='notification_logs')
    
    # Удаление таблиц
    op.drop_table('notification_settings')
    op.drop_table('notification_logs') 