# Backup and Upload to S3

This directory contains a script and Docker setup to back up a PostgreSQL database and upload the backup to an S3 bucket.

## Files

- **`.env.example`**: Contains example .env file structure for database connection and S3 configuration (for local use only).
- **`backup_and_upload_to_s3.py`**: Python script to back up the database and upload the dump to S3.
- **`Dockerfile`**: Dockerfile to create an image with the necessary files/dependencies to run the backup script.

## Prerequisites

- Ensure you have access to the PostgreSQL database and S3 bucket.
- Create a `.env` file with the correct values for the following values based off of `.env.example`:
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `BUCKET_NAME`

## Usage

### Running with Docker
1. Build the Docker image:
`docker build -t backup-to-s3 `

2. Run the container:
`docker run --env-file .env backup-to-s3`

## How It Works
1. The script uses pg_dump to create a PostgreSQL database dump in a custom binary format (-Fc).
2. The dump is streamed directly to S3 using the AWS CLI.
3. Logs from pg_dump and the AWS CLI are printed to the console for debugging.
    - pg_dump logs are live and the AWS CLI logs are printed at the end (errors only)
## Notes
- Ensure the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have sufficient permissions to upload to the specified S3 bucket.
- The backup file is named using the format: <date>-<DB_NAME>.dump in the bucket for restoration purposes.
