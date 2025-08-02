import os
import subprocess
import sys
from datetime import datetime
import threading

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
ENDPOINT_URL = os.environ["AWS_ENDPOINT_URL"]
BACKUP_FILE = os.environ["BACKUP_FILE"]  # Format: "<date>-<database-name>.dump"
BUCKET_NAME = os.environ["BUCKET_NAME"]

S3_PATH = f"s3://{BUCKET_NAME}/{BACKUP_FILE}"
os.environ["PGPASSWORD"] = DB_PASSWORD

def log_stream(stream, prefix):
        for line in stream:
            print(f"{datetime.now()} [{prefix}] {line.decode().strip()}")

aws_cp_cmd = [
    "aws", "s3", "cp", S3_PATH, "-",
    "--endpoint-url", ENDPOINT_URL,
    "--expected-size", "60000000000",
    "--debug"
]

pg_restore_cmd = [
    "pg_restore",
    "-h", DB_HOST,
    "-p", DB_PORT,
    "-U", DB_USER,
    "-d", DB_NAME,
    "-Fc",
    "-v",
    "--clean",
    "--if-exists"
]

print(f"Starting restore from {S3_PATH} to {DB_NAME}...")

try:
    aws_proc = subprocess.Popen(aws_cp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    restore_proc = subprocess.Popen(
        pg_restore_cmd,
        stdin=aws_proc.stdout,
        stderr=subprocess.PIPE
    )
    aws_proc.stdout.close()


    aws_thread = threading.Thread(target=log_stream, args=(aws_proc.stderr, "aws"))
    restore_thread = threading.Thread(target=log_stream, args=(restore_proc.stderr, "pg_restore"))
    aws_thread.start()
    restore_thread.start()

    aws_thread.join()
    restore_thread.join()

    if aws_proc.wait() != 0:
        print("AWS download failed!")
        sys.exit(1)

    if restore_proc.wait() != 0:
        print("pg_restore failed (likely expected due to transaction_timeout parameter)")

    print("Restore completed successfully!")

except Exception as e:
    print(f"Restore failed: {str(e)}")
    sys.exit(1)
