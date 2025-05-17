import argparse
from constants import logger
from all_data_transfer import import_non_scraped_data
from util import recreate_db_schemas, setup_logging

parser = argparse.ArgumentParser()


parser.add_argument(
    "--recreate_db", default=False, type=bool, help="To delete and recreate all the schemas in the table bcwat-dev"
)
parser.add_argument(
    "--non_scraped", default=False, type=bool, help="Would you like to move the stations table over?"
)

args = parser.parse_args()

if __name__=='__main__':
    setup_logging()

    if args.recreate_db:
        recreate_db_schemas()
    if args.non_scraped:
        import_non_scraped_data()