import re
from typing import Dict, List, Any, Tuple
from collections import Counter


class TextRefiner:
    """Refines and extracts key information from PDF text content."""
    
    def __init__(self):
        self.max_summary_length = 500
        self.min_content_length = 30
        
        # Common patterns for different content types
        self.patterns = {
            'travel': {
                'destinations': r'\b(?:visit|go to|see|explore)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                'activities': r'\b(?:enjoy|experience|try|discover)\s+([^.!?]+)',
                'locations': r'\b(?:in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                'tips': r'\b(?:tip|advice|recommendation|suggestion)\s*:?\s*([^.!?]+)'
            },
            'hr': {
                'steps': r'\b(?:step|procedure|process)\s+\d+[:\s]*([^.!?]+)',
                'features': r'\b(?:feature|function|tool)\s*:?\s*([^.!?]+)',
                'instructions': r'\b(?:click|select|choose|enable)\s+([^.!?]+)',
                'workflows': r'\b(?:workflow|process|automation)\s*:?\s*([^.!?]+)'
            },
            'food': {
                'ingredients': r'\b(?:ingredients?|you will need)\s*:?\s*([^.!?]+)',
                'instructions': r'\b(?:instructions?|directions?|method)\s*:?\s*([^.!?]+)',
                'recipes': r'\b(?:recipe|dish|meal)\s*:?\s*([^.!?]+)',
                'preparation': r'\b(?:prepare|cook|make|serve)\s+([^.!?]+)'
            }
        }
    
    def refine_text_content(self, text: str, content_type: str = 'general') -> str:
        """
        Refine and clean text content.
        
        Args:
            text: Raw text content
            content_type: Type of content ('travel', 'hr', 'food', 'general')
            
        Returns:
            Refined text content
        """
        if not text:
            return ""
        
        # Clean up common PDF artifacts
        refined = self._clean_pdf_artifacts(text)
        
        # Remove excessive whitespace
        refined = re.sub(r'\s+', ' ', refined)
        
        # Remove common noise patterns
        refined = self._remove_noise_patterns(refined)
        
        # Extract relevant content based on type
        if content_type in self.patterns:
            refined = self._extract_relevant_content(refined, content_type)
        
        return refined.strip()
    
    def _clean_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts."""
        # Remove page numbers and headers
        text = re.sub(r'\b(?:Page|P)\s*\d+\b', '', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove common PDF artifacts
        artifacts = [
            r'Adobe\s+Reader',
            r'PDF\s+Document',
            r'Page\s+\d+\s+of\s+\d+',
            r'©\s*\d{4}',
            r'All\s+rights\s+reserved',
            r'Confidential',
            r'Draft',
            r'Adobe\s+Acrobat',
            r'Learn\s+Acrobat',
            r'Adobe\s+PDF'
        ]
        
        for pattern in artifacts:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Clean up bullet points and formatting
        text = re.sub(r'^\s*[•\-\*]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _remove_noise_patterns(self, text: str) -> str:
        """Remove noise patterns from text."""
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.!?]{3,}', '.', text)
        
        # Remove excessive spaces
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text
    
    def _extract_relevant_content(self, text: str, content_type: str) -> str:
        """Extract content relevant to the specific type."""
        patterns = self.patterns.get(content_type, {})
        relevant_sentences = []
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < self.min_content_length:
                continue
            
            # Check if sentence contains relevant patterns
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, sentence, re.IGNORECASE):
                    relevant_sentences.append(sentence)
                    break
        
        if relevant_sentences:
            return '. '.join(relevant_sentences) + '.'
        else:
            return text
    
    def extract_key_information(self, text: str, content_type: str = 'general') -> Dict[str, List[str]]:
        """
        Extract key information from text based on content type.
        
        Args:
            text: Text content to analyze
            content_type: Type of content ('travel', 'hr', 'food', 'general')
            
        Returns:
            Dictionary with extracted information categories
        """
        extracted_info = {}
        
        if content_type == 'travel':
            extracted_info = self._extract_travel_info(text)
        elif content_type == 'hr':
            extracted_info = self._extract_hr_info(text)
        elif content_type == 'food':
            extracted_info = self._extract_food_info(text)
        else:
            extracted_info = self._extract_general_info(text)
        
        return extracted_info
    
    def _extract_travel_info(self, text: str) -> Dict[str, List[str]]:
        """Extract travel-specific information."""
        info = {
            'destinations': [],
            'activities': [],
            'tips': [],
            'locations': []
        }
        
        # Extract destinations
        destinations = re.findall(r'\b(?:visit|go to|see|explore)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
        info['destinations'].extend(destinations)
        
        # Extract activities
        activities = re.findall(r'\b(?:enjoy|experience|try|discover)\s+([^.!?]+)', text, re.IGNORECASE)
        info['activities'].extend(activities)
        
        # Extract tips
        tips = re.findall(r'\b(?:tip|advice|recommendation|suggestion)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['tips'].extend(tips)
        
        # Extract locations
        locations = re.findall(r'\b(?:in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
        info['locations'].extend(locations)
        
        return info
    
    def _extract_hr_info(self, text: str) -> Dict[str, List[str]]:
        """Extract HR-specific information."""
        info = {
            'steps': [],
            'features': [],
            'instructions': [],
            'workflows': []
        }
        
        # Extract steps
        steps = re.findall(r'\b(?:step|procedure|process)\s+\d+[:\s]*([^.!?]+)', text, re.IGNORECASE)
        info['steps'].extend(steps)
        
        # Extract features
        features = re.findall(r'\b(?:feature|function|tool)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['features'].extend(features)
        
        # Extract instructions
        instructions = re.findall(r'\b(?:click|select|choose|enable)\s+([^.!?]+)', text, re.IGNORECASE)
        info['instructions'].extend(instructions)
        
        # Extract workflows
        workflows = re.findall(r'\b(?:workflow|process|automation)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['workflows'].extend(workflows)
        
        return info
    
    def _extract_food_info(self, text: str) -> Dict[str, List[str]]:
        """Extract food-specific information."""
        info = {
            'ingredients': [],
            'instructions': [],
            'recipes': [],
            'preparation': []
        }
        
        # Extract ingredients
        ingredients = re.findall(r'\b(?:ingredients?|you will need)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['ingredients'].extend(ingredients)
        
        # Extract instructions
        instructions = re.findall(r'\b(?:instructions?|directions?|method)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['instructions'].extend(instructions)
        
        # Extract recipes
        recipes = re.findall(r'\b(?:recipe|dish|meal)\s*:?\s*([^.!?]+)', text, re.IGNORECASE)
        info['recipes'].extend(recipes)
        
        # Extract preparation steps
        preparation = re.findall(r'\b(?:prepare|cook|make|serve)\s+([^.!?]+)', text, re.IGNORECASE)
        info['preparation'].extend(preparation)
        
        return info
    
    def _extract_general_info(self, text: str) -> Dict[str, List[str]]:
        """Extract general information from text."""
        info = {
            'key_points': [],
            'definitions': [],
            'examples': []
        }
        
        # Extract key points (sentences with important keywords)
        key_words = ['important', 'key', 'essential', 'critical', 'main', 'primary']
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence.lower() for word in key_words):
                info['key_points'].append(sentence)
        
        # Extract definitions
        definitions = re.findall(r'\b(?:is|are|refers to|means)\s+([^.!?]+)', text, re.IGNORECASE)
        info['definitions'].extend(definitions)
        
        # Extract examples
        examples = re.findall(r'\b(?:example|for instance|such as)\s+([^.!?]+)', text, re.IGNORECASE)
        info['examples'].extend(examples)
        
        return info
    
    def summarize_content(self, text: str, max_length: int = None) -> str:
        """
        Create a concise summary of the content.
        
        Args:
            text: Text content to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        if not text:
            return ""
        
        if max_length is None:
            max_length = self.max_summary_length
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return ""
        
        # If text is already short enough, return as is
        if len(text) <= max_length:
            return text
        
        # Select the most important sentences
        important_sentences = self._select_important_sentences(sentences)
        
        # Combine sentences until we reach the max length
        summary = ""
        for sentence in important_sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()
    
    def _select_important_sentences(self, sentences: List[str]) -> List[str]:
        """Select the most important sentences based on content analysis."""
        if not sentences:
            return []
        
        # Score sentences based on various factors
        scored_sentences = []
        
        for sentence in sentences:
            score = 0
            
            # Score based on length (prefer medium-length sentences)
            length = len(sentence)
            if 20 <= length <= 100:
                score += 2
            elif 10 <= length <= 150:
                score += 1
            
            # Score based on keywords
            important_words = ['important', 'key', 'essential', 'main', 'primary', 'best', 'top']
            for word in important_words:
                if word in sentence.lower():
                    score += 3
            
            # Score based on action words
            action_words = ['create', 'build', 'make', 'do', 'use', 'try', 'visit', 'explore']
            for word in action_words:
                if word in sentence.lower():
                    score += 2
            
            # Score based on specific terms
            specific_terms = ['recipe', 'ingredient', 'form', 'workflow', 'destination', 'activity']
            for term in specific_terms:
                if term in sentence.lower():
                    score += 2
            
            scored_sentences.append((sentence, score))
        
        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in scored_sentences[:5]]
    
    def create_actionable_summary(self, text: str, content_type: str) -> str:
        """
        Create an actionable summary based on content type.
        
        Args:
            text: Text content to summarize
            content_type: Type of content ('travel', 'hr', 'food')
            
        Returns:
            Actionable summary
        """
        if content_type == 'travel':
            return self._create_travel_summary(text)
        elif content_type == 'hr':
            return self._create_hr_summary(text)
        elif content_type == 'food':
            return self._create_food_summary(text)
        else:
            return self.summarize_content(text)
    
    def _create_travel_summary(self, text: str) -> str:
        """Create travel-specific actionable summary."""
        # Extract key travel information
        info = self._extract_travel_info(text)
        
        summary_parts = []
        
        if info['destinations']:
            destinations = info['destinations'][:3]
            summary_parts.append(f"Key destinations: {', '.join(destinations)}")
        
        if info['activities']:
            activities = info['activities'][:2]
            summary_parts.append(f"Recommended activities: {', '.join(activities)}")
        
        if info['tips']:
            summary_parts.append(f"Travel tips: {info['tips'][0]}")
        
        # If no structured info found, create a general summary
        if not summary_parts:
            sentences = re.split(r'[.!?]+', text)
            relevant_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(word in sentence.lower() for word in 
                    ['visit', 'see', 'explore', 'enjoy', 'experience', 'discover', 'try', 'go to']):
                    relevant_sentences.append(sentence)
                    if len(relevant_sentences) >= 2:
                        break
            
            if relevant_sentences:
                return '. '.join(relevant_sentences) + '.'
        
        return '. '.join(summary_parts) if summary_parts else self.summarize_content(text)
    
    def _create_hr_summary(self, text: str) -> str:
        """Create HR-specific actionable summary."""
        # Extract key HR information
        info = self._extract_hr_info(text)
        
        summary_parts = []
        
        if info['steps']:
            summary_parts.append(f"Key steps: {info['steps'][0]}")
        
        if info['features']:
            features = info['features'][:2]
            summary_parts.append(f"Features: {', '.join(features)}")
        
        if info['instructions']:
            summary_parts.append(f"Instructions: {info['instructions'][0]}")
        
        # If no structured info found, create a general summary
        if not summary_parts:
            sentences = re.split(r'[.!?]+', text)
            relevant_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(word in sentence.lower() for word in 
                    ['create', 'build', 'design', 'fill', 'sign', 'send', 'track', 'manage', 'organize']):
                    relevant_sentences.append(sentence)
                    if len(relevant_sentences) >= 2:
                        break
            
            if relevant_sentences:
                return '. '.join(relevant_sentences) + '.'
        
        return '. '.join(summary_parts) if summary_parts else self.summarize_content(text)
    
    def _create_food_summary(self, text: str) -> str:
        """Create food-specific actionable summary."""
        # Extract key food information
        info = self._extract_food_info(text)
        
        summary_parts = []
        
        if info['recipes']:
            summary_parts.append(f"Recipe: {info['recipes'][0]}")
        
        if info['ingredients']:
            summary_parts.append(f"Ingredients: {info['ingredients'][0]}")
        
        if info['instructions']:
            summary_parts.append(f"Instructions: {info['instructions'][0]}")
        
        # If no structured info found, create a general summary
        if not summary_parts:
            sentences = re.split(r'[.!?]+', text)
            relevant_sentences = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and any(word in sentence.lower() for word in 
                    ['ingredient', 'recipe', 'cook', 'prepare', 'serve', 'dish', 'meal', 'food']):
                    relevant_sentences.append(sentence)
                    if len(relevant_sentences) >= 2:
                        break
            
            if relevant_sentences:
                return '. '.join(relevant_sentences) + '.'
        
        return '. '.join(summary_parts) if summary_parts else self.summarize_content(text) 