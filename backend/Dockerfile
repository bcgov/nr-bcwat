# pull official base image
FROM python:3.12.10-bookworm

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/

EXPOSE 8000

CMD ["python3", "-u", "-m", "gunicorn", "-w", "4", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--timeout", "90", "wsgi:app"]
