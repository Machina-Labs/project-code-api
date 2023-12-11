FROM python:3.10.6-slim
 
EXPOSE 8000

WORKDIR /app

# Pin Python 3.9 to prevent its installation
RUN echo 'Package: python3.9*' > /etc/apt/preferences.d/no-python3.9 \
    && echo 'Pin: version *' >> /etc/apt/preferences.d/no-python3.9 \
    && echo 'Pin-Priority: -1' >> /etc/apt/preferences.d/no-python3.9

# Install only necessary packages
RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install poetry==1.3.1

COPY . .
RUN poetry install --only main --no-interaction --no-ansi

# Command to run the application using Uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]