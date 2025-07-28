import re
from typing import Dict, List, Any, Tuple
from enum import Enum


class PersonaType(Enum):
    """Enumeration of supported persona types."""
    TRAVEL_PLANNER = "Travel Planner"
    HR_PROFESSIONAL = "HR professional"
    FOOD_CONTRACTOR = "Food Contractor"


class PersonaAnalyzer:
    """Analyzes content based on specific personas and their tasks."""
    
    def __init__(self):
        self.persona_keywords = {
            PersonaType.TRAVEL_PLANNER: {
                'destinations': ['city', 'town', 'village', 'coast', 'beach', 'mountain'],
                'activities': ['visit', 'explore', 'tour', 'experience', 'enjoy', 'discover'],
                'logistics': ['hotel', 'restaurant', 'transport', 'booking', 'reservation'],
                'planning': ['itinerary', 'schedule', 'plan', 'organize', 'arrange'],
                'group_travel': ['group', 'friends', 'college', 'budget', 'shared'],
                'cultural': ['culture', 'tradition', 'history', 'local', 'authentic']
            },
            PersonaType.HR_PROFESSIONAL: {
                'forms': ['form', 'fillable', 'interactive', 'field', 'input'],
                'compliance': ['compliance', 'legal', 'regulation', 'policy', 'requirement'],
                'workflow': ['workflow', 'process', 'approval', 'signature', 'tracking'],
                'onboarding': ['onboarding', 'new hire', 'employee', 'orientation', 'training'],
                'documentation': ['document', 'record', 'file', 'archive', 'store'],
                'automation': ['automate', 'efficiency', 'streamline', 'optimize']
            },
            PersonaType.FOOD_CONTRACTOR: {
                'recipes': ['recipe', 'ingredient', 'cook', 'prepare', 'make'],
                'vegetarian': ['vegetarian', 'vegan', 'plant-based', 'meatless'],
                'buffet': ['buffet', 'catering', 'large group', 'serving', 'presentation'],
                'corporate': ['corporate', 'business', 'professional', 'formal'],
                'dietary': ['gluten-free', 'allergy', 'dietary', 'restriction'],
                'planning': ['menu', 'planning', 'preparation', 'timing', 'logistics']
            }
        }
        
        self.task_keywords = {
            PersonaType.TRAVEL_PLANNER: {
                'trip_planning': ['plan', 'organize', 'arrange', 'schedule', 'itinerary'],
                'group_coordination': ['group', 'friends', 'college', 'budget', 'shared'],
                'destination_research': ['destination', 'location', 'place', 'area', 'region'],
                'activity_planning': ['activity', 'attraction', 'experience', 'entertainment'],
                'logistics': ['accommodation', 'transport', 'booking', 'reservation']
            },
            PersonaType.HR_PROFESSIONAL: {
                'form_creation': ['create', 'build', 'design', 'develop', 'make'],
                'form_management': ['manage', 'organize', 'track', 'monitor', 'maintain'],
                'onboarding_process': ['onboarding', 'new hire', 'employee', 'orientation'],
                'compliance_tracking': ['compliance', 'legal', 'regulation', 'requirement'],
                'workflow_automation': ['automate', 'workflow', 'process', 'efficiency']
            },
            PersonaType.FOOD_CONTRACTOR: {
                'menu_planning': ['menu', 'plan', 'design', 'create', 'develop'],
                'vegetarian_catering': ['vegetarian', 'catering', 'buffet', 'serving'],
                'corporate_event': ['corporate', 'business', 'professional', 'formal'],
                'dietary_accommodation': ['dietary', 'allergy', 'restriction', 'gluten-free'],
                'preparation_logistics': ['prepare', 'cook', 'timing', 'logistics']
            }
        }
    
    def get_persona_type(self, persona_role: str) -> PersonaType:
        """
        Determine persona type from role string.
        
        Args:
            persona_role: Role string from input
            
        Returns:
            PersonaType enum value
        """
        role_lower = persona_role.lower()
        
        if 'travel' in role_lower or 'planner' in role_lower:
            return PersonaType.TRAVEL_PLANNER
        elif 'hr' in role_lower or 'professional' in role_lower:
            return PersonaType.HR_PROFESSIONAL
        elif 'food' in role_lower or 'contractor' in role_lower:
            return PersonaType.FOOD_CONTRACTOR
        else:
            # Default to travel planner if unknown
            return PersonaType.TRAVEL_PLANNER
    
    def analyze_content_relevance(self, text: str, persona_type: PersonaType, 
                                task_description: str) -> Tuple[float, List[str]]:
        """
        Analyze content relevance for a specific persona and task.
        
        Args:
            text: Text content to analyze
            persona_type: Type of persona
            task_description: Description of the task
            
        Returns:
            Tuple of (relevance_score, relevant_keywords)
        """
        text_lower = text.lower()
        task_lower = task_description.lower()
        
        # Get keywords for this persona
        persona_keywords = self.persona_keywords.get(persona_type, {})
        task_keywords = self.task_keywords.get(persona_type, {})
        
        # Calculate relevance score
        relevance_score = 0.0
        relevant_keywords = []
        
        # Check persona-specific keywords
        for category, keywords in persona_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    relevance_score += 0.1
                    relevant_keywords.append(keyword)
        
        # Check task-specific keywords
        for category, keywords in task_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    relevance_score += 0.2
                    relevant_keywords.append(keyword)
        
        # Check for task-specific terms in the text
        task_terms = task_lower.split()
        for term in task_terms:
            if len(term) > 3 and term in text_lower:
                relevance_score += 0.15
                relevant_keywords.append(term)
        
        # Normalize score
        relevance_score = min(relevance_score, 1.0)
        
        return relevance_score, list(set(relevant_keywords))
    
    def extract_actionable_content(self, text: str, persona_type: PersonaType) -> List[str]:
        """
        Extract actionable content based on persona type.
        
        Args:
            text: Text content to analyze
            persona_type: Type of persona
            
        Returns:
            List of actionable content snippets
        """
        actionable_content = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for actionable patterns based on persona
            if persona_type == PersonaType.TRAVEL_PLANNER:
                if self._is_travel_actionable(line):
                    actionable_content.append(line)
            elif persona_type == PersonaType.HR_PROFESSIONAL:
                if self._is_hr_actionable(line):
                    actionable_content.append(line)
            elif persona_type == PersonaType.FOOD_CONTRACTOR:
                if self._is_food_actionable(line):
                    actionable_content.append(line)
        
        return actionable_content
    
    def _is_travel_actionable(self, line: str) -> bool:
        """Check if line contains actionable travel information."""
        action_indicators = [
            'visit', 'go to', 'see', 'explore', 'try', 'book', 'reserve',
            'stay at', 'eat at', 'enjoy', 'experience', 'discover'
        ]
        return any(indicator in line.lower() for indicator in action_indicators)
    
    def _is_hr_actionable(self, line: str) -> bool:
        """Check if line contains actionable HR information."""
        action_indicators = [
            'create', 'build', 'design', 'fill', 'sign', 'send', 'track',
            'manage', 'organize', 'automate', 'enable', 'configure'
        ]
        return any(indicator in line.lower() for indicator in action_indicators)
    
    def _is_food_actionable(self, line: str) -> bool:
        """Check if line contains actionable food information."""
        action_indicators = [
            'ingredients', 'instructions', 'cook', 'prepare', 'serve',
            'recipe', 'method', 'steps', 'directions'
        ]
        return any(indicator in line.lower() for indicator in action_indicators)
    
    def rank_sections_by_importance(self, sections: List[Dict], persona_type: PersonaType,
                                  task_description: str) -> List[Tuple[Dict, float]]:
        """
        Rank sections by importance for the specific persona and task.
        
        Args:
            sections: List of section dictionaries
            persona_type: Type of persona
            task_description: Description of the task
            
        Returns:
            List of tuples (section, importance_score) sorted by importance
        """
        ranked_sections = []
        
        for section in sections:
            title = section.get('title', '')
            content = section.get('content', '')
            
            # Analyze title relevance
            title_relevance, _ = self.analyze_content_relevance(title, persona_type, task_description)
            
            # Analyze content relevance
            content_relevance, _ = self.analyze_content_relevance(content, persona_type, task_description)
            
            # Calculate overall importance score
            importance_score = (title_relevance * 0.4) + (content_relevance * 0.6)
            
            ranked_sections.append((section, importance_score))
        
        # Sort by importance score (descending)
        ranked_sections.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_sections
    
    def get_persona_specific_filters(self, persona_type: PersonaType) -> Dict[str, Any]:
        """
        Get persona-specific filtering criteria.
        
        Args:
            persona_type: Type of persona
            
        Returns:
            Dictionary with filtering criteria
        """
        filters = {
            PersonaType.TRAVEL_PLANNER: {
                'min_content_length': 50,
                'preferred_keywords': ['destination', 'activity', 'hotel', 'restaurant', 'transport'],
                'exclude_keywords': ['advertisement', 'sponsored', 'promotion']
            },
            PersonaType.HR_PROFESSIONAL: {
                'min_content_length': 30,
                'preferred_keywords': ['form', 'fillable', 'signature', 'workflow', 'compliance'],
                'exclude_keywords': ['advertisement', 'promotion', 'marketing']
            },
            PersonaType.FOOD_CONTRACTOR: {
                'min_content_length': 40,
                'preferred_keywords': ['recipe', 'ingredient', 'cook', 'prepare', 'serve'],
                'exclude_keywords': ['advertisement', 'promotion', 'sponsored']
            }
        }
        
        return filters.get(persona_type, {}) 