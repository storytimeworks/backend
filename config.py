import os

# CSRF settings, come back to this later
CORS_HEADERS = "Content-Type"

# MySQL database credentials, fetched from environment variables
MYSQL_USER = os.environ["RDS_USERNAME"]
MYSQL_PASSWORD = os.environ["RDS_PASSWORD"]
MYSQL_DB = os.environ["RDS_DB_NAME"]
MYSQL_HOST = os.environ["RDS_HOSTNAME"]
MYSQL_DETAILS = (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB)

SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s/%s" % MYSQL_DETAILS
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for signing cookies
SECRET_KEY = os.environ["SECRET_KEY"]
