"""Added last_login field to User model

Revision ID: 5151f05a7bb9
Revises:
Create Date: 2024-05-16 17:20:10.140427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5151f05a7bb9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### Create Schemas ###
    schemas = ['meta', 'voters', 'security', 'signatures']
    for schema in schemas:
        op.execute(f'CREATE SCHEMA IF NOT EXISTS {schema};')

    # ### Create Users Table in Security Schema ###
    op.create_table(
        'users',
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email'),
        schema='security'
    )

    # ### Create Update Timestamp Function in Meta Schema ###
    op.execute("""
    CREATE OR REPLACE FUNCTION meta.update_updated_at_column()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$;
    """)

    # ### Create Trigger on Users Table in Security Schema ###
    op.execute("""
    CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON security.users
    FOR EACH ROW EXECUTE FUNCTION meta.update_updated_at_column();
    """)


def downgrade():
    # ### Drop Trigger before Dropping Table or Function ###
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON security.users;")

    # ### Drop Function ###
    op.execute("DROP FUNCTION IF EXISTS meta.update_updated_at_column;")

    # ### Drop Users Table ###
    op.drop_table('users', schema='security')

    # ### Drop Schemas ###
    schemas = ['meta', 'voters', 'security', 'signatures']
    for schema in reversed(schemas):  # reverse order for dependencies
        op.execute(f'DROP SCHEMA IF EXISTS {schema} CASCADE;')
