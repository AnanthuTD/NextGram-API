FROM mybaseimage
# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./backend .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80 5432
# Define environment variable
ENV NAME World

# Run manage.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
