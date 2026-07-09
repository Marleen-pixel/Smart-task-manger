"""
Reminders Module - Professional deadline tracking and alerts
Monitors task deadlines and provides intelligent notifications
With comprehensive validation and error handling
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReminderError(Exception):
    """Raised when reminder operations fail"""
    pass


class ReminderManager:
    """
    Professional reminder manager for task deadlines
    Handles deadline tracking, alerts, and notifications
    """
    
    # Configuration
    DEFAULT_REMINDER_FILE = "reminders.json"
    ALERT_THRESHOLD_HOURS = 24  # Alert if deadline within 24 hours
    DATE_FORMAT = "%Y-%m-%d %H:%M"
    DATE_FORMAT_SHORT = "%Y-%m-%d"
    
    def __init__(self, reminder_file: str = DEFAULT_REMINDER_FILE):
        """
        Initialize reminder manager
        
        Args:
            reminder_file: Path to reminders JSON file
        """
        self.reminder_file = reminder_file
        self.reminders: Dict[str, str] = {}
        self.load_reminders()
        logger.info(f"Reminder manager initialized with file: {reminder_file}")
    
    def load_reminders(self) -> bool:
        """
        Load reminders from JSON file with error handling
        
        Returns:
            True if loaded successfully, False if file doesn't exist or is invalid
        """
        try:
            if os.path.exists(self.reminder_file):
                with open(self.reminder_file, "r") as f:
                    data = json.load(f)
                    
                    if not isinstance(data, dict):
                        logger.warning("Invalid reminders file format")
                        self.reminders = {}
                        return False
                    
                    self.reminders = data
                    logger.info(f"Loaded {len(self.reminders)} reminders")
                    return True
            else:
                logger.info("Reminders file does not exist yet")
                self.reminders = {}
                return True
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in reminders file: {e}")
            self.reminders = {}
            return False
        except IOError as e:
            logger.error(f"Error reading reminders file: {e}")
            self.reminders = {}
            return False
    
    def save_reminders(self) -> bool:
        """
        Save reminders to JSON file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.reminder_file, "w") as f:
                json.dump(self.reminders, f, indent=2)
            logger.info(f"Saved {len(self.reminders)} reminders")
            return True
        except IOError as e:
            logger.error(f"Error saving reminders: {e}")
            return False
    
    def set_deadline(self, task_id: int, deadline: str) -> bool:
        """
        Set a deadline for a task with validation
        
        Args:
            task_id: The task ID
            deadline: Deadline string "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"
            
        Returns:
            True if deadline set successfully, False otherwise
        """
        try:
            # Validate task_id
            if not isinstance(task_id, int) or task_id < 1:
                logger.warning(f"Invalid task ID: {task_id}")
                print("❌ Invalid task ID. Must be a positive number.")
                return False
            
            # Parse and validate deadline
            deadline_obj = self._parse_deadline(deadline)
            if not deadline_obj:
                return False
            
            # Check if deadline is in the past
            if deadline_obj < datetime.now():
                logger.warning(f"Deadline in the past: {deadline}")
                print("⚠️  Warning: Deadline is in the past!")
            
            # Store with standardized format
            self.reminders[str(task_id)] = deadline_obj.strftime(self.DATE_FORMAT)
            logger.info(f"Deadline set for task {task_id}: {deadline}")
            
            return self.save_reminders()
            
        except Exception as e:
            logger.error(f"Error setting deadline: {e}")
            print(f"❌ Error setting deadline: {e}")
            return False
    
    def remove_deadline(self, task_id: int) -> bool:
        """
        Remove deadline for a task
        
        Args:
            task_id: The task ID
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            if str(task_id) not in self.reminders:
                logger.warning(f"No deadline found for task {task_id}")
                print(f"⚠️  No deadline set for task {task_id}")
                return False
            
            del self.reminders[str(task_id)]
            logger.info(f"Deadline removed for task {task_id}")
            return self.save_reminders()
            
        except Exception as e:
            logger.error(f"Error removing deadline: {e}")
            return False
    
    def get_deadline(self, task_id: int) -> Optional[str]:
        """
        Get deadline for a task
        
        Args:
            task_id: The task ID
            
        Returns:
            Deadline string or None if not set
        """
        return self.reminders.get(str(task_id))
    
    def check_alerts(self, tasks: List[Dict]) -> List[Dict]:
        """
        Check for upcoming deadline alerts
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            List of alert dictionaries for upcoming deadlines
        """
        alerts = []
        now = datetime.now()
        
        for task_id_str, deadline_str in self.reminders.items():
            try:
                task_id = int(task_id_str)
                deadline = datetime.strptime(deadline_str, self.DATE_FORMAT)
                
                # Find the task
                task = next((t for t in tasks if t.get("id") == task_id), None)
                if not task:
                    logger.debug(f"Task {task_id} not found for deadline check")
                    continue
                
                # Skip completed tasks
                if task.get("completed"):
                    continue
                
                # Calculate time until deadline
                time_remaining = deadline - now
                
                # Alert if deadline within threshold
                if timedelta(0) <= time_remaining <= timedelta(hours=self.ALERT_THRESHOLD_HOURS):
                    alert = self._create_alert(task, deadline, time_remaining)
                    alerts.append(alert)
                    
            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing deadline for task {task_id_str}: {e}")
                continue
        
        # Sort by urgency (least time remaining first)
        alerts.sort(key=lambda x: x["hours_left"])
        logger.info(f"Found {len(alerts)} deadline alerts")
        
        return alerts
    
    def _parse_deadline(self, deadline: str) -> Optional[datetime]:
        """
        Parse and validate deadline string
        
        Args:
            deadline: Deadline string in format "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"
            
        Returns:
            Datetime object or None if invalid
        """
        if not isinstance(deadline, str):
            logger.warning("Deadline must be a string")
            print("❌ Deadline must be a string")
            return None
        
        deadline = deadline.strip()
        
        try:
            # Try full format first
            if len(deadline.split()) == 2:
                return datetime.strptime(deadline, self.DATE_FORMAT)
            # Try date only format
            elif len(deadline.split()) == 1:
                dt = datetime.strptime(deadline, self.DATE_FORMAT_SHORT)
                return dt.replace(hour=23, minute=59)  # End of day
            else:
                raise ValueError("Invalid format")
                
        except ValueError:
            logger.warning(f"Invalid deadline format: {deadline}")
            print("❌ Invalid date format. Use: YYYY-MM-DD or YYYY-MM-DD HH:MM")
            return None
    
    def _create_alert(self, task: Dict, deadline: datetime, 
                     time_remaining: timedelta) -> Dict:
        """Create alert dictionary"""
        total_seconds = time_remaining.total_seconds()
        hours_left = int(total_seconds / 3600)
        minutes_left = int((total_seconds % 3600) / 60)
        
        return {
            "task_id": task.get("id"),
            "task_title": task.get("title", "Untitled"),
            "category": task.get("category", "General"),
            "deadline": deadline.strftime(self.DATE_FORMAT),
            "hours_left": hours_left,
            "minutes_left": minutes_left,
            "urgency": self._get_urgency_level(hours_left)
        }
    
    def _get_urgency_level(self, hours_left: int) -> str:
        """Determine urgency level based on hours remaining"""
        if hours_left < 1:
            return "🚨 CRITICAL"
        elif hours_left < 3:
            return "🔴 URGENT"
        elif hours_left < 12:
            return "🟠 HIGH"
        else:
            return "🟡 MEDIUM"
    
    def display_alerts(self, tasks: List[Dict]) -> None:
        """Display all current deadline alerts"""
        alerts = self.check_alerts(tasks)
        
        if not alerts:
            print("✅ No upcoming deadlines!")
            logger.info("No deadline alerts to display")
            return
        
        print("\n" + "=" * 75)
        print("⏰ DEADLINE ALERTS")
        print("=" * 75)
        
        for alert in alerts:
            print(f"\n{alert['urgency']} {alert['task_title']}")
            print(f"   📁 Category: {alert['category']}")
            print(f"   📅 Due: {alert['deadline']}")
            print(f"   ⏱️  Time left: {alert['hours_left']}h {alert['minutes_left']}m")
        
        print("\n" + "=" * 75 + "\n")
    
    def view_all_deadlines(self, tasks: List[Dict]) -> None:
        """Display all set deadlines in a formatted table"""
        if not self.reminders:
            print("📭 No deadlines set!")
            logger.info("No deadlines to display")
            return
        
        print("\n" + "=" * 75)
        print("📅 ALL DEADLINES")
        print("=" * 75)
        print(f"{'ID':<4} {'Task':<30} {'Deadline':<20} {'Status':<10}")
        print("=" * 75)
        
        for reminder_id, deadline_str in sorted(self.reminders.items(), 
                                               key=lambda x: x[1]):
            try:
                task_id = int(reminder_id)
                task = next((t for t in tasks if t.get("id") == task_id), None)
                
                if task:
                    status = "✅ Done" if task.get("completed") else "⭕ Pending"
                    task_title = task["title"][:28] + "..." if len(task["title"]) > 28 else task["title"]
                    print(f"{task_id:<4} {task_title:<30} {deadline_str:<20} {status:<10}")
            except (ValueError, AttributeError):
                logger.warning(f"Error displaying deadline {reminder_id}")
                continue
        
        print("=" * 75 + "\n")
    
    def auto_check_and_alert(self, tasks: List[Dict]) -> None:
        """Automatically check and display deadline alerts"""
        alerts = self.check_alerts(tasks)
        
        if alerts:
            print("\n" + "🔔 " * 15)
            for alert in alerts[:3]:  # Show top 3 alerts
                print(f"🔔 {alert['urgency']} '{alert['task_title']}' - "
                      f"{alert['hours_left']}h {alert['minutes_left']}m left")
            
            if len(alerts) > 3:
                print(f"🔔 ... and {len(alerts) - 3} more")
            
            print("🔔 " * 15 + "\n")


class CountdownTimer:
    """Countdown timer utility for displaying time remaining"""
    
    @staticmethod
    def get_time_until(deadline_str: str, 
                      date_format: str = "%Y-%m-%d %H:%M") -> Tuple[int, int, int, int]:
        """
        Calculate time remaining until deadline
        
        Args:
            deadline_str: Deadline string
            date_format: Expected date format
            
        Returns:
            Tuple of (days, hours, minutes, seconds)
        """
        try:
            deadline = datetime.strptime(deadline_str, date_format)
            now = datetime.now()
            remaining = deadline - now
            
            if remaining.total_seconds() < 0:
                return (0, 0, 0, 0)
            
            days = remaining.days
            seconds = remaining.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            return (days, hours, minutes, secs)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error parsing deadline: {e}")
            return (0, 0, 0, 0)
    
    @staticmethod
    def format_countdown(days: int, hours: int, minutes: int, seconds: int) -> str:
        """Format countdown as readable string"""
        if days > 0:
            return f"{days}d {hours}h remaining"
        elif hours > 0:
            return f"{hours}h {minutes}m remaining"
        elif minutes > 0:
            return f"{minutes}m {seconds}s remaining"
        else:
            return "Time's up! ⏰"
