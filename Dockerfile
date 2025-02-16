# Use the official Python base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir Flask

# Expose Flask app port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
