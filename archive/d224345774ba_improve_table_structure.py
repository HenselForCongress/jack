"""Improve table structure

Revision ID: d224345774ba
Revises: dac1c6b2464f
Create Date: 2024-05-16 18:10:25.154311

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import sqlalchemy_utils

# Revision identifiers, used by Alembic
revision = 'd224345774ba'
down_revision = 'dac1c6b2464f'
branch_labels = None
depends_on = None


def table_exists(connection, table_name, schema):
    query = text(f"""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = :table_name
        AND table_schema = :schema
    );
    """)
    result = connection.execute(query, {"table_name": table_name, "schema": schema})
    return result.scalar()

def column_exists(connection, table_name, column_name, schema):
    query = text(f"""
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = :table_name
        AND column_name = :column_name
        AND table_schema = :schema
    );
    """)
    result = connection.execute(query, {"table_name": table_name, "column_name": column_name, "schema": schema})
    return result.scalar()


def upgrade():
    bind = op.get_bind()

    # Users table handling
    if not table_exists(bind, 'users', 'security'):
        op.create_table(
            'users',
            sa.Column('user_id', sa.dialects.postgresql.UUID(), nullable=False, comment='Unique user ID'),
            sa.Column('email', sa.String(length=255), nullable=False, comment="User's email address"),
            sa.Column('is_active', sa.Boolean(), nullable=True, comment='Is the user active?'),
            sa.Column('last_login', sa.DateTime(), nullable=True, comment='Last login time'),
            sa.Column('created_at', sa.DateTime(), nullable=True, comment='Record creation date'),
            sa.Column('updated_at', sa.DateTime(), nullable=True, comment='Record last update date'),
            sa.PrimaryKeyConstraint('user_id'),
            sa.UniqueConstraint('email'),
            schema='security'
        )

    # Address table handling
    if not table_exists(bind, 'address', 'voters'):
        op.create_table(
            'address',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Auto incrementing primary key'),
            sa.Column('house_number', sa.String(length=50), nullable=False, comment='House number of residence'),
            sa.Column('house_number_suffix', sa.String(length=3), nullable=True, comment='House number suffix'),
            sa.Column('street_name', sa.String(length=50), nullable=False, comment='Street name of residence'),
            sa.Column('street_type', sa.String(length=100), nullable=True, comment='Street type (e.g., Ave, Blvd)'),
            sa.Column('direction', sa.String(length=50), nullable=True, comment='Street prefix direction (e.g., N, S)'),
            sa.Column('post_direction', sa.String(length=50), nullable=True, comment='Street suffix direction'),
            sa.Column('apt_num', sa.String(length=50), nullable=True, comment='Apartment number'),
            sa.Column('city', sa.String(length=50), nullable=False, comment='City of residence'),
            sa.Column('state', sa.String(length=50), nullable=False, comment='State of residence'),
            sa.Column('zip', sa.String(length=10), nullable=False, comment='ZIP code of residence'),
            sa.Column('full_address_searchable', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date'),
            sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date'),
            sa.PrimaryKeyConstraint('id'),
            schema='voters'
        )
    else:
        # Add missing columns with alterations if they do not exist
        if not column_exists(bind, 'address', 'created_at', 'voters'):
            with op.batch_alter_table('address', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date', server_default=sa.text('now()')))
        if not column_exists(bind, 'address', 'updated_at', 'voters'):
            with op.batch_alter_table('address', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date', server_default=sa.text('now()')))

    # Locality table handling
    if not table_exists(bind, 'locality', 'voters'):
        op.create_table(
            'locality',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='Auto incrementing primary key'),
            sa.Column('locality_code', sa.String(length=3), nullable=False, comment='Locality FIPS code'),
            sa.Column('locality_name', sa.String(length=255), nullable=False, comment='Name of locality'),
            sa.Column('precinct_code', sa.String(length=255), nullable=True, comment='Code number for precinct'),
            sa.Column('precinct_name', sa.String(length=255), nullable=True, comment='Name of precinct'),
            sa.Column('town_code', sa.String(length=255), nullable=True, comment='Code number for town'),
            sa.Column('town_name', sa.String(length=255), nullable=True, comment='Name of town'),
            sa.Column('town_prec_code', sa.String(length=255), nullable=True, comment='Code number for town precinct'),
            sa.Column('town_prec_name', sa.String(length=255), nullable=True, comment='Name of town precinct'),
            sa.Column('congressional_district', sa.String(length=255), nullable=True, comment='Congressional District'),
            sa.Column('state_senate_district', sa.String(length=255), nullable=True, comment='State Senate District'),
            sa.Column('house_delegates_district', sa.String(length=255), nullable=True, comment='House of Delegates District'),
            sa.Column('super_district_code', sa.String(length=255), nullable=True, comment='Super District code'),
            sa.Column('super_district_name', sa.String(length=255), nullable=True, comment='Super District name'),
            sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date'),
            sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date'),
            sa.PrimaryKeyConstraint('id'),
            schema='voters'
        )
    else:
        # Add missing columns with alterations if they do not exist
        if not column_exists(bind, 'locality', 'created_at', 'voters'):
            with op.batch_alter_table('locality', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date', server_default=sa.text('now()')))
        if not column_exists(bind, 'locality', 'updated_at', 'voters'):
            with op.batch_alter_table('locality', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date', server_default=sa.text('now()')))

    # Voters table handling
    if not table_exists(bind, 'voters', 'voters'):
        op.create_table(
            'voters',
            sa.Column('identification_number', sa.String(length=50), nullable=False, comment="Voter's unique identification number"),
            sa.Column('last_name', sa.String(length=50), nullable=False, comment="Voter's last name"),
            sa.Column('first_name', sa.String(length=50), nullable=False, comment="Voter's first name"),
            sa.Column('middle_name', sa.String(length=50), nullable=True, comment="Voter's middle name"),
            sa.Column('suffix', sa.String(length=50), nullable=True, comment="Voter's name suffix"),
            sa.Column('gender', sa.String(length=1), nullable=True, comment="Voter's gender"),
            sa.Column('dob', sa.Date(), nullable=True, comment="Voter's date of birth"),
            sa.Column('registration_date', sa.Date(), nullable=True, comment="Voter's registration date"),
            sa.Column('effective_date', sa.Date(), nullable=True, comment="Voter's effective date for the precinct"),
            sa.Column('status', sa.String(length=255), nullable=True, comment="Voter's registration status"),
            sa.Column('residence_address_id', sa.Integer(), nullable=False, comment='Foreign key to residence address'),
            sa.Column('mailing_address_id', sa.Integer(), nullable=True, comment='Foreign key to mailing address'),
            sa.Column('locality_id', sa.Integer(), nullable=False, comment='Foreign key to locality'),
            sa.Column('full_name_searchable', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date'),
            sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date'),
            sa.ForeignKeyConstraint(['locality_id'], ['voters.locality.id'], ),
            sa.ForeignKeyConstraint(['mailing_address_id'], ['voters.address.id'], ),
            sa.ForeignKeyConstraint(['residence_address_id'], ['voters.address.id'], ),
            sa.PrimaryKeyConstraint('identification_number'),
            schema='voters'
        )
        with op.batch_alter_table('voters', schema='voters') as batch_op:
            batch_op.create_index(batch_op.f('ix_voters_voters_first_name'), ['first_name'], unique=False)
            batch_op.create_index(batch_op.f('ix_voters_voters_last_name'), ['last_name'], unique=False)
    else:
        # Add missing columns with alterations if they do not exist
        if not column_exists(bind, 'voters', 'created_at', 'voters'):
            with op.batch_alter_table('voters', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, comment='Record creation date', server_default=sa.text('now()')))
        if not column_exists(bind, 'voters', 'updated_at', 'voters'):
            with op.batch_alter_table('voters', schema='voters') as batch_op:
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, comment='Record last update date', server_default=sa.text('now()')))

    # List of table names that need the trigger, adjust as necessary
    tables_with_updated_at = [
        'address', 'locality', 'voters'
    ]

    # Schema names for corresponding tables, adjust as necessary
    schema_names = [
        'voters', 'voters', 'voters'
    ]

    # Creating a trigger for each table
    for table, schema in zip(tables_with_updated_at, schema_names):
        op.execute(f"""
        CREATE TRIGGER update_{table}_updated_at BEFORE UPDATE ON {schema}.{table}
        FOR EACH ROW EXECUTE FUNCTION meta.update_updated_at_column();
        """)


def downgrade():
    # List of table names that need the trigger, adjust as necessary
    tables_with_updated_at = [
        'address', 'locality', 'voters'
    ]

    # Schema names for corresponding tables, adjust as necessary
    schema_names = [
        'voters', 'voters', 'voters'
    ]

    # Dropping each trigger
    for table, schema in zip(tables_with_updated_at, schema_names):
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {schema}.{table};")

    with op.batch_alter_table('voters', schema='voters') as batch_op:
        batch_op.drop_index(batch_op.f('ix_voters_voters_last_name'))
        batch_op.drop_index(batch_op.f('ix_voters_voters_first_name'))

    op.drop_table('voters', schema='voters')
    op.drop_table('locality', schema='voters')
    with op.batch_alter_table('address', schema='voters') as batch_op:
        batch_op.drop_index(batch_op.f('ix_voters_address_zip'))
        batch_op.drop_index(batch_op.f('ix_voters_address_street_name'))
        batch_op.drop_index(batch_op.f('ix_voters_address_city'))

    op.drop_table('address', schema='voters')
    op.drop_table('users', schema='security')
