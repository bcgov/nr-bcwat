.ONESHELL:

install:
	cd backend; \
	python3 -m venv --copies venv; \
	. venv/bin/activate; \
	pip install -r requirements.txt; \
	cd ../client; \
	npm i;

start-server:
	cd backend; \
	# python3 -m venv venv; \
	# . venv/bin/activate; \
	./startup.sh;

start-client:
	cd client; \
	npm run dev;
