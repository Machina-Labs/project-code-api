from fastapi import FastAPI, Depends, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, Column, Date, DateTime, Float, or_, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel

from random import randrange

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

app = FastAPI()

Base = declarative_base(bind=engine)

# Entity Project
class Project(Base):
    __tablename__ = "sf_opportunities"
    __table_args__ = {'schema': 'etl'}

    sf_opp_index = Column(BigInteger, primary_key=True)  # Assuming 'id' is your unique identifier
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

# Updated Request Body
class ProjectRequest(BaseModel):
    search_term: str = Query(..., max_length=100)

@app.get("/")
def root():
    return {"message": "Hello Lakehouse"}

"""
# Example calls. 
http://localhost:8000/project?search_term=SPAC
http://localhost:8000/project?search_term=SPCX653
"""
@app.get("/project")
def get_project(
    search_term: str = Query(None, max_length=100),
    db: Session = Depends(session),
):
    if search_term:
        upper_search_term = search_term.upper()
        result_set = db.query(Project).filter(
            or_(
                Project.account_name.ilike(f"%{upper_search_term}%"), 
                Project.project_code == upper_search_term
            )
        ).order_by(desc(Project.opp_created_date)).all()
    else:
        result_set = db.query(Project).order_by(desc(Project.opp_created_date)).all()

    response_body = jsonable_encoder(result_set)
    return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


############### Example #################################
## docs of example: https://betterprogramming.pub/build-a-fastapi-on-the-lakehouse-94e4052cc3c9
# """
# Base = declarative_base(bind=engine)

# # Entity User
# class Users(Base):
#     __tablename__ = "users"
#     # __table_args__ = {"autoload": True}
#     id = Column(Integer, primary_key=True, nullable=False)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     address = Column(String, nullable=True)
#     email = Column(String, nullable=True)
#     ip_address = Column(String, nullable=True)


# # Request Body
# class UsersRequest(BaseModel):
#     first_name: str = Query(..., max_length=50)
#     last_name: str = Query(..., max_length=50)


# @app.get("/")
# def root():
#     return {"message": "Hello Lakehouse"}


# @app.get("/user")
# def get_user(
#     id: int = None,
#     first_name: str = Query(None, max_length=50),
#     db: Session = Depends(session),
# ):
#     if id is not None:
#         result_set = db.query(Users).filter(Users.id == id).all()
#     elif first_name is not None:
#         result_set = db.query(Users).filter(Users.first_name == first_name).all()
#     else:
#         result_set = db.query(Users).all()
#     response_body = jsonable_encoder(result_set)
#     return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


# @app.post("/user")
# def create_user(request: UsersRequest, db: Session = Depends(session)):
#     user = Users(
#         id=randrange(1_000_000, 10_000_000),
#         first_name=request.first_name,
#         last_name=request.last_name,
#     )
#     db.add(user)
#     db.commit()
#     response_body = jsonable_encoder({"user_id": user.id})
#     return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


# @app.put("/user/{id}")
# def update_user(id: int, request: UsersRequest, db: Session = Depends(session)):
#     user = db.query(Users).filter(Users.id == id).first()
#     if user is None:
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)
#     user.first_name = request.first_name
#     user.last_name = request.last_name
#     db.commit()
#     response_body = jsonable_encoder({"user_id": user.id})
#     return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)


# @app.delete("/user/{id}")
# def delete_user(id: int, db: Session = Depends(session)):
#     db.query(Users).filter(Users.id == id).delete()
#     db.commit()
#     response_body = jsonable_encoder({"user_id": id, "msg": "record deleted"})
#     return JSONResponse(status_code=status.HTTP_200_OK, content=response_body)

# """
