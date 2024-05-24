"""Added voter data tables and additional functionality

Revision ID: dac1c6b2464f
Revises:
Create Date: 2024-05-16 17:51:54.353754

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlalchemy_utils
import uuid

# revision identifiers, used by Alembic.
revision = 'dac1c6b2464f'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create Schemas
    schemas = ['meta', 'electorate', 'security', 'signatures']
    for schema in schemas:
        op.execute(f'CREATE SCHEMA IF NOT EXISTS {schema};')


    # Create Update Timestamp Function in Meta Schema
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

    # Drop users table if it exists
    op.execute('DROP TABLE IF EXISTS security.users;')

    # ### Create Users Table in Security Schema ###
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

    # Create tables under electorate schema
    op.create_table('address',
    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False, comment="Auto incrementing primary key"),
    sa.Column('house_number', sa.String(length=50), nullable=False, comment="House number of residence"),
    sa.Column('house_number_suffix', sa.String(length=3), nullable=True, comment="House number suffix"),
    sa.Column('street_name', sa.String(length=50), nullable=False, index=True, comment="Street name of residence"),
    sa.Column('street_type', sa.String(length=100), nullable=True, comment="Street type (e.g., Ave, Blvd)"),
    sa.Column('direction', sa.String(length=50), nullable=True, comment="Street prefix direction (e.g., N, S)"),
    sa.Column('post_direction', sa.String(length=50), nullable=True, comment="Street suffix direction"),
    sa.Column('apt_num', sa.String(length=50), nullable=True, comment="Apartment number"),
    sa.Column('city', sa.String(length=50), nullable=False, index=True, comment="City of residence"),
    sa.Column('state', sa.String(length=50), nullable=False, comment="State of residence"),
    sa.Column('zip', sa.String(length=10), nullable=False, index=True, comment="ZIP code of residence"),
    sa.Column('full_address_searchable', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="Record creation date"),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), server_onupdate=sa.func.now(), comment="Record last update date"),
    schema='electorate'
    )

    op.create_table('locality',
    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False, comment="Auto incrementing primary key"),
    sa.Column('locality_code', sa.String(length=3), nullable=False, comment="Locality FIPS code"),
    sa.Column('locality_name', sa.String(length=255), nullable=False, comment="Name of locality"),
    sa.Column('precinct_code', sa.String(length=255), nullable=True, comment="Code number for precinct"),
    sa.Column('precinct_name', sa.String(length=255), nullable=True, comment="Name of precinct"),
    sa.Column('town_code', sa.String(length=255), nullable=True, comment="Code number for town"),
    sa.Column('town_name', sa.String(length=255), nullable=True, comment="Name of town"),
    sa.Column('town_prec_code', sa.String(length=255), nullable=True, comment="Code number for town precinct"),
    sa.Column('town_prec_name', sa.String(length=255), nullable=True, comment="Name of town precinct"),
    sa.Column('congressional_district', sa.String(length=255), nullable=True, comment="Congressional District"),
    sa.Column('state_senate_district', sa.String(length=255), nullable=True, comment="State Senate District"),
    sa.Column('house_delegates_district', sa.String(length=255), nullable=True, comment="House of Delegates District"),
    sa.Column('super_district_code', sa.String(length=255), nullable=True, comment="Super District code"),
    sa.Column('super_district_name', sa.String(length=255), nullable=True, comment="Super District name"),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="Record creation date"),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), server_onupdate=sa.func.now(), comment="Record last update date"),
    schema='electorate'
    )

    op.create_table('voters',
    sa.Column('identification_number', sa.String(length=50), primary_key=True, nullable=False, comment="Voter's unique identification number"),
    sa.Column('last_name', sa.String(length=50), nullable=False, index=True, comment="Voter's last name"),
    sa.Column('first_name', sa.String(length=50), nullable=False, index=True, comment="Voter's first name"),
    sa.Column('middle_name', sa.String(length=50), nullable=True, comment="Voter's middle name"),
    sa.Column('suffix', sa.String(length=50), nullable=True, comment="Voter's name suffix"),
    sa.Column('gender', sa.String(length=1), nullable=True, comment="Voter's gender"),
    sa.Column('dob', sa.Date(), nullable=True, comment="Voter's date of birth"),
    sa.Column('registration_date', sa.Date(), nullable=True, comment="Voter's registration date"),
    sa.Column('effective_date', sa.Date(), nullable=True, comment="Voter's effective date for the precinct"),
    sa.Column('status', sa.String(length=255), nullable=True, comment="Voter's registration status"),
    sa.Column('residence_address_id', sa.Integer(), sa.ForeignKey('electorate.address.id'), nullable=False, comment="Foreign key to residence address"),
    sa.Column('mailing_address_id', sa.Integer(), sa.ForeignKey('electorate.address.id'), nullable=True, comment="Foreign key to mailing address"),
    sa.Column('locality_id', sa.Integer(), sa.ForeignKey('electorate.locality.id'), nullable=False, comment="Foreign key to locality"),
    sa.Column('full_name_searchable', sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="Record creation date"),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), server_onupdate=sa.func.now(), comment="Record last update date"),
    schema='electorate'
    )

    # Create tables under security schema
    op.create_table('users',
    sa.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()), comment="Unique user ID"),
    sa.Column('email', sa.String(length=255), nullable=False, unique=True, comment="User's email address"),
    sa.Column('is_active', sa.Boolean, default=True, comment="Is the user active?"),
    sa.Column('last_login', sa.DateTime, nullable=True, comment="Last login time"),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), comment="Record creation date"),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), server_onupdate=sa.func.now(), comment="Record last update date"),
    schema='security'
    )

    # Create indexes for address table
    with op.batch_alter_table('address', schema='electorate') as batch_op:
        batch_op.create_index(batch_op.f('ix_electorate_address_city'), ['city'], unique=False)
        batch_op.create_index(batch_op.f('ix_electorate_address_street_name'), ['street_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_electorate_address_zip'), ['zip'], unique=False)

    # Create indexes for voters table
    with op.batch_alter_table('voters', schema='electorate') as batch_op:
        batch_op.create_index(batch_op.f('ix_electorate_voters_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_electorate_voters_last_name'), ['last_name'], unique=False)

    # List of table names that need the trigger
    tables_with_updated_at = [
        'address', 'locality', 'voters'
    ]

    # Schema names for corresponding tables
    schema_names = [
        'electorate', 'electorate', 'electorate'
    ]

    # Creating a trigger for each table
    for table, schema in zip(tables_with_updated_at, schema_names):
        op.execute(f"""
        CREATE TRIGGER update_{table}_updated_at BEFORE UPDATE ON {schema}.{table}
        FOR EACH ROW EXECUTE FUNCTION meta.update_updated_at_column();
        """)


def downgrade():
    # Drop triggers
    tables_with_updated_at = [
        'address', 'locality', 'voters'
    ]

    schema_names = [
        'electorate', 'electorate', 'electorate'
    ]

    for table, schema in zip(tables_with_updated_at, schema_names):
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {schema}.{table};")

    # Drop security schema tables
    op.drop_table('users', schema='security')

    # Drop electorate schema tables
    with op.batch_alter_table('voters', schema='electorate') as batch_op:
        batch_op.drop_index(batch_op.f('ix_electorate_voters_last_name'))
        batch_op.drop_index(batch_op.f('ix_electorate_voters_first_name'))

    op.drop_table('voters', schema='electorate')
    op.drop_table('locality', schema='electorate')

    with op.batch_alter_table('address', schema='electorate') as batch_op:
        batch_op.drop_index(batch_op.f('ix_electorate_address_zip'))
        batch_op.drop_index(batch_op.f('ix_electorate_address_street_name'))
        batch_op.drop_index(batch_op.f('ix_electorate_address_city'))

    op.drop_table('address', schema='electorate')

    # Drop meta schema function and schemas
    op.execute("DROP FUNCTION IF EXISTS meta.update_updated_at_column;")
    for schema in ['meta', 'electorate', 'security', 'signatures']:
        op.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
