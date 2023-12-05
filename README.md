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
http://localhost:8000/project?search_term=SPAC&app_key=5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy

http://localhost:8000/project?search_term=SPCX653


curl -X GET "https://project-code-api.azurewebsites.us" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

curl -X GET "http://localhost:8000/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

curl -X GET "https://project-code-api.azurewebsites.us/project?search_term=SPAC" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"

curl -X GET "https://project-code-api.azurewebsites.us" -H "X-API-KEY: 5pA0RVLjcZrrEcNc7GhWT3BlbkFJ5rmx4MdvuJ4QQyVeTy"
```