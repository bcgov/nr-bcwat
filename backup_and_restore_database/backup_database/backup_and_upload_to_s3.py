import os
import subprocess
import sys
from datetime import date, datetime

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
S3_PATH = f"s3://{os.getenv('BUCKET_NAME')}/{date.today()}-{DB_NAME}.dump"

os.environ["PGPASSWORD"] = DB_PASSWORD

pg_dump_cmd = [
    "pg_dump",
    "-h", DB_HOST,
    "-p", DB_PORT,
    "-U", DB_USER,
    "-d", DB_NAME,
    "-Fc",
    "-v"
]

aws_cp_cmd = ["aws", "s3", "cp", "-", S3_PATH, "--only-show-errors"]

print("Streaming dump into S3 bucket...")

dump_proc = subprocess.Popen(pg_dump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

aws_proc = subprocess.Popen(aws_cp_cmd, stdin=dump_proc.stdout, stderr=subprocess.PIPE, text=True)

dump_proc.stdout.close()

for line in dump_proc.stderr:
    print(f"{datetime.now()} {line.strip()}")

# Wait for both to finish and get final stderr from aws
_, aws_stderr = aws_proc.communicate()

if aws_proc.returncode != 0:
    print("[aws s3 cp] ERROR:")
    print(aws_stderr)
if dump_proc.wait() != 0:
    print("pg_dump exited with a non-zero status.")
