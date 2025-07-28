import os
import json
from pathlib import Path
from PyPDF2 import PdfReader
import re
from jsonschema import validate, ValidationError

# =============================
# CONFIGURATION SECTION
# =============================
# Use these paths for Docker container
INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")
SCHEMA_PATH = "sample_dataset/schema/output_schema.json"  # Schema is still mounted from the project root

# For local testing, use:
# INPUT_DIR = Path("sample_dataset/pdfs")
# OUTPUT_DIR = Path("sample_dataset/outputs")
# SCHEMA_PATH = "sample_dataset/schema/output_schema.json"
# =============================

def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

def is_heading(text):
    if not text.strip():
        return False
    return text.isupper() or re.match(r"^\d+\. ", text)

def extract_title(reader):
    if reader.metadata and reader.metadata.title:
        return reader.metadata.title
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return "Untitled Document"

def extract_outline(reader):
    outline = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line in text.splitlines():
            if is_heading(line):
                if len(line) < 20:
                    level = "H1"
                elif len(line) < 40:
                    level = "H2"
                else:
                    level = "H3"
                outline.append({
                    "level": level,
                    "text": line.strip(),
                    "page": i + 1
                })
    return outline

def process_pdfs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    schema = load_schema()

    for pdf_file in pdf_files:
        try:
            reader = PdfReader(str(pdf_file))
            title = extract_title(reader)
            outline = extract_outline(reader)
            output_data = {
                "title": title,
                "outline": outline
            }
            validate(instance=output_data, schema=schema)
            output_file = OUTPUT_DIR / f"{pdf_file.stem}.json"
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Processed {pdf_file.name} -> {output_file.name}")
        except ValidationError as ve:
            print(f"Schema validation failed for {pdf_file.name}: {ve}")
        except Exception as e:
            print(f"Failed to process {pdf_file.name}: {e}")

if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs()
    print("Completed processing pdfs")