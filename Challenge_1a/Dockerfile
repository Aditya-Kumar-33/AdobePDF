# Use AMD64-compatible Python base image
FROM --platform=linux/amd64 python:3.10

# Set working directory inside container
WORKDIR /app

# Copy the processing script into the container
COPY process_pdfs.py .

# Copy the full schema directory to maintain structure
COPY sample_dataset/schema /app/schema

# Install required dependencies
RUN pip install --no-cache-dir PyPDF2 jsonschema

# Command to run the script when container starts
CMD ["python", "process_pdfs.py"]
