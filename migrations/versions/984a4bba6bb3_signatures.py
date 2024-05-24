"""signatures

Revision ID: 984a4bba6bb3
Revises: c70e2c681e18
Create Date: 2024-05-17 22:29:34.135529

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '984a4bba6bb3'
down_revision = 'c70e2c681e18'
branch_labels = None
depends_on = None


def upgrade():
    # Create schema for signatures
    op.execute("CREATE SCHEMA IF NOT EXISTS signatures;")



    # Create circulators table
    op.create_table('circulators',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('address_1', sa.String(length=255), nullable=False),
        sa.Column('address_2', sa.String(length=255)),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('zip', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='signatures'
    )

    # Create notaries table
    op.create_table('notaries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('registration_number', sa.String(length=255), nullable=False),
        sa.Column('commission_expiration', sa.Date(), nullable=False),
        sa.Column('commission_state', sa.String(length=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='signatures'
    )

    # Create batches table
    op.create_table('batches',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date_shipped', sa.Date(), nullable=False),
        sa.Column('carrier', sa.String(length=255), nullable=False),
        sa.Column('tracking_number', sa.String(length=255), nullable=False),
        sa.Column('ship_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=255), nullable=False),
        sa.Column('arrival_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        schema='signatures'
    )

    # Create sheets table
    op.create_table('sheets',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('collector_id', sa.Integer(), nullable=False),
        sa.Column('notary_id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['collector_id'], ['signatures.circulators.id']),
        sa.ForeignKeyConstraint(['notary_id'], ['signatures.notaries.id']),
        sa.ForeignKeyConstraint(['submission_id'], ['signatures.batches.id']),
        schema='signatures'
    )

    # Create sheet_status table in meta schema
    op.create_table('sheet_status',
        sa.Column('status', sa.String(length=15), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.UniqueConstraint('status', name='sheet_status_unique'),
        schema='meta'
    )

    # Create signature_status table in meta schema
    op.create_table('signature_status',
        sa.Column('status', sa.String(length=15), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.UniqueConstraint('status', name='signature_status_unique'),
        schema='meta'
    )

    # Create collected table in signatures schema with foreign key constraints
    op.create_table('collected',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('sheet_id', sa.Integer(), nullable=False),
        sa.Column('row_id', sa.Integer(), nullable=False),
        sa.Column('voter_id', sa.String(length=50), nullable=True),
        sa.Column('first_name', sa.String(length=50), nullable=True),
        sa.Column('last_name', sa.String(length=50), nullable=True),
        sa.Column('full_street_address', sa.Text(), nullable=True),
        sa.Column('apt', sa.String(length=50), nullable=True),
        sa.Column('city', sa.String(length=50), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip', sa.String(length=5), nullable=True),
        sa.Column('last_4', sa.String(length=4), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('date_collected', sa.Date(), nullable=False, server_default=sa.func.current_date()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint('row_id >= 1 AND row_id <= 12', name='collected_row_number_check'),
        sa.ForeignKeyConstraint(['sheet_id'], ['signatures.sheets.id'], name='collected_sheets_fk'),
        sa.ForeignKeyConstraint(['status'], ['meta.signature_status.status'], name='collected_signature_status_fk'),
        sa.ForeignKeyConstraint(['voter_id'], ['electorate.voters.identification_number'], name='collected_voters_fk'),
        schema='signatures'
    )

    # Create triggers
    op.execute("""
    CREATE TRIGGER update_circulators_updated_at
    BEFORE UPDATE ON signatures.circulators
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_notaries_updated_at
    BEFORE UPDATE ON signatures.notaries
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_batches_updated_at
    BEFORE UPDATE ON signatures.batches
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_sheet_status_updated_at
    BEFORE UPDATE ON meta.sheet_status
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_signature_status_updated_at
    BEFORE UPDATE ON meta.signature_status
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

    op.execute("""
    CREATE TRIGGER update_collected_updated_at
    BEFORE UPDATE ON signatures.collected
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)


def downgrade():
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_circulators_updated_at ON signatures.circulators;")
    op.execute("DROP TRIGGER IF EXISTS update_notaries_updated_at ON signatures.notaries;")
    op.execute("DROP TRIGGER IF EXISTS update_batches_updated_at ON signatures.batches;")
    op.execute("DROP TRIGGER IF EXISTS update_sheet_status_updated_at ON meta.sheet_status;")
    op.execute("DROP TRIGGER IF EXISTS update_signature_status_updated_at ON meta.signature_status;")
    op.execute("DROP TRIGGER IF EXISTS update_collected_updated_at ON signatures.collected;")

    # Drop tables
    op.drop_table('collected', schema='signatures')
    op.drop_table('signature_status', schema='meta')
    op.drop_table('sheet_status', schema='meta')
    op.drop_table('batches', schema='signatures')
    op.drop_table('notaries', schema='signatures')
    op.drop_table('circulators', schema='signatures')
    op.drop_table('sheets', schema='signatures')
    op.execute("DROP SCHEMA IF EXISTS signatures CASCADE;")
