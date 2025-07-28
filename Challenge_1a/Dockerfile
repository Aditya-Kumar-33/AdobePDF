FROM --platform=linux/amd64 python:3.10

WORKDIR /app

# Copy the processing script
COPY process_pdfs.py .
# Copy the schema file into the image
COPY sample_dataset/schema/output_schema.json sample_dataset/schema/output_schema.json

# Install required dependencies
RUN pip install PyPDF2 jsonschema

# Run the script
CMD ["python", "process_pdfs.py"] 