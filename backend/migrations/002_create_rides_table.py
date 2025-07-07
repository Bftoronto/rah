"""Создание таблицы поездок

Revision ID: 002
Revises: 001
Create Date: 2024-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы поездок
    op.create_table('rides',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=False),
        sa.Column('passenger_id', sa.Integer(), nullable=True),
        sa.Column('from_location', sa.String(), nullable=False),
        sa.Column('to_location', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('seats', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['passenger_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Создание индексов для поездок
    op.create_index(op.f('ix_rides_id'), 'rides', ['id'], unique=False)
    op.create_index('ix_rides_driver_id', 'rides', ['driver_id'], unique=False)
    op.create_index('ix_rides_passenger_id', 'rides', ['passenger_id'], unique=False)
    op.create_index('ix_rides_status', 'rides', ['status'], unique=False)
    op.create_index('ix_rides_date', 'rides', ['date'], unique=False)
    op.create_index('ix_rides_from_location', 'rides', ['from_location'], unique=False)
    op.create_index('ix_rides_to_location', 'rides', ['to_location'], unique=False)
    op.create_index('ix_rides_price', 'rides', ['price'], unique=False)
    op.create_index('ix_rides_created_at', 'rides', ['created_at'], unique=False)


def downgrade():
    # Удаление индексов
    op.drop_index('ix_rides_created_at', table_name='rides')
    op.drop_index('ix_rides_price', table_name='rides')
    op.drop_index('ix_rides_to_location', table_name='rides')
    op.drop_index('ix_rides_from_location', table_name='rides')
    op.drop_index('ix_rides_date', table_name='rides')
    op.drop_index('ix_rides_status', table_name='rides')
    op.drop_index('ix_rides_passenger_id', table_name='rides')
    op.drop_index('ix_rides_driver_id', table_name='rides')
    op.drop_index(op.f('ix_rides_id'), table_name='rides')
    
    # Удаление таблицы
    op.drop_table('rides')
