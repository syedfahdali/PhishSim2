# Use Python 3.12.2 as the base image
FROM python:3.12.2-slim

# Install system dependencies required for mysqlclient and other Python packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt into the container
COPY ./requirements.txt /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

# Install the required Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the application files into the container
COPY . /app/

# Expose port 8000 to allow communication to/from the container
EXPOSE 8000

# Command to run the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]