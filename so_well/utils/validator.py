# so_well/utils/validator.py
import csv
from .logging import logger

def preprocess_csv(input_file, output_file):
    """
    Preprocesses the input CSV file to replace invalid characters and write to a new file.
    Logs any problematic rows.
    """
    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row_num, row in enumerate(reader, start=1):
                try:
                    writer.writerow(row)
                except Exception as e:
                    logger.error(f"Error processing row {row_num}: {row} - {str(e)}")

        logger.info(f"Preprocessed CSV saved to {output_file}")
    except Exception as e:
        logger.error(f"Error in preprocessing CSV: {str(e)}")

if __name__ == "__main__":
    preprocess_csv('data/Registered_Voter_List.csv', 'data/Processed_Voter_List.csv')
