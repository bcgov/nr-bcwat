# Use Playwright's official Python image which includes all browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.50.0-noble

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

RUN playwright install chromium
RUN playwright install --with-deps chromium

# copy project
COPY . /usr/src/app/

EXPOSE 8888

CMD ["python3", "-u", "-m", "gunicorn", "-w", "2", "--timeout", "120", "--bind", "0.0.0.0:8888", "--access-logfile", "-", "wsgi:app"]