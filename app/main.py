from fastapi import FastAPI, Depends, Query, status, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    or_,
    desc,
)

from pydantic import BaseModel
from contextlib import contextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
APP_CLIENT_NAME = os.getenv("APP_CLIENT_NAME")
APP_KEY = os.getenv("APP_KEY")

# Construct the Databricks database URI
DATABRICKS_DATABASE_URI = f"databricks+connector://token:{DATABRICKS_TOKEN}@{DATABRICKS_SERVER_HOSTNAME}:443/{DATABRICKS_HTTP_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABRICKS_DATABASE_URI, 
    connect_args={"http_path": DATABRICKS_HTTP_PATH},
    pool_recycle=1800  # Example: 30 minutes
)


app = FastAPI()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# Entity Project
class Project(Base):
    __tablename__ = "sf_opportunities"
    __table_args__ = {"schema": "etl"}

    sf_opp_index = Column(
        BigInteger, primary_key=True
    )  # Assuming 'id' is your unique identifier
    # New fields
    sf_account_index = Column(BigInteger)
    account_name = Column(String)
    account_code = Column(String)
    # sf_opp_index = Column(BigInteger)
    opp_name = Column(String)
    stage_name = Column(String)
    is_closed = Column(Boolean)
    is_won = Column(Boolean)
    po_id = Column(Float)
    po_number = Column(String)
    owner_name = Column(String)
    sf_account_id = Column(String)
    sf_opp_id = Column(String)
    is_deleted_account = Column(Boolean)
    is_deleted_opp = Column(Boolean)
    account_created_date = Column(DateTime)
    opp_created_date = Column(DateTime)
    partition_day = Column(Date)
    project_code = Column(String)

class ProjectRequest(BaseModel):
    search_term: str = Query(..., max_length=100)

"""
# Example calls. 
curl -X GET "http://localhost:8000" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"
curl -X GET "http://localhost:8000/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"
"""

@app.get("/")
def root():
    return {"message": "Hello Lakehouse"}

@app.exception_handler(Exception)
def validation_exception_handler(request, err):
    base_error_message = f"Failed to execute: {request.method}: {request.url}"
    return JSONResponse(status_code=400, content={"message": f"{base_error_message}. Detail: {err}"})

def execute_project_query(db, search_term):
    upper_search_term = search_term.upper() if search_term else None
    query = db.query(Project)

    if upper_search_term:
        query = query.filter(
            or_(
                Project.account_name.ilike(f"%{upper_search_term}%"),
                Project.account_code.ilike(f"%{upper_search_term}%"),
                Project.project_code.ilike(f"%{upper_search_term}%"),
            )
        ).order_by(desc(Project.opp_created_date))
    else:
        query = query.order_by(desc(Project.opp_created_date))

    return query.all()

@app.get("/project")
def get_project(search_term: str = Query(None, max_length=100), x_api_key: str = Header(None)):
    if x_api_key != APP_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    try:
        with session_scope() as db:
            result_set = execute_project_query(db, search_term)
            filtered_result_set = [item for item in result_set if item is not None]
            json_result = jsonable_encoder(filtered_result_set)
            return JSONResponse(content=json_result)
    except DatabaseError as e:
        raise e


# @app.get("/project")
# def get_project(
#     search_term: str = Query(None, max_length=100),
#     x_api_key: str = Header(None),
#     db: Session = Depends(get_db)  # Injecting the session using Depends
# ):
#     if x_api_key != APP_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#         )

#     try:
#         result_set = execute_project_query(db, search_term)
#     except DatabaseError as e:
#         # You can handle specific exceptions here if necessary
#         raise e

#     filtered_result_set = [item for item in result_set if item is not None]
#     json_result = jsonable_encoder(filtered_result_set)

#     return JSONResponse(content=json_result)
