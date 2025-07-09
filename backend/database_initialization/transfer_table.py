import argparse
from constants import logger
from all_data_transfer import import_data, create_compressed_files
from util import recreate_db_schemas, setup_logging

parser = argparse.ArgumentParser()


parser.add_argument(
    "--recreate_db", default=False, action='store_true', help="To delete and recreate all the schemas in the table bcwat-dev"
)
parser.add_argument(
    "--import_data", default=False, action='store_true', help="Would you like to move the stations table over?"
)
parser.add_argument(
    "--aws_transfer", default=False, action="store_true", help="Enable this if you want to send the data from the database to the S3 bucket"
)

args = parser.parse_args()

if __name__=='__main__':
    setup_logging()

    if not args.aws_transfer:
        if args.recreate_db:
            recreate_db_schemas()
        if args.import_data:
            import_data()
    else:
        create_compressed_files()
