#!/usr/bin/env bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_RUN_PORT=8888

python3 -m flask --debug run
