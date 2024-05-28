import logging
from sqlalchemy import Column, Engine, ForeignKey, Integer, MetaData, String, Table, create_engine, delete, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, case, func
from sqlalchemy.orm import Session


from config import DB_PATH

import time

# Import your models
from db import Base, MedicalRecord, MedicalMetadata, Purpose, TempMedicalRecord

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def check_compliance(access_code, aip, pip):
    return (access_code & pip == 0) and (access_code & aip != 0)


def get_schema_info(base):
    schema_info = {}
    for cls in base.__subclasses__():
        # Get the table comment
        table_description = cls.__table__.comment if cls.__table__.comment else ''

        columns_info = {}
        for column in cls.__table__.columns:
            # Get the column comment
            column_description = column.comment if column.comment else ''
            columns_info[column.name] = {
                'type': str(column.type),
                'description': column_description
            }

        relationships_info = {}
        for rel in cls.__mapper__.relationships:
            # Get the relationship comment from the info dictionary
            rel_description = rel.info.get('description', '')
            relationships_info[rel.key] = {
                'description': rel_description
            }

        table_info = {
            'description': table_description,
            'columns': columns_info,
            'relationships': relationships_info
        }
        schema_info[cls.__tablename__] = table_info

    # Format the schema information as a structured string
    structured_string = ""
    for table, info in schema_info.items():
        structured_string += f"Table: {table}\n"
        structured_string += f"Description: {info['description']}\n"
        structured_string += "Columns:\n"
        for column_name, column_info in info['columns'].items():
            structured_string += f"  - {column_name} ({column_info['type']}): {
                column_info['description']}\n"
        structured_string += "Relationships:\n"
        for rel_name, rel_info in info['relationships'].items():
            structured_string += f"  - {rel_name}: {rel_info['description']}\n"
        structured_string += "\n"

    return structured_string


def close_session(session):
    session.close()


def filter_accessible_records(records, access_code):
    def remove_none(array_of_dicts):
        # Remove key-value pairs where the value is None
        filtered_array = [{k: v for k, v in d.items() if v is not None}
                          for d in array_of_dicts]
        return filtered_array
    filtered_records = []

    for record in records:
        metadata = record.metadata_
        masked_record = {}
        for column in record.__table__.columns:
            column_name = column.name
            aip = getattr(metadata, f"{column_name}_aip", None)
            pip = getattr(metadata, f"{column_name}_pip", None)
            attribute = getattr(record, column_name)
            if aip is not None and pip is not None and attribute is not None:
                if check_compliance(access_code, aip, pip):
                    masked_record[column_name] = attribute
                else:
                    masked_record[column_name] = 'Masked'
            else:
                masked_record[column_name] = getattr(record, column_name)
        filtered_records.append(masked_record)
    return remove_none(filtered_records)


def copy_medical_records_to_temp(session, medical_records):
    try:
        # Delete all entries in TempMedicalRecord
        session.query(TempMedicalRecord).delete()

        # Iterate through each medical record and create TempMedicalRecord objects
        for medical_record in medical_records:
            temp_medical_record_data = {}

            # Iterate through each column of TempMedicalRecord
            for column in TempMedicalRecord.__table__.columns:
                # Check if the column exists in the medical record
                if hasattr(medical_record, column.name):
                    # If it exists, add it to the data dictionary
                    temp_medical_record_data[column.name] = getattr(
                        medical_record, column.name)
                else:
                    # If it doesn't exist, assign None to the column in the data dictionary
                    temp_medical_record_data[column.name] = None

            # Create the TempMedicalRecord object with the collected data
            temp_medical_record = TempMedicalRecord(**temp_medical_record_data)

            # Add the TempMedicalRecord object to the session
            session.add(temp_medical_record)

        # Commit the changes
        session.commit()
        print("Medical records copied successfully to TempMedicalRecord.")
    except Exception as e:
        # Rollback the session if an error occurs
        session.rollback()
        print("An error occurred:", str(e))


def analyze_records(records):
    is_same_class = False

    # One record
    if type(records) == MedicalRecord:
        records = [records]
        is_same_class = True
    # Multiple records
    elif type(records) == list and type(records[0]) == MedicalRecord:
        is_same_class = True
    else:
        logging.info(f"Retrieved records are not of parent class. Type: {
                     type(records)}, Record: {records}")

    return is_same_class, records


if __name__ == "__main__":
    start = time.time()

    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:

        # Perform your query
        sql_query = text("""
            SELECT patient_name, reference_id, report_year
            FROM medical_records
            WHERE report_year = 2003
            LIMIT 5;
        """)
        sql_query = text("""
                    SELECT COUNT(*) AS row_count
                    FROM medical_records;""")
        # query = session.query(MedicalRecord.patient_name, MedicalRecord.reference_id, MedicalRecord.report_year).filter_by(
        #    report_year=2003).limit(5).all()
        query = session.execute(sql_query).fetchall()
        print(query)
        """ for r in query:
            print(r.reference_id, r.report_year, r.patient_name) """

        # Insert results into the temporary table
        copy_medical_records_to_temp(session, query)
        results = session.query(TempMedicalRecord).all()
        """ for r in query:
            print(r.reference_id, r.report_year, r.patient_name) """

        filtered = filter_accessible_records(results, 2)
        print(filtered)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        print(f"Execution time: {time.time() - start}")
        close_session(session)
