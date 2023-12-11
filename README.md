# Install 

- Create a copy of the .env template file with the databricks server and host for the Dashboard Runner resource already filled in.
- Add the databricks token to use
- Create a new python environment with those 4 libraries installed
- Run the uvicorn main code to test the app locally 

```
conda create -n pcode python=3.10.6
conda activate pcode
pip install fastapi
pip install "uvicorn[standard]"
pip install sqlalchemy
pip install sqlalchemy-databricks 
uvicorn app.main:app --reload
curl -X GET 'http://localhost:8000/project?search_term=HPN066'
curl -X GET 'http://localhost:8000/project?search_term=SPAC'
```

# Related links 

- https://github.com/tiangolo/fastapi
- https://betterprogramming.pub/build-a-fastapi-on-the-lakehouse-94e4052cc3c9

# To Do

[ ] Limit search results with pagination, e.g. project?search_term=A&limit=10 
[ ] Add authenentication token  

# Example calls 

```
# Example calls. 
curl -X GET "http://localhost:8000" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"
curl -X GET "http://localhost:8000/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"


curl -X GET "https://project-code-api.azurewebsites.us" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"
curl -X GET "https://project-code-api.azurewebsites.us/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

```

# Session management

FastAPI uses dependency injection to handle database sessions in the main.py file:

    SessionMaker Creation:

    python

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

A Session object is created using SQLAlchemy's sessionmaker function, bound to the database engine. This Session acts as a factory for creating new session objects.

Session Dependency Function:

python

def session():
    db = Session()
    try:
        yield db
    finally:
        db.close()

The session() function is defined as a generator. It creates and yields a new session from the Session factory. After processing the request, the session is closed to free resources.

Using the Session in Endpoint Functions:

python

    @app.get("/project")
    def get_project(..., db: Session = Depends(session)):
        ...

    In the endpoint (e.g., get_project), the session is injected as a dependency using FastAPI's Depends function. For each request to this endpoint, FastAPI calls the session() function to provide a session (db).

    Session Lifecycle:
    FastAPI automatically manages the session lifecycle:
        A new SQLAlchemy session is created when a request comes in.
        This session is used throughout the request to interact with the database.
        After the request is processed, the finally block in the session() function executes, closing the session.

    Exception Handling:
    In the endpoint, exceptions such as DatabaseError that may occur during query execution are handled. Specific database-related exceptions can be caught and managed as needed.

This dependency injection pattern for database sessions in FastAPI ensures each request has its own session, which is properly closed after handling, thereby avoiding resource leaks and maintaining database interaction integrity.