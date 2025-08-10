"""
AI Integration Module for Smart Todo List
Handles AI-powered task management features including:
- Context processing and analysis
- Task prioritization
- Deadline suggestions
- Smart categorization
- Task enhancement
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from django.conf import settings
from django.utils import timezone

class AITaskManager:
    """AI-powered task management system"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        
    def analyze_context(self, context_text: str, source_type: str = 'notes') -> Dict:
        """
        Analyze daily context to extract insights, keywords, and sentiment
        """
        try:
            prompt = f"""
            Analyze the following {source_type} content and extract:
            1. Key topics and themes
            2. Important deadlines or time-sensitive information
            3. Priority indicators (urgent, important, etc.)
            4. Sentiment (positive, negative, neutral)
            5. Action items or tasks mentioned
            6. Relevant keywords
            
            Content: {context_text}
            
            Return as JSON with keys: topics, deadlines, priorities, sentiment, action_items, keywords
            """
            
            response = self._call_ai_api(prompt)
            if response:
                return json.loads(response)
            else:
                # Fallback analysis without AI
                return self._fallback_context_analysis(context_text)
                
        except Exception as e:
            print(f"Error in context analysis: {e}")
            return self._fallback_context_analysis(context_text)
    
    def prioritize_task(self, task_title: str, task_description: str, 
                       context_entries: List[Dict] = None) -> float:
        """
        Calculate AI-based priority score for a task
        """
        try:
            context_summary = ""
            if context_entries:
                context_summary = " ".join([entry.get('content', '') for entry in context_entries])
            
            prompt = f"""
            Calculate a priority score (0.0 to 1.0) for this task based on:
            - Task title: {task_title}
            - Task description: {task_description}
            - Recent context: {context_summary}
            
            Consider factors like:
            - Urgency indicators (deadline, urgent, ASAP, etc.)
            - Importance keywords (critical, important, must, etc.)
            - Context relevance
            - Time sensitivity
            
            Return only the numeric score (0.0 to 1.0).
            """
            
            response = self._call_ai_api(prompt)
            if response:
                try:
                    return float(response.strip())
                except ValueError:
                    return self._fallback_priority_calculation(task_title, task_description)
            else:
                return self._fallback_priority_calculation(task_title, task_description)
                
        except Exception as e:
            print(f"Error in task prioritization: {e}")
            return self._fallback_priority_calculation(task_title, task_description)
    
    def suggest_deadline(self, task_title: str, task_description: str, 
                        current_workload: int = 0) -> Optional[datetime]:
        """
        Suggest realistic deadline based on task complexity and workload
        """
        try:
            prompt = f"""
            Suggest a realistic deadline for this task:
            - Task: {task_title}
            - Description: {task_description}
            - Current workload: {current_workload} tasks
            
            Consider:
            - Task complexity and scope
            - Current workload
            - Typical completion times for similar tasks
            - Buffer time for unexpected issues
            
            Return the suggested deadline in format: YYYY-MM-DD HH:MM
            If no specific deadline needed, return "None"
            """
            
            response = self._call_ai_api(prompt)
            if response and response.strip().lower() != "none":
                try:
                    return datetime.strptime(response.strip(), "%Y-%m-%d %H:%M")
                except ValueError:
                    return self._fallback_deadline_suggestion(task_title, current_workload)
            else:
                return None
                
        except Exception as e:
            print(f"Error in deadline suggestion: {e}")
            return self._fallback_deadline_suggestion(task_title, current_workload)
    
    def suggest_categories_and_tags(self, task_title: str, task_description: str) -> Tuple[str, List[str]]:
        """
        Suggest category and tags for a task
        """
        try:
            prompt = f"""
            Suggest a category and tags for this task:
            - Task: {task_title}
            - Description: {task_description}
            
            Return as JSON: {{"category": "category_name", "tags": ["tag1", "tag2", "tag3"]}}
            
            Common categories: Work, Personal, Health, Finance, Learning, Home, Social
            """
            
            response = self._call_ai_api(prompt)
            if response:
                try:
                    result = json.loads(response)
                    return result.get('category', 'General'), result.get('tags', [])
                except json.JSONDecodeError:
                    return self._fallback_categorization(task_title)
            else:
                return self._fallback_categorization(task_title)
                
        except Exception as e:
            print(f"Error in categorization: {e}")
            return self._fallback_categorization(task_title)
    
    def enhance_task_description(self, task_title: str, task_description: str, 
                                context_entries: List[Dict] = None) -> str:
        """
        Enhance task description with context-aware details
        """
        try:
            context_summary = ""
            if context_entries:
                context_summary = " ".join([entry.get('content', '') for entry in context_entries])
            
            prompt = f"""
            Enhance this task description with relevant context and details:
            - Original title: {task_title}
            - Original description: {task_description}
            - Context: {context_summary}
            
            Provide an enhanced description that:
            - Includes relevant context
            - Adds specific details and requirements
            - Mentions related deadlines or dependencies
            - Suggests approach or steps
            
            Return only the enhanced description.
            """
            
            response = self._call_ai_api(prompt)
            if response:
                return response.strip()
            else:
                return self._fallback_description_enhancement(task_title, task_description)
                
        except Exception as e:
            print(f"Error in description enhancement: {e}")
            return self._fallback_description_enhancement(task_title, task_description)
    
    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """
        Call OpenAI API for AI processing
        """
        if not self.api_key:
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"API call failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error calling AI API: {e}")
            return None
    
    def _fallback_context_analysis(self, context_text: str) -> Dict:
        """Fallback context analysis without AI"""
        keywords = re.findall(r'\b\w{4,}\b', context_text.lower())
        keywords = [k for k in keywords if k not in ['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were']]
        
        urgency_words = ['urgent', 'asap', 'immediately', 'deadline', 'due', 'important', 'critical']
        urgency_score = sum(1 for word in urgency_words if word in context_text.lower())
        
        return {
            'topics': keywords[:5],
            'deadlines': [],
            'priorities': ['high' if urgency_score > 0 else 'normal'],
            'sentiment': 'neutral',
            'action_items': [],
            'keywords': keywords[:10]
        }
    
    def _fallback_priority_calculation(self, title: str, description: str) -> float:
        """Fallback priority calculation"""
        urgency_words = ['urgent', 'asap', 'immediately', 'deadline', 'due', 'important', 'critical', 'emergency']
        text = f"{title} {description}".lower()
        
        urgency_count = sum(1 for word in urgency_words if word in text)
        if urgency_count >= 2:
            return 0.9
        elif urgency_count == 1:
            return 0.7
        else:
            return 0.5
    
    def _fallback_deadline_suggestion(self, title: str, workload: int) -> Optional[datetime]:
        """Fallback deadline suggestion"""
        # Simple heuristic: add 1-3 days based on workload
        days_to_add = min(workload + 1, 7)
        return timezone.now() + timedelta(days=days_to_add)
    
    def _fallback_categorization(self, title: str) -> Tuple[str, List[str]]:
        """Fallback categorization"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['work', 'job', 'office', 'meeting', 'project']):
            return 'Work', ['work', 'professional']
        elif any(word in title_lower for word in ['home', 'house', 'clean', 'cook', 'garden']):
            return 'Home', ['home', 'household']
        elif any(word in title_lower for word in ['health', 'exercise', 'gym', 'doctor', 'medical']):
            return 'Health', ['health', 'wellness']
        elif any(word in title_lower for word in ['learn', 'study', 'course', 'book', 'read']):
            return 'Learning', ['learning', 'education']
        else:
            return 'Personal', ['personal', 'general']
    
    def _fallback_description_enhancement(self, title: str, description: str) -> str:
        """Fallback description enhancement"""
        if description:
            return description
        else:
            return f"Task: {title}. Please add more details as needed."

# Global AI manager instance
ai_manager = AITaskManager()
