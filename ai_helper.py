"""
AI Helper Module - Professional ChatGPT integration
Provides task suggestions, auto-categorization, and productivity insights
With comprehensive error handling and logging
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

try:
    from openai import OpenAI, APIError, RateLimitError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed")


class AIConfigError(Exception):
    """Raised when AI configuration is invalid"""
    pass


class AIHelper:
    """
    Manages AI interactions with OpenAI API
    Handles task suggestions, auto-categorization, and insights
    """
    
    # Valid task categories
    VALID_CATEGORIES = ["Work", "Study", "Shopping", "Personal", "Health", "Other", "General"]
    
    # API configuration
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_RETRIES = 3
    TIMEOUT = 30
    
    def __init__(self):
        """Initialize OpenAI client with validation"""
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize and validate OpenAI client"""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not available")
            return
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set in environment")
            return
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise AIConfigError(f"OpenAI initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if AI features are available and configured"""
        return self.client is not None and OPENAI_AVAILABLE
    
    def suggest_tasks(self, existing_tasks: List[Dict]) -> Optional[List[str]]:
        """
        Generate intelligent task suggestions based on existing tasks
        
        Args:
            existing_tasks: List of existing task dictionaries
            
        Returns:
            List of suggested task titles or None if error occurs
        """
        if not self.is_available():
            logger.error("AI features not available")
            print("❌ AI features not available. Please configure OPENAI_API_KEY")
            return None
        
        try:
            task_summary = self._summarize_tasks(existing_tasks)
            
            prompt = f"""Based on the following tasks that this person has:

{task_summary}

Generate 3-5 NEW task suggestions that would help them be more productive today.
The suggestions should be practical, actionable, and complement their existing tasks.
Focus on tasks that improve productivity and well-being.

Return ONLY a valid JSON array of strings (task titles), no other text. Example:
["Task 1", "Task 2", "Task 3"]"""
            
            logger.info("Requesting task suggestions from OpenAI")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
                timeout=self.TIMEOUT
            )
            
            response_text = response.choices[0].message.content.strip()
            suggestions = json.loads(response_text)
            
            if not isinstance(suggestions, list):
                logger.warning("Invalid response format from OpenAI")
                return None
            
            # Validate suggestions
            valid_suggestions = [s for s in suggestions if isinstance(s, str) and s.strip()]
            logger.info(f"Generated {len(valid_suggestions)} task suggestions")
            return valid_suggestions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            print("⚠️  Error parsing AI response. Please try again.")
            return None
        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            print("⚠️  Rate limit exceeded. Please try again in a moment.")
            return None
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            print(f"❌ API error: {str(e)[:100]}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating suggestions: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def auto_categorize(self, task_title: str) -> str:
        """
        Automatically categorize a task using AI analysis
        
        Args:
            task_title: The task title to categorize
            
        Returns:
            Category name (from VALID_CATEGORIES) or "General" as fallback
        """
        if not self.is_available():
            logger.debug(f"AI not available, using default category for: {task_title}")
            return "General"
        
        # Validate input
        if not task_title or not isinstance(task_title, str):
            logger.warning("Invalid task title for categorization")
            return "General"
        
        try:
            categories_str = ", ".join(self.VALID_CATEGORIES)
            prompt = f"""Categorize this task into ONE of these categories: {categories_str}

Task: "{task_title}"

Respond with ONLY the category name from the list, nothing else."""
            
            logger.debug(f"Auto-categorizing task: {task_title[:50]}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent categorization
                max_tokens=20,
                timeout=self.TIMEOUT
            )
            
            category = response.choices[0].message.content.strip()
            
            # Validate and sanitize category
            if category in self.VALID_CATEGORIES:
                logger.info(f"Task categorized as '{category}'")
                return category
            
            logger.warning(f"Invalid category returned: {category}, using General")
            return "General"
            
        except RateLimitError:
            logger.warning("Rate limit in auto-categorize")
            return "General"
        except APIError as e:
            logger.error(f"API error in categorization: {e}")
            return "General"
        except Exception as e:
            logger.error(f"Error in auto-categorize: {e}")
            return "General"
    
    def get_task_insights(self, tasks: List[Dict]) -> Optional[str]:
        """
        Generate AI-powered insights about task productivity
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Insight string or None if error occurs
        """
        if not self.is_available():
            logger.debug("AI not available for insights")
            return None
        
        if not tasks:
            return "No tasks to analyze for insights."
        
        try:
            task_summary = self._summarize_tasks(tasks)
            
            prompt = f"""Analyze these tasks and provide brief, actionable productivity insights:

{task_summary}

Give 2-3 sentences of constructive feedback about their task management, 
focusing on patterns, priorities, and improvements."""
            
            logger.info("Requesting productivity insights from OpenAI")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=150,
                timeout=self.TIMEOUT
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info("Insights generated successfully")
            return insights
            
        except RateLimitError:
            logger.warning("Rate limit in insights generation")
            return None
        except APIError as e:
            logger.error(f"API error getting insights: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return None
    
    def _summarize_tasks(self, tasks: List[Dict]) -> str:
        """
        Create a concise text summary of tasks for AI context
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            Formatted task summary string
        """
        if not tasks:
            return "No existing tasks yet."
        
        summary = []
        # Limit to last 10 tasks to avoid token limits
        for task in tasks[-10:]:
            status = "✅ Completed" if task.get("completed") else "⭕ Pending"
            title = task.get("title", "Untitled")[:50]
            category = task.get("category", "General")
            summary.append(f"- [{status}] {title} (Category: {category})")
        
        return "\n".join(summary) if summary else "No tasks found."
    
    @staticmethod
    def validate_configuration() -> bool:
        """
        Validate OpenAI configuration
        
        Returns:
            True if properly configured, False otherwise
        """
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not installed")
            print("❌ OpenAI library not installed.")
            print("   Install with: pip install openai")
            return False
        
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            logger.warning("OPENAI_API_KEY not configured")
            print("⚠️  OPENAI_API_KEY not set in environment.")
            print("   Create a .env file with: OPENAI_API_KEY=your_api_key")
            return False
        
        logger.info("OpenAI configuration validated")
        return True
