# Use the official Python image as the base image
FROM python:3.11.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports
EXPOSE 80

# Define the command to run the application
CMD ["python", "src/app.py"]
