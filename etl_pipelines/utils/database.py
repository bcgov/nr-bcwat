import psycopg2
import os
from utils.constants import logger, DB_URI
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
port = os.getenv("PGPORT")
user = os.getenv("PGUSER")
password = os.getenv("PGPASS")
database = os.getenv("PGDB")
host = os.getenv("PGHOST")
pgschema_prefix = os.getenv("PGSCHEMA_PREFIX")

class Database:
	def __init__(self):
		self.conn = self.connect()
		self.pool = ThreadedConnectionPool(minconn=1, maxconn=10, host = host, database = database, user = user, password = password, port = port)

	def connect(self):
		"""
		Connect to database and return connection
		"""
		logger.debug("Connecting to PostgreSQL Database using psycopg2...")
		try:
			conn = psycopg2.connect(
					host=host,
					user=user,
					database=database,
					port=port,
					password=password,
					sslmode = 'require'
				)
			return conn
		except psycopg2.OperationalError as e:
			logger.error(f'Could not connect to Database: {e}')

db = Database()
