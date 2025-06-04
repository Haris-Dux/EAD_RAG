
# USE PYTHON IMAGE
FROM python:3.12-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libglib2.0-0 \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


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