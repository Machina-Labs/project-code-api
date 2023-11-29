from fastapi import FastAPI, Depends, Query, status, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
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
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DatabaseError

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
    DATABRICKS_DATABASE_URI, connect_args={"http_path": DATABRICKS_HTTP_PATH}
)

# Create a sessionmaker
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

app = FastAPI()
Base = declarative_base(bind=engine)


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


"""
# Example calls. 
http://localhost:8000/project?search_term=SPAC&app_key=5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy

http://localhost:8000/project?search_term=SPCX653


curl -X GET "https://project-code-api.azurewebsites.us" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

curl -X GET "http://localhost:8000/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

curl -X GET "https://project-code-api.azurewebsites.us/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

"""

# Updated Request Body
class ProjectRequest(BaseModel):
    search_term: str = Query(..., max_length=100)


@app.get("/")
def root():
    return {"message": "Hello Lakehouse"}

# # Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

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
def get_project(
    search_term: str = Query(None, max_length=100),
    x_api_key: str = Header(None),
):
    if x_api_key != APP_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    try:
        db = Session()
        result_set = execute_project_query(db, search_term)
    except DatabaseError as e:
        Session.remove()  # Dispose the current session
        if "Invalid SessionHandle" in str(e):
            db = Session()  # Create a new session
            result_set = execute_project_query(db, search_term)
        else:
            raise e
    finally:
        Session.remove()  # Ensure the session is removed after processing

    filtered_result_set = [item for item in result_set if item is not None]
    json_result = jsonable_encoder(filtered_result_set)

    return JSONResponse(content=json_result)


# def execute_project_query(search_term):
#     db = Session()  # Directly acquire a session
#     upper_search_term = search_term.upper() if search_term else None
#     query = db.query(Project)

#     if upper_search_term:
#         query = query.filter(
#             or_(
#                 Project.account_name.ilike(f"%{upper_search_term}%"),
#                 Project.account_code.ilike(f"%{upper_search_term}%"),
#                 Project.project_code.ilike(f"%{upper_search_term}%"),
#             )
#         ).order_by(desc(Project.opp_created_date))
#     else:
#         query = query.order_by(desc(Project.opp_created_date))

#     return query.all()

# @app.get("/project")
# def get_project(
#     search_term: str = Query(None, max_length=100),
#     x_api_key: str = Header(None),
# ):
#     if x_api_key != APP_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#         )

#     try:
#         result_set = execute_project_query(search_term)
#     except DatabaseError as e:
#         if "Invalid SessionHandle" in str(e):
#             Session.remove()  # Dispose the current session
#             result_set = execute_project_query(search_term)
#         else:
#             raise

#     filtered_result_set = [item for item in result_set if item is not None]
#     json_result = jsonable_encoder(filtered_result_set)

#     return JSONResponse(content=json_result)
