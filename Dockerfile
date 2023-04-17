# Use an official Python runtime as a parent image
FROM python:3.9-slim
FROM fedora:latest
RUN dnf -y update && dnf -y install python3-pip

# Install PostgreSQL development files
RUN dnf install -y postgresql-devel

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./backend .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run manage.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
