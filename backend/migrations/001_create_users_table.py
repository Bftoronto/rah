"""Создание таблиц пользователей

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы пользователей
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_driver', sa.Boolean(), nullable=True),
        sa.Column('privacy_policy_version', sa.String(), nullable=True),
        sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=True),
        sa.Column('privacy_policy_accepted_at', sa.DateTime(), nullable=True),
        sa.Column('car_brand', sa.String(), nullable=True),
        sa.Column('car_model', sa.String(), nullable=True),
        sa.Column('car_year', sa.Integer(), nullable=True),
        sa.Column('car_color', sa.String(), nullable=True),
        sa.Column('driver_license_number', sa.String(), nullable=True),
        sa.Column('driver_license_photo_url', sa.String(), nullable=True),
        sa.Column('car_photo_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('total_rides', sa.Integer(), nullable=True),
        sa.Column('cancelled_rides', sa.Integer(), nullable=True),
        sa.Column('profile_history', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    
    # Создание таблицы истории изменений профиля
    op.create_table('profile_change_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('changed_at', sa.DateTime(), nullable=True),
        sa.Column('changed_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индекса для истории изменений
    op.create_index(op.f('ix_profile_change_logs_id'), 'profile_change_logs', ['id'], unique=False)
    op.create_index('ix_profile_change_logs_user_id', 'profile_change_logs', ['user_id'], unique=False)


def downgrade():
    # Удаление таблиц
    op.drop_index('ix_profile_change_logs_user_id', table_name='profile_change_logs')
    op.drop_index(op.f('ix_profile_change_logs_id'), table_name='profile_change_logs')
    op.drop_table('profile_change_logs')
    
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users') 