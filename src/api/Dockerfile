# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# RUN apt update -y
# RUN apt install awscli -y
# RUN aws configure set default.region us-east-1

COPY .. ..

# Use a virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Set default environment variables, including the PORT environment variable
ENV PORT=80

# Run app.py when the container launches
CMD gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app