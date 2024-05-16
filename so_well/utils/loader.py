# so_well/utils/loader.py
import csv
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from so_well.models import Address, Locality, Voter, db
from .logging import logger

def insert_address(row):
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
        db.session.add(address)
        db.session.flush()
        return address.id
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error inserting address: {str(e)}")
        return None

def insert_locality(row):
    try:
        locality = Locality(
            locality_code=row['LOCALITY_CODE'],
            locality_name=row['LOCALITYNAME'],
            precinct_code=row['PRECINCT_CODE_VALUE'],
            precinct_name=row['PRECINCTNAME'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(locality)
        db.session.flush()
        return locality.id
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error inserting locality: {str(e)}")
        return None

def insert_voter(row, residence_address_id, mailing_address_id, locality_id):
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
        db.session.add(voter)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error inserting voter: {str(e)}")

def load_data(file_path='data/Registered_Voter_List.csv'):
    logger.info("Loading data...")
    inserted_addresses = 0
    inserted_localities = 0
    inserted_voters = 0
    errors = 0

    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                residence_address_id = insert_address(row)
                mailing_address_id = insert_address(row) if row['MAILING_ADDRESS_LINE_1'] else None
                locality_id = insert_locality(row)

                if residence_address_id:
                    inserted_addresses += 1
                else:
                    errors += 1

                if locality_id:
                    inserted_localities += 1
                else:
                    errors += 1

                if residence_address_id and locality_id:
                    insert_voter(row, residence_address_id, mailing_address_id, locality_id)
                    inserted_voters += 1
                else:
                    errors += 1

            db.session.commit()
            logger.info(f"Data loaded successfully - Addresses: {inserted_addresses}, Localities: {inserted_localities}, Voters: {inserted_voters}")
            if errors > 0:
                logger.error(f"Total Errors: {errors}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    load_data()
