#!/usr/bin/env bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_RUN_PORT=8000

# python3 -m gunicorn -w 4 wsgi:app --log-level debug --debug run
python3 -m flask --debug run
