"""Values & Connections

Revision ID: 692fc097b07f
Revises: 984a4bba6bb3
Create Date: 2024-05-23 17:44:49.985055

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '692fc097b07f'
down_revision = '984a4bba6bb3'
branch_labels = None
depends_on = None


def upgrade():
    # Insert data into sheet_status table
    op.execute("""
    INSERT INTO meta.sheet_status (status, description, "order")
    VALUES
    ('Printed', 'Printed but not yet with signing teams', 1),
    ('Signing', 'In field with teams', 2),
    ('Summarizing', 'Preparing summary sheet', 3),
    ('Shipped', 'In transit to state', 5),
    ('Submission', 'Delivered to state, awaiting confirmation that state has recorded signatures', 6),
    ('Complete', 'State has completed verification and recording process', 7),
    ('Pre-shipment', 'Summary complete, awaiting shipment', 4);
    """)

    # Insert data into signature_status table
    op.execute("""
    INSERT INTO meta.signature_status (status, description, "order")
    VALUES
    ('Recorded', 'Signature entered into database, still need to search', 1),
    ('Validated', 'Confirmed by the state to meet signer criteria', 4),
    ('Matched', 'Match found in internal datasystems', 2),
    ('No Match Found', 'Unable to find a match for this signature', 3);
    """)

    # Create batch_status table in meta schema
    op.create_table('batch_status',
        sa.Column('status', sa.String(length=15), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.UniqueConstraint('status', name='batch_status_unique'),
        schema='meta'
    )

    # Insert data into batch_status table
    op.execute("""
    INSERT INTO meta.batch_status (status, description, "order")
    VALUES
    ('Building', 'Batch created and sheets are being added', 1),
    ('Pre-shipment', 'Batch closed, shipping label printed, awaiting shipment', 2),
    ('Shipped', 'In transit to the state', 3),
    ('Verification', 'Delivered to state and awaiting final verification results', 4),
    ('Complete', 'The state has completed the verification and recording process', 5);
    """)

    # Create triggers for batch_status table
    op.execute("""
    CREATE TRIGGER update_batch_status_updated_at
    BEFORE UPDATE ON meta.batch_status
    FOR EACH ROW
    EXECUTE FUNCTION meta.update_updated_at_column();
    """)

def downgrade():
    # Drop batch_status related objects
    op.execute("DROP TRIGGER IF EXISTS update_batch_status_updated_at ON meta.batch_status;")
    op.drop_table('batch_status', schema='meta')

    # Remove data from signature_status table
    op.execute("""
    DELETE FROM meta.signature_status
    WHERE status IN ('Recorded', 'Validated', 'Matched', 'No Match Found');
    """)

    # Remove data from sheet_status table
    op.execute("""
    DELETE FROM meta.sheet_status
    WHERE status IN ('Printed', 'Signing', 'Summarizing', 'Shipped', 'Submission', 'Complete', 'Pre-shipment');
    """)

