# Backup and Upload to S3

This directory contains a script and a Docker container to restore a PostgreSQL database from a dump in an S3 bucket.

## Files

- **`.env.example`**: Contains example .env file structure for database connection and S3 configuration (for local use only).
- **`restore_database_from_s3.py`**: Python script to restore the database from S3.
- **`Dockerfile`**: Dockerfile to create an image with the necessary files/dependencies to run the restore script.

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
`docker build -t restore-from-s3 `

2. Run the container:
`docker run --rm --env-file .env restore-from-s3`

## How It Works
1. The script uses pg_restore to read a database dump from s3 and rebuild the database.
2. The dump file is streamed directly from S3 using the AWS CLI.
3. Logs from  pg_restore and the AWS CLI are printed to the console for debugging.

## Notes
- Ensure the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY have sufficient permissions to read from the specified S3 bucket.
- Ensure the BACKUP_FILE env var is setup to point at the correct file within the S3 bucket (done to permit modification of restore without rebuilding docker container)
