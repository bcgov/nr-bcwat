import argparse
from constants import logger
from all_data_transfer import (
    import_data,
    create_compressed_files,
    import_from_s3
)
from util import (
    recreate_db_schemas,
    setup_logging,
    check_temp_dir_exists,
    clean_aws_s3_bucket
)
parser = argparse.ArgumentParser()


parser.add_argument(
    "--local_import", default=False, action='store_true', help="To delete and recreate all the schemas in the table bcwat-dev"
)
parser.add_argument(
    "--aws_upload", default=False, action="store_true", help="Enable this if you want to send the data from the database to the S3 bucket"
)
parser.add_argument(
    "--aws_import", default=False, action='store_true', help="Enable this if you want to import data from the S3 bucket"
)
parser.add_argument(
    "--aws_cleanup", default=False, action="store_true", help="Use this to delete everything in the S3 Bucket currently."
)

args = parser.parse_args()

if __name__=='__main__':
    setup_logging()

    if args.local_import:
        recreate_db_schemas()
        import_data()
    if args.aws_upload:
        check_temp_dir_exists()
        create_compressed_files()
    if args.aws_import:
        check_temp_dir_exists()
        recreate_db_schemas()
        import_from_s3()

    if args.aws_cleanup:
        clean_aws_s3_bucket()
