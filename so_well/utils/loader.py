# so_well/utils/loader.py
import csv
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from so_well.models import Address, Locality, Voter, db
from .logging import logger
from .validator import preprocess_csv  # Import the validator module

BATCH_SIZE = 1000  # Adjust batch size to optimize performance

def insert_address(row, session):
    existing_address = session.query(Address).filter_by(
        house_number=row['HOUSE_NUMBER'],
        house_number_suffix=row['HOUSENUMBERSUFFIX'],
        street_name=row['STREET_NAME'],
        street_type=row['STREETTYPECODENAME'],
        direction=row['DIRECTION'],
        post_direction=row['POST_DIRECTION'],
        apt_num=row['APT_NUM'],
        city=row['CITY'],
        state=row['STATE'],
        zip=row['ZIP']
    ).first()

    if existing_address:
        return existing_address.id

    try:
        address = Address(
            house_number=row['HOUSE_NUMBER'],
            house_number_suffix=row['HOUSENUMBERSUFFIX'],
            street_name=row['STREET_NAME'],
            street_type=row['STREETTYPECODENAME'],
            direction=row['DIRECTION'],
            post_direction=row['POST_DIRECTION'],
            apt_num=row['APT_NUM'],
            city=row['CITY'],
            state=row['STATE'],
            zip=row['ZIP'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(address)
        session.flush()
        return address.id
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting address: {str(e)}")
        return None

def insert_locality(row, session):
    existing_locality = session.query(Locality).filter_by(
        locality_code=row['LOCALITY_CODE'],
        locality_name=row['LOCALITYNAME'],
        precinct_code=row['PRECINCT_CODE_VALUE'],
        precinct_name=row['PRECINCTNAME']
    ).first()

    if existing_locality:
        return existing_locality.id

    try:
        locality = Locality(
            locality_code=row['LOCALITY_CODE'],
            locality_name=row['LOCALITYNAME'],
            precinct_code=row['PRECINCT_CODE_VALUE'],
            precinct_name=row['PRECINCTNAME'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(locality)
        session.flush()
        return locality.id
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting locality: {str(e)}")
        return None

def insert_voter(row, residence_address_id, mailing_address_id, locality_id, session):
    existing_voter = session.query(Voter).filter_by(
        identification_number=row['IDENTIFICATION_NUMBER']
    ).first()

    if existing_voter:
        return

    try:
        voter = Voter(
            identification_number=row['IDENTIFICATION_NUMBER'],
            last_name=row['LAST_NAME'],
            first_name=row['FIRST_NAME'],
            middle_name=row['MIDDLE_NAME'],
            suffix=row['SUFFIX'],
            gender=row['GENDER'],
            dob=datetime.strptime(row['DOB'], '%m/%d/%Y') if row['DOB'] else None,
            registration_date=datetime.strptime(row['REGISTRATION_DATE'], '%m/%d/%Y') if row['REGISTRATION_DATE'] else None,
            effective_date=datetime.strptime(row['EFFECTIVE_DATE'], '%m/%d/%Y') if row['EFFECTIVE_DATE'] else None,
            status=row['STATUS'],
            residence_address_id=residence_address_id,
            mailing_address_id=mailing_address_id,
            locality_id=locality_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(voter)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error inserting voter: {str(e)}")

def load_data(file_path='data/Registered_Voter_List.csv'):
    logger.info("Loading data...")

    # Preprocess the CSV file
    processed_file_path = 'data/Processed_Voter_List.csv'
    preprocess_csv(file_path, processed_file_path)

    inserted_addresses = 0
    inserted_localities = 0
    inserted_voters = 0
    skipped_addresses = 0
    skipped_localities = 0
    skipped_voters = 0
    errors = 0

    try:
        with open(processed_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # Print column names for debugging
            logger.info(f"CSV Columns: {reader.fieldnames}")

            batch_records = []
            for i, row in enumerate(reader, start=1):
                batch_records.append(row)

                if i % BATCH_SIZE == 0:
                    process_batch(batch_records, inserted_addresses, inserted_localities, inserted_voters, skipped_addresses, skipped_localities, skipped_voters, errors)
                    batch_records = []  # Reset batch

            # Process remaining records
            if batch_records:
                process_batch(batch_records, inserted_addresses, inserted_localities, inserted_voters, skipped_addresses, skipped_localities, skipped_voters, errors)

            logger.info(f"Data loaded successfully - Inserted Addresses: {inserted_addresses}, Inserted Localities: {inserted_localities}, Inserted Voters: {inserted_voters}")
            logger.info(f"Skipped Addresses: {skipped_addresses}, Skipped Localities: {skipped_localities}, Skipped Voters: {skipped_voters}")
            if errors > 0:
                logger.error(f"Total Errors: {errors}")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")

def process_batch(batch_records, inserted_addresses, inserted_localities, inserted_voters, skipped_addresses, skipped_localities, skipped_voters, errors):
    session = db.session()
    try:
        for row in batch_records:
            try:
                residence_address_id = insert_address(row, session)
                if residence_address_id:
                    inserted_addresses += 1
                else:
                    skipped_addresses += 1

                mailing_address_id = insert_address(row, session) if row['MAILING_ADDRESS_LINE_1'] else None

                locality_id = insert_locality(row, session)
                if locality_id:
                    inserted_localities += 1
                else:
                    skipped_localities += 1

                if residence_address_id and locality_id:
                    insert_voter(row, residence_address_id, mailing_address_id, locality_id, session)
                    inserted_voters += 1
                else:
                    skipped_voters += 1
            except KeyError as e:
                errors += 1
                logger.error(f"Error processing row {row}: Missing column {e}")

        session.commit()
        logger.info(f"Processed batch - Inserted Addresses: {inserted_addresses}, Inserted Localities: {inserted_localities}, Inserted Voters: {inserted_voters}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing batch: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    load_data()
