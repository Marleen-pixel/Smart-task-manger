"""
AI Integration Module for Smart Task Manager
Provides ChatGPT-powered task suggestions and auto-categorization
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Default categories for fallback categorization
DEFAULT_CATEGORIES = {
    "Study": ["study", "learn", "homework", "project", "assignment", "course", "exam", "book", "reading", "research"],
    "Work": ["work", "meeting", "email", "report", "deadline", "project", "client", "presentation", "task", "office"],
    "Personal": ["personal", "doctor", "health", "gym", "exercise", "appointment", "family", "friend"],
    "Shopping": ["shopping", "buy", "groceries", "store", "mall", "purchase", "shop"],
    "General": []
}


class AITaskSuggester:
    """AI-powered task suggestion and categorization engine"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Task Suggester
        
        Args:
            api_key: OpenAI API key (can be set via environment variable)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = "gpt-3.5-turbo"
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
    def is_available(self) -> bool:
        """Check if AI features are available"""
        return self.client is not None
    
    def generate_task_suggestions(self, user_query: str, max_suggestions: int = 5) -> List[Dict]:
        """
        Generate task suggestions based on user query using ChatGPT
        
        Args:
            user_query: User's natural language input (e.g., "آج مجھے کیا کرنا چاہیے؟")
            max_suggestions: Maximum number of suggestions to generate
        
        Returns:
            List of suggested tasks with titles
        """
        if not self.is_available():
            print("⚠️  OpenAI API not configured. Using fallback suggestions.")
            return self._fallback_suggestions()
        
        try:
            prompt = f"""Generate {max_suggestions} practical task suggestions based on this query: "{user_query}"
            
            Return as a JSON array with this format:
            [
                {{"title": "Task description", "priority": "high/medium/low"}},
                ...
            ]
            
            Make suggestions relevant, actionable, and diverse."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful task management assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            suggestions = json.loads(response_text)
            
            return suggestions
        
        except json.JSONDecodeError:
            print("❌ Error parsing AI response. Using fallback suggestions.")
            return self._fallback_suggestions()
        except Exception as e:
            print(f"⚠️  AI Error: {e}. Using fallback suggestions.")
            return self._fallback_suggestions()
    
    def _fallback_suggestions(self) -> List[Dict]:
        """Provide default suggestions when AI is unavailable"""
        return [
            {"title": "Morning routine - exercise or meditation", "priority": "high"},
            {"title": "Check and respond to important emails", "priority": "medium"},
            {"title": "Plan your daily schedule", "priority": "high"},
            {"title": "Work on priority project", "priority": "high"},
            {"title": "Review learning materials or new concepts", "priority": "medium"}
        ]
    
    def categorize_task_ai(self, task_title: str) -> str:
        """
        Categorize a task using AI (ChatGPT)
        
        Args:
            task_title: Title of the task to categorize
        
        Returns:
            Category name
        """
        if not self.is_available():
            return self.categorize_task_fallback(task_title)
        
        try:
            prompt = f"""Categorize this task into ONE of these categories: Study, Work, Personal, Shopping, or General.
            
            Task: "{task_title}"
            
            Return ONLY the category name, nothing else."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task categorization expert. Respond with only the category name."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip()
            
            # Validate category
            valid_categories = list(DEFAULT_CATEGORIES.keys())
            if category in valid_categories:
                return category
            else:
                return self.categorize_task_fallback(task_title)
        
        except Exception as e:
            print(f"⚠️  AI Categorization error: {e}")
            return self.categorize_task_fallback(task_title)
    
    def categorize_task_fallback(self, task_title: str) -> str:
        """
        Fallback categorization using keyword matching
        
        Args:
            task_title: Title of the task to categorize
        
        Returns:
            Category name
        """
        task_lower = task_title.lower()
        
        for category, keywords in DEFAULT_CATEGORIES.items():
            for keyword in keywords:
                if keyword in task_lower:
                    return category
        
        return "General"
    
    def auto_categorize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Auto-categorize multiple tasks
        
        Args:
            tasks: List of tasks to categorize
        
        Returns:
            List of tasks with updated categories
        """
        categorized_tasks = []
        
        for task in tasks:
            if task.get("category") == "General" or "category" not in task:
                task["category"] = self.categorize_task_ai(task["title"])
                task["auto_categorized"] = True
            categorized_tasks.append(task)
        
        return categorized_tasks
    
    def suggest_today_tasks(self, existing_tasks: List[Dict] = None) -> List[Dict]:
        """
        Suggest tasks for today based on existing tasks
        
        Args:
            existing_tasks: List of existing tasks (optional)
        
        Returns:
            List of suggested tasks for today
        """
        context = ""
        if existing_tasks:
            categories = {}
            for task in existing_tasks:
                cat = task.get("category", "General")
                categories[cat] = categories.get(cat, 0) + 1
            
            context = f"\nExisting tasks by category: {json.dumps(categories)}"
        
        query = f"آج مجھے کیا کرنا چاہیے؟{context}"
        suggestions = self.generate_task_suggestions(query)
        
        # Categorize each suggestion
        for suggestion in suggestions:
            suggestion["category"] = self.categorize_task_ai(suggestion["title"])
        
        return suggestions


class TaskAIHelper:
    """Helper class to integrate AI with TaskManager"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI helper"""
        self.ai_suggester = AITaskSuggester(api_key)
    
    def suggest_and_add_interactive(self, task_manager) -> bool:
        """
        Interactive task suggestion workflow
        
        Args:
            task_manager: TaskManager instance
        
        Returns:
            True if tasks were added successfully
        """
        print("\n🤖 AI Task Suggester")
        print("=" * 50)
        
        if not self.ai_suggester.is_available():
            print("⚠️  AI features not available. Please set OPENAI_API_KEY environment variable.")
            print("    You can still add tasks manually.")
            return False
        
        print("📝 Tell me what you want to accomplish today.")
        print("   (e.g., 'I need to prepare for exams and workout')")
        user_input = input("\nYour plan: ").strip()
        
        if not user_input:
            print("❌ No input provided.")
            return False
        
        print("\n⏳ Generating suggestions...")
        suggestions = self.ai_suggester.generate_task_suggestions(user_input, max_suggestions=5)
        
        print("\n✨ Here are your suggested tasks:\n")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion['title']}")
            print(f"   Priority: {suggestion.get('priority', 'medium')}")
        
        print("\n📋 Would you like to add these tasks? (yes/no)")
        choice = input("Your choice: ").strip().lower()
        
        if choice in ["yes", "y"]:
            added_count = 0
            for suggestion in suggestions:
                title = suggestion['title']
                category = self.ai_suggester.categorize_task_ai(title)
                if task_manager.add_task(title, category):
                    added_count += 1
            
            print(f"\n✅ Added {added_count} tasks successfully!")
            return True
        
        return False
    
    def add_task_with_auto_category(self, task_manager, title: str) -> bool:
        """
        Add a task with automatic categorization
        
        Args:
            task_manager: TaskManager instance
            title: Task title
        
        Returns:
            True if task was added successfully
        """
        if not title or not title.strip():
            print("❌ Task title cannot be empty!")
            return False
        
        category = self.ai_suggester.categorize_task_ai(title)
        print(f"🔍 Auto-categorized as: {category}")
        
        return task_manager.add_task(title, category)


# Example usage
if __name__ == "__main__":
    print("🤖 AI Integration Module")
    print("=" * 50)
    
    # Initialize AI Suggester
    suggester = AITaskSuggester()
    
    if suggester.is_available():
        print("✅ OpenAI API is available!")
        
        # Test suggestions
        print("\n📝 Generating task suggestions...")
        suggestions = suggester.generate_task_suggestions("میں نے اپنی تعلیم پر توجہ دینی ہے")
        
        print("\n✨ Suggestions:")
        for i, task in enumerate(suggestions, 1):
            print(f"{i}. {task['title']}")
        
        # Test categorization
        print("\n🔍 Testing auto-categorization:")
        test_tasks = [
            "Prepare for mathematics exam",
            "Attend team meeting",
            "Buy milk and bread",
            "Call mom"
        ]
        
        for task in test_tasks:
            category = suggester.categorize_task_ai(task)
            print(f"  '{task}' → {category}")
    else:
        print("⚠️  OpenAI API not configured.")
        print("   Set OPENAI_API_KEY environment variable to enable AI features.")
