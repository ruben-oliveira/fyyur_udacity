import os
SECRET_KEY = os.urandom(32)

#DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
#DB_USER = os.getenv('DB_USER', 'postgres')
#DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
#DB_NAME = os.getenv('DB_NAME', 'fyyur_db')

#DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)


# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://Oliver:fyyurpass@localhost:5432/fyyur_db'
SQLALCHEMY_ECHO = True