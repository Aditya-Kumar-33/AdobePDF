import pdfplumber
import PyPDF2
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class PDFProcessor:
    """Handles PDF text extraction and document structure analysis."""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF file with page numbers.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with page numbers as keys and text content as values
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = {}
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages[page_num] = text.strip()
                return pages
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {}
    
    def extract_sections_from_text(self, text: str) -> List[Dict]:
        """
        Identify sections in the text based on headers and structure.
        
        Args:
            text: Text content from a page
            
        Returns:
            List of dictionaries containing section information
        """
        sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and self._is_section_header(line):
                # Look for content after the header
                content_start = i + 1
                content_end = len(lines)
                
                # Find the next section header or end of content
                for j in range(i + 1, len(lines)):
                    if self._is_section_header(lines[j].strip()):
                        content_end = j
                        break
                
                # Extract content for this section
                content = '\n'.join(lines[content_start:content_end]).strip()
                
                sections.append({
                    'title': line,
                    'content': content,
                    'start_line': i
                })
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """
        Determine if a line is likely a section header.
        
        Args:
            line: Text line to analyze
            
        Returns:
            True if line appears to be a section header
        """
        if not line:
            return False
        
        # Clean the line
        line = line.strip()
        if len(line) < 3:
            return False
        
        # Check for common header patterns
        header_indicators = [
            line.isupper() and len(line) > 3,  # All caps and meaningful length
            line.startswith('Chapter'),
            line.startswith('Section'),
            line.startswith('Part'),
            len(line.split()) <= 8 and len(line) > 10,  # Short but meaningful titles
            any(keyword in line.lower() for keyword in [
                'guide', 'overview', 'introduction', 'summary',
                'tips', 'tricks', 'instructions', 'steps', 'recipe',
                'ingredients', 'method', 'procedure', 'workflow',
                'feature', 'tool', 'function', 'destination', 'activity'
            ]),
            # Check for title case patterns
            (line[0].isupper() and line.count(' ') >= 1 and 
             all(word[0].isupper() or word.lower() in ['a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for'] 
                 for word in line.split()))
        ]
        
        return any(header_indicators)
    
    def get_document_info(self, pdf_path: str) -> Dict:
        """
        Extract basic document information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with document metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                info = {
                    'num_pages': len(pdf_reader.pages),
                    'filename': os.path.basename(pdf_path),
                    'file_size': os.path.getsize(pdf_path)
                }
                
                # Try to get document metadata
                if pdf_reader.metadata:
                    info['title'] = pdf_reader.metadata.get('/Title', '')
                    info['author'] = pdf_reader.metadata.get('/Author', '')
                
                return info
        except Exception as e:
            print(f"Error getting document info for {pdf_path}: {str(e)}")
            return {'filename': os.path.basename(pdf_path)}
    
    def process_pdf_collection(self, collection_path: str) -> Dict[str, Dict]:
        """
        Process all PDFs in a collection directory.
        
        Args:
            collection_path: Path to collection directory
            
        Returns:
            Dictionary with filename as key and processed content as value
        """
        collection_data = {}
        pdf_dir = os.path.join(collection_path, 'PDFs')
        
        if not os.path.exists(pdf_dir):
            print(f"PDF directory not found: {pdf_dir}")
            return collection_data
        
        for filename in os.listdir(pdf_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_dir, filename)
                pages = self.extract_text_from_pdf(pdf_path)
                doc_info = self.get_document_info(pdf_path)
                
                collection_data[filename] = {
                    'pages': pages,
                    'info': doc_info,
                    'sections': []
                }
                
                # Extract sections from each page
                for page_num, text in pages.items():
                    sections = self.extract_sections_from_text(text)
                    for section in sections:
                        section['page_number'] = page_num
                        collection_data[filename]['sections'].append(section)
        
        return collection_data 