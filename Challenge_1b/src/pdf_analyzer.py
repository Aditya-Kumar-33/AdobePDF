import os
from typing import Dict, List, Any, Tuple
from .pdf_processor import PDFProcessor
from .json_handler import JSONHandler
from .persona_analyzer import PersonaAnalyzer, PersonaType
from .text_refiner import TextRefiner


class PDFAnalyzer:
    """Main PDF analysis engine that orchestrates the entire analysis process."""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.json_handler = JSONHandler()
        self.persona_analyzer = PersonaAnalyzer()
        self.text_refiner = TextRefiner()
    
    def analyze_collection(self, collection_path: str) -> Dict[str, Any]:
        """
        Analyze a complete collection of PDFs.
        
        Args:
            collection_path: Path to the collection directory
            
        Returns:
            Analysis results in the required JSON format
        """
        print(f"Analyzing collection: {collection_path}")
        
        # Load input configuration
        input_file = os.path.join(collection_path, 'challenge1b_input.json')
        input_data = self.json_handler.load_input_json(input_file)
        
        # Process PDFs in the collection
        pdf_data = self.pdf_processor.process_pdf_collection(collection_path)
        
        # Determine persona type
        persona_role = input_data.get('persona', {}).get('role', '')
        persona_type = self.persona_analyzer.get_persona_type(persona_role)
        
        # Get task description
        task_description = input_data.get('job_to_be_done', {}).get('task', '')
        
        # Create output structure
        output_data = self.json_handler.create_output_structure(input_data)
        
        # Analyze and rank sections
        all_sections = []
        for filename, doc_data in pdf_data.items():
            sections = doc_data.get('sections', [])
            for section in sections:
                section['document'] = filename
                all_sections.append(section)
        
        # Rank sections by importance
        ranked_sections = self.persona_analyzer.rank_sections_by_importance(
            all_sections, persona_type, task_description
        )
        
        # Add top sections to output
        for i, (section, score) in enumerate(ranked_sections[:5]):
            self.json_handler.add_extracted_section(
                output_data,
                section['document'],
                section['title'],
                i + 1,  # importance_rank (1-5)
                section['page_number']
            )
        
        # Generate subsection analysis
        self._generate_subsection_analysis(
            output_data, pdf_data, persona_type, task_description
        )
        
        return output_data
    
    def _generate_subsection_analysis(self, output_data: Dict[str, Any], 
                                    pdf_data: Dict[str, Dict], 
                                    persona_type: PersonaType,
                                    task_description: str) -> None:
        """
        Generate subsection analysis for the output.
        
        Args:
            output_data: Output JSON data
            pdf_data: Processed PDF data
            persona_type: Type of persona
            task_description: Description of the task
        """
        content_type = self._get_content_type(persona_type)
        
        # Collect all pages from all documents
        all_pages = []
        for filename, doc_data in pdf_data.items():
            pages = doc_data.get('pages', {})
            for page_num, text in pages.items():
                all_pages.append({
                    'document': filename,
                    'page_number': page_num,
                    'text': text
                })
        
        # Rank pages by relevance
        ranked_pages = []
        for page_info in all_pages:
            relevance_score, _ = self.persona_analyzer.analyze_content_relevance(
                page_info['text'], persona_type, task_description
            )
            ranked_pages.append((page_info, relevance_score))
        
        # Sort by relevance score
        ranked_pages.sort(key=lambda x: x[1], reverse=True)
        
        # Add top relevant pages to subsection analysis
        for page_info, score in ranked_pages[:5]:
            refined_text = self.text_refiner.create_actionable_summary(
                page_info['text'], content_type
            )
            
            if refined_text and len(refined_text) > 50:
                self.json_handler.add_subsection_analysis(
                    output_data,
                    page_info['document'],
                    refined_text,
                    page_info['page_number']
                )
    
    def _get_content_type(self, persona_type: PersonaType) -> str:
        """Get content type based on persona type."""
        content_type_map = {
            PersonaType.TRAVEL_PLANNER: 'travel',
            PersonaType.HR_PROFESSIONAL: 'hr',
            PersonaType.FOOD_CONTRACTOR: 'food'
        }
        return content_type_map.get(persona_type, 'general')
    
    def process_all_collections(self, base_path: str = '.') -> None:
        """
        Process all collections in the base directory.
        
        Args:
            base_path: Base directory containing collections
        """
        collections = ['Collection 1', 'Collection 2', 'Collection 3']
        
        for collection_name in collections:
            collection_path = os.path.join(base_path, collection_name)
            
            if os.path.exists(collection_path):
                try:
                    print(f"\nProcessing {collection_name}...")
                    output_data = self.analyze_collection(collection_path)
                    
                    # Save output
                    output_file = os.path.join(collection_path, 'challenge1b_output.json')
                    self.json_handler.save_output_json(output_data, output_file)
                    
                    print(f"Successfully processed {collection_name}")
                    
                except Exception as e:
                    print(f"Error processing {collection_name}: {str(e)}")
            else:
                print(f"Collection directory not found: {collection_path}")
    
    def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """
        Validate that output data meets requirements.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['metadata', 'extracted_sections', 'subsection_analysis']
        
        # Check required fields exist
        for field in required_fields:
            if field not in output_data:
                print(f"Missing required field: {field}")
                return False
        
        # Check metadata structure
        metadata = output_data.get('metadata', {})
        required_metadata = ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp']
        
        for field in required_metadata:
            if field not in metadata:
                print(f"Missing required metadata field: {field}")
                return False
        
        # Check extracted_sections structure
        extracted_sections = output_data.get('extracted_sections', [])
        if not isinstance(extracted_sections, list):
            print("extracted_sections must be a list")
            return False
        
        for section in extracted_sections:
            required_section_fields = ['document', 'section_title', 'importance_rank', 'page_number']
            for field in required_section_fields:
                if field not in section:
                    print(f"Missing required field in extracted_sections: {field}")
                    return False
        
        # Check subsection_analysis structure
        subsection_analysis = output_data.get('subsection_analysis', [])
        if not isinstance(subsection_analysis, list):
            print("subsection_analysis must be a list")
            return False
        
        for subsection in subsection_analysis:
            required_subsection_fields = ['document', 'refined_text', 'page_number']
            for field in required_subsection_fields:
                if field not in subsection:
                    print(f"Missing required field in subsection_analysis: {field}")
                    return False
        
        print("Output validation passed")
        return True
    
    def get_analysis_summary(self, collection_path: str) -> Dict[str, Any]:
        """
        Get a summary of the analysis for a collection.
        
        Args:
            collection_path: Path to the collection directory
            
        Returns:
            Summary of the analysis
        """
        try:
            # Load input data
            input_file = os.path.join(collection_path, 'challenge1b_input.json')
            input_data = self.json_handler.load_input_json(input_file)
            
            # Process PDFs
            pdf_data = self.pdf_processor.process_pdf_collection(collection_path)
            
            # Get persona info
            persona_role = input_data.get('persona', {}).get('role', '')
            persona_type = self.persona_analyzer.get_persona_type(persona_role)
            
            # Count documents and pages
            total_documents = len(pdf_data)
            total_pages = sum(len(doc_data.get('pages', {})) for doc_data in pdf_data.values())
            total_sections = sum(len(doc_data.get('sections', [])) for doc_data in pdf_data.values())
            
            summary = {
                'collection_name': os.path.basename(collection_path),
                'persona': persona_role,
                'task': input_data.get('job_to_be_done', {}).get('task', ''),
                'total_documents': total_documents,
                'total_pages': total_pages,
                'total_sections': total_sections,
                'persona_type': persona_type.value,
                'documents_processed': list(pdf_data.keys())
            }
            
            return summary
            
        except Exception as e:
            return {
                'collection_name': os.path.basename(collection_path),
                'error': str(e)
            } 