# Install 

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
