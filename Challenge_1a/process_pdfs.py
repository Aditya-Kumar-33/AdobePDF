import os
import json
import re
from pathlib import Path
from PyPDF2 import PdfReader
from jsonschema import validate, ValidationError

# =============================
# CONFIGURATION SECTION
# =============================
# For Docker container
INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")
SCHEMA_PATH = Path("/app/schema/output_schema.json")
# =============================

def load_schema():
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)

def is_heading(text):
    """
    Determines whether a line of text is likely a heading.
    """
    if not text.strip():
        return False
    return text.isupper() or re.match(r"^\d+(\.\d+)*\s", text)

def extract_title(reader):
    """
    Tries to extract the document title from metadata or first non-empty line.
    """
    if reader.metadata and reader.metadata.title:
        return reader.metadata.title.strip()
    
    first_page = reader.pages[0]
    text = first_page.extract_text() or ""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return "Untitled Document"

def extract_outline(reader):
    """
    Extracts heading structure from the PDF.
    Heuristic used:
        - Short UPPERCASE → H1
        - Medium length → H2
        - Others → H3
    """
    outline = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for line in text.splitlines():
            if is_heading(line):
                clean_line = line.strip()
                length = len(clean_line)
                if length < 20:
                    level = "H1"
                elif length < 40:
                    level = "H2"
                else:
                    level = "H3"
                outline.append({
                    "level": level,
                    "text": clean_line,
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
            print(f"✅ Processed {pdf_file.name} → {output_file.name}")
        
        except ValidationError as ve:
            print(f"❌ Schema validation failed for {pdf_file.name}: {ve}")
        except Exception as e:
            print(f"❌ Failed to process {pdf_file.name}: {e}")

if __name__ == "__main__":
    print("Starting PDF processing...")
    process_pdfs()
    print("Completed PDF processing.")
