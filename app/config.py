
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
databricks_token = os.getenv("DATABRICKS_TOKEN")
databricks_server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
databricks_http_path = os.getenv("DATABRICKS_HTTP_PATH")

# Construct the Databricks database URI
DATABRICKS_DATABASE_URI = f"databricks+connector://token:{databricks_token}@{databricks_server_hostname}:443/{databricks_http_path}"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABRICKS_DATABASE_URI,
    connect_args={"http_path": databricks_http_path}
)

# Create a sessionmaker
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a dependency that provides a session
def session():
    db = Session()
    try:
        yield db
    finally:
        db.close()

