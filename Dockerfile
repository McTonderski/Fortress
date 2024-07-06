# Use the slim variant of the Python image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory into the container's working directory
COPY . .

# Expose the port your application runs on
EXPOSE 8000

# Define the command to run your application
CMD ["python", "-m", "docker_fortress"]
