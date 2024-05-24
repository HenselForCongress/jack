"""search

Revision ID: c70e2c681e18
Revises: 43f13098f2a3
Create Date: 2024-05-17 14:50:04.154052
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c70e2c681e18'
down_revision = '43f13098f2a3'
branch_labels = None
depends_on = None

def upgrade():
    # Create materialized view for electorate.voter_lookup
    op.execute("""
    CREATE MATERIALIZED VIEW electorate.voter_lookup
    TABLESPACE pg_default
    AS
    SELECT
        v.identification_number,
        v.last_name,
        v.first_name,
        v.middle_name,
        v.status,
        a.house_number,
        a.street_name,
        SUBSTRING(a.zip FROM 1 FOR 5) AS zip,
        a.city,
        to_tsvector('english'::regconfig, (COALESCE(v.first_name, ''::character varying)::text || ' '::text) || COALESCE(v.middle_name, ''::character varying)::text) AS full_name_searchable,
        to_tsvector('english'::regconfig, (
            COALESCE(a.house_number, ''::character varying)::text || ' '::text ||
            COALESCE(a.house_number_suffix, ''::character varying)::text || ' '::text ||
            COALESCE(a.street_name, ''::character varying)::text || ' '::text ||
            COALESCE(a.street_type, ''::character varying)::text || ' '::text ||
            COALESCE(a.direction, ''::character varying)::text || ' '::text ||
            COALESCE(a.post_direction, ''::character varying)::text || ' '::text ||
            COALESCE(a.apt_num, ''::character varying)::text)) AS address_searchable,
        to_tsvector('english'::regconfig, a.city::text) AS city_searchable,
        to_tsvector('simple'::regconfig, SUBSTRING(a.zip FROM 1 FOR 5)::text) AS zip_searchable
    FROM
        electorate.voters v
    JOIN
        electorate.address a ON v.residence_address_id = a.id
    WITH DATA;
    """)

# Create indexes on the materialized view
    op.execute("""
    CREATE INDEX idx_voter_mview_full_name_searchable ON electorate.voter_lookup USING gin (full_name_searchable);
    """)

    op.execute("""
    CREATE INDEX idx_voter_mview_address_searchable ON electorate.voter_lookup USING gin (address_searchable);
    """)

    op.execute("""
    CREATE INDEX idx_voter_mview_city_searchable ON electorate.voter_lookup USING gin (city_searchable);
    """)

    op.execute("""
    CREATE INDEX idx_voter_mview_zip_searchable ON electorate.voter_lookup USING gin (zip_searchable);
    """)

# Refresh the materialized view periodically
    op.execute("""
    REFRESH MATERIALIZED VIEW electorate.voter_lookup;
    """)

def downgrade():
    # Drop indexes on the materialized view
    op.execute("""
    DROP INDEX IF EXISTS idx_voter_mview_full_name_searchable;
    """)

    op.execute("""
    DROP INDEX IF EXISTS idx_voter_mview_address_searchable;
    """)

    op.execute("""
    DROP INDEX IF EXISTS idx_voter_mview_city_searchable;
    """)

    op.execute("""
    DROP INDEX IF EXISTS idx_voter_mview_zip_searchable;
    """)

    # Drop the materialized view
    op.execute("""
    DROP MATERIALIZED VIEW IF EXISTS electorate.voter_lookup;
    """)
