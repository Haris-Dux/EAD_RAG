
# USE PYTHON IMAGE
FROM python:3.12-slim


# SET WOTKIN DIRECTORY
WORKDIR /app


# COPY REQUIREMENTS AND INSTALL DEPENDECIES
COPY requirements.txt .

# INSTALL DEPENDECIES
RUN pip install --no-cache-dir -r requirements.txt

# COPY THE APP CODE
COPY ./app ./app

# RUN FAST API APPLICATION
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]