import json
import os
from datetime import datetime
from typing import Dict, List, Any


class JSONHandler:
    """Handles JSON input/output operations for the PDF analysis system."""
    
    def __init__(self):
        self.required_input_fields = [
            'challenge_info', 'documents', 'persona', 'job_to_be_done'
        ]
    
    def load_input_json(self, file_path: str) -> Dict[str, Any]:
        """
        Load and validate input JSON file.
        
        Args:
            file_path: Path to the input JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self._validate_input_structure(data)
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {file_path}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading {file_path}: {str(e)}")
    
    def _validate_input_structure(self, data: Dict[str, Any]) -> None:
        """
        Validate that input JSON has required structure.
        
        Args:
            data: Input JSON data
            
        Raises:
            ValueError: If required fields are missing
        """
        for field in self.required_input_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate challenge_info
        challenge_info = data.get('challenge_info', {})
        if 'challenge_id' not in challenge_info:
            raise ValueError("Missing challenge_id in challenge_info")
        
        # Validate documents
        documents = data.get('documents', [])
        if not isinstance(documents, list) or len(documents) == 0:
            raise ValueError("Documents must be a non-empty list")
        
        for doc in documents:
            if not isinstance(doc, dict) or 'filename' not in doc:
                raise ValueError("Each document must have a filename field")
        
        # Validate persona
        persona = data.get('persona', {})
        if 'role' not in persona:
            raise ValueError("Persona must have a role field")
        
        # Validate job_to_be_done
        job_to_be_done = data.get('job_to_be_done', {})
        if 'task' not in job_to_be_done:
            raise ValueError("job_to_be_done must have a task field")
    
    def create_output_structure(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the basic output JSON structure.
        
        Args:
            input_data: Parsed input JSON data
            
        Returns:
            Basic output structure with metadata
        """
        # Extract document filenames
        document_filenames = [doc['filename'] for doc in input_data.get('documents', [])]
        
        # Create metadata
        metadata = {
            "input_documents": document_filenames,
            "persona": input_data.get('persona', {}).get('role', ''),
            "job_to_be_done": input_data.get('job_to_be_done', {}).get('task', ''),
            "processing_timestamp": datetime.now().isoformat()
        }
        
        return {
            "metadata": metadata,
            "extracted_sections": [],
            "subsection_analysis": []
        }
    
    def add_extracted_section(self, output_data: Dict[str, Any], 
                            document: str, section_title: str, 
                            importance_rank: int, page_number: int) -> None:
        """
        Add an extracted section to the output.
        
        Args:
            output_data: Output JSON data
            document: Source document filename
            section_title: Title of the section
            importance_rank: Rank of importance (1-5)
            page_number: Page number where section was found
        """
        section = {
            "document": document,
            "section_title": section_title,
            "importance_rank": importance_rank,
            "page_number": page_number
        }
        output_data["extracted_sections"].append(section)
    
    def add_subsection_analysis(self, output_data: Dict[str, Any],
                              document: str, refined_text: str, 
                              page_number: int) -> None:
        """
        Add subsection analysis to the output.
        
        Args:
            output_data: Output JSON data
            document: Source document filename
            refined_text: Refined/extracted text content
            page_number: Page number where content was found
        """
        subsection = {
            "document": document,
            "refined_text": refined_text,
            "page_number": page_number
        }
        output_data["subsection_analysis"].append(subsection)
    
    def save_output_json(self, output_data: Dict[str, Any], file_path: str) -> None:
        """
        Save output JSON to file.
        
        Args:
            output_data: Output JSON data
            file_path: Path where to save the output file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, indent=4, ensure_ascii=False)
            
            print(f"Output saved to: {file_path}")
        except Exception as e:
            raise Exception(f"Error saving output to {file_path}: {str(e)}")
    
    def get_collection_info(self, collection_path: str) -> Dict[str, Any]:
        """
        Get information about a collection directory.
        
        Args:
            collection_path: Path to collection directory
            
        Returns:
            Dictionary with collection information
        """
        collection_info = {
            'path': collection_path,
            'name': os.path.basename(collection_path),
            'input_file': None,
            'output_file': None,
            'pdf_count': 0
        }
        
        # Check for input and output files
        input_path = os.path.join(collection_path, 'challenge1b_input.json')
        output_path = os.path.join(collection_path, 'challenge1b_output.json')
        
        if os.path.exists(input_path):
            collection_info['input_file'] = input_path
        
        if os.path.exists(output_path):
            collection_info['output_file'] = output_path
        
        # Count PDF files
        pdf_dir = os.path.join(collection_path, 'PDFs')
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
            collection_info['pdf_count'] = len(pdf_files)
        
        return collection_info 