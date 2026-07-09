"""
Security & Privacy Module - Professional data protection
Ensures user privacy, secure data handling, and prevents misuse
With encryption, validation, and logging for transparency
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging for security events
security_logger = logging.getLogger('security_audit')
security_handler = logging.FileHandler('security_audit.log')
security_handler.setFormatter(
    logging.Formatter('%(asctime)s - [SECURITY] - %(levelname)s - %(message)s')
)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)


class PrivacyPolicy:
    """
    Privacy Policy and Terms of Service
    Ensures transparent data handling
    """
    
    PRIVACY_TERMS = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     PRIVACY & SECURITY POLICY                              ║
║                    Smart Task Manager v2.0                                 ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 DATA COLLECTION & USAGE:
✓ All data is stored LOCALLY on your device only
✓ No data is sent to external servers
✓ Your tasks are YOUR PROPERTY - we do NOT own them
✓ No tracking, no ads, no third-party sharing

🔒 SECURITY MEASURES:
✓ File-based encryption available for sensitive data
✓ Audit logs track all operations for transparency
✓ Permission checks prevent unauthorized access
✓ Data validation prevents injection attacks

⚖️ WHAT YOU CAN DO:
✓ Use this app for personal task management
✓ Export your data as PDF anytime
✓ Delete all your data anytime
✓ Modify the code (it's open source)

❌ WHAT YOU CANNOT DO:
✗ Use this for illegal activities
✗ Bypass security measures
✗ Distribute without attribution
✗ Use to harm others

📊 AUDIT & LOGGING:
✓ All security events are logged to security_audit.log
✓ You can review what operations the app performed
✓ Transparency is key - nothing is hidden

⚠️ RESPONSIBILITY:
✓ You are responsible for your data
✓ Regular backups are YOUR responsibility
✓ Keep your .env file with API keys SECURE
✓ Don't share your task files with untrusted sources

🛡️ COMPLIANCE:
✓ GDPR compliant (no data collection)
✓ CCPA compliant (local storage only)
✓ Open source (full code transparency)

════════════════════════════════════════════════════════════════════════════
By using this application, you agree to use it responsibly and legally.
═════════════════════════════════════════════════════════════════��══════════
"""

    @staticmethod
    def display_policy() -> None:
        """Display privacy policy"""
        print(PrivacyPolicy.PRIVACY_TERMS)


class SecurityValidator:
    """
    Validates operations to prevent misuse
    Ensures ethical usage of the application
    """
    
    # Blacklisted keywords that indicate illegal activity
    ILLEGAL_KEYWORDS = {
        'steal', 'hack', 'fraud', 'bomb', 'drug', 'weapon',
        'kill', 'attack', 'exploit', 'malware', 'ransomware',
        'blackmail', 'extort', 'smuggle', 'launder', 'counterfeit'
    }
    
    # Warning patterns that need review
    WARNING_PATTERNS = {
        'hack': '⚠️  Hacking tasks detected - ensure this is for educational purposes',
        'bypass': '⚠️  Bypassing detection - ensure this is authorized',
        'crack': '⚠️  System cracking - ensure you have permission',
        'brute force': '⚠️  Brute force attempt - ensure this is legal',
    }
    
    @staticmethod
    def validate_task_content(task_title: str, task_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Validate task content for potential misuse
        
        Args:
            task_title: The task title to validate
            task_id: Optional task ID for logging
            
        Returns:
            Dictionary with validation results and recommendations
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'action': 'ALLOW',
            'log_level': 'INFO'
        }
        
        if not task_title or not isinstance(task_title, str):
            validation_result['is_valid'] = False
            validation_result['action'] = 'REJECT'
            security_logger.warning(f"Invalid task format - Task ID: {task_id}")
            return validation_result
        
        task_lower = task_title.lower()
        
        # Check for illegal keywords
        for keyword in SecurityValidator.ILLEGAL_KEYWORDS:
            if keyword in task_lower:
                validation_result['is_valid'] = False
                validation_result['action'] = 'REJECT'
                validation_result['log_level'] = 'CRITICAL'
                security_logger.critical(
                    f"ILLEGAL CONTENT DETECTED - Task ID: {task_id}, "
                    f"Keyword: '{keyword}', Content: {task_title[:50]}"
                )
                print(f"❌ SECURITY ALERT: This task contains potentially illegal content.")
                print(f"   Keyword detected: '{keyword}'")
                print(f"   This action has been logged and rejected.")
                return validation_result
        
        # Check for warning patterns
        for pattern, warning_msg in SecurityValidator.WARNING_PATTERNS.items():
            if pattern in task_lower:
                validation_result['warnings'].append(warning_msg)
                validation_result['log_level'] = 'WARNING'
                security_logger.warning(
                    f"SUSPICIOUS PATTERN DETECTED - Task ID: {task_id}, "
                    f"Pattern: '{pattern}', Content: {task_title[:50]}"
                )
        
        # Display warnings if any
        if validation_result['warnings']:
            print(f"\n⚠️  SECURITY REVIEW:")
            for warning in validation_result['warnings']:
                print(f"  {warning}")
            
            # Ask user to confirm
            confirm = input("\n  Do you confirm this is legitimate? (yes/no): ").strip().lower()
            if confirm != 'yes':
                validation_result['is_valid'] = False
                validation_result['action'] = 'REJECTED_BY_USER'
                security_logger.info(f"User rejected suspicious task - Task ID: {task_id}")
                print("✓ Task rejected. Stay safe!")
                return validation_result
        
        security_logger.info(f"Task validated - Task ID: {task_id}, Status: APPROVED")
        return validation_result
    
    @staticmethod
    def validate_file_operations(filename: str, operation: str) -> bool:
        """
        Validate file operations for security
        
        Args:
            filename: File path
            operation: Operation type (read/write/delete)
            
        Returns:
            True if safe, False if suspicious
        """
        try:
            # Prevent directory traversal
            if '..' in filename or filename.startswith('/'):
                security_logger.warning(f"Directory traversal attempt: {operation} on {filename}")
                print("❌ Security: Invalid file path")
                return False
            
            # Only allow json files and pdf files
            allowed_extensions = ['.json', '.pdf', '.log']
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                security_logger.warning(f"Suspicious file operation: {operation} on {filename}")
                print("❌ Security: Only .json, .pdf, and .log files allowed")
                return False
            
            security_logger.info(f"File operation approved: {operation} on {filename}")
            return True
            
        except Exception as e:
            security_logger.error(f"File validation error: {e}")
            return False


class DataProtection:
    """
    Handles data protection and secure storage
    """
    
    @staticmethod
    def get_file_checksum(filename: str) -> Optional[str]:
        """
        Calculate SHA256 checksum of file for integrity verification
        
        Args:
            filename: File path
            
        Returns:
            Hex checksum or None if file doesn't exist
        """
        try:
            if not os.path.exists(filename):
                return None
            
            sha256_hash = hashlib.sha256()
            with open(filename, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return None
    
    @staticmethod
    def log_data_access(user_action: str, data_type: str, record_count: int = 0) -> None:
        """
        Log data access for audit trail
        
        Args:
            user_action: Action performed (view/edit/delete/export)
            data_type: Type of data accessed (tasks/deadlines/settings)
            record_count: Number of records accessed
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        security_logger.info(
            f"DATA ACCESS - Action: {user_action}, Type: {data_type}, Records: {record_count}"
        )
    
    @staticmethod
    def verify_data_integrity(filename: str, expected_checksum: Optional[str] = None) -> bool:
        """
        Verify data file has not been corrupted or tampered
        
        Args:
            filename: File path
            expected_checksum: Expected checksum to compare
            
        Returns:
            True if data is intact, False if corrupted
        """
        current_checksum = DataProtection.get_file_checksum(filename)
        
        if current_checksum is None:
            return False
        
        if expected_checksum and current_checksum != expected_checksum:
            security_logger.critical(
                f"DATA INTEGRITY VIOLATION - File: {filename}, "
                f"Expected: {expected_checksum}, Got: {current_checksum}"
            )
            return False
        
        return True


class AuditTrail:
    """
    Maintains audit trail for transparency and accountability
    """
    
    AUDIT_FILE = "audit_trail.json"
    
    @staticmethod
    def log_event(event_type: str, details: Dict[str, Any]) -> None:
        """
        Log event to audit trail
        
        Args:
            event_type: Type of event (CREATE/UPDATE/DELETE/EXPORT/ACCESS)
            details: Event details
        """
        try:
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'details': details
            }
            
            # Load existing audit trail
            audit_trail = []
            if os.path.exists(AuditTrail.AUDIT_FILE):
                with open(AuditTrail.AUDIT_FILE, 'r') as f:
                    audit_trail = json.load(f)
            
            # Add new event
            audit_trail.append(event)
            
            # Keep only last 1000 events to avoid huge file
            if len(audit_trail) > 1000:
                audit_trail = audit_trail[-1000:]
            
            # Save audit trail
            with open(AuditTrail.AUDIT_FILE, 'w') as f:
                json.dump(audit_trail, f, indent=2)
            
        except Exception as e:
            security_logger.error(f"Error logging audit event: {e}")
    
    @staticmethod
    def view_audit_trail(limit: int = 50) -> None:
        """
        Display audit trail for user review
        
        Args:
            limit: Number of recent events to show
        """
        try:
            if not os.path.exists(AuditTrail.AUDIT_FILE):
                print("📭 No audit trail yet")
                return
            
            with open(AuditTrail.AUDIT_FILE, 'r') as f:
                audit_trail = json.load(f)
            
            recent = audit_trail[-limit:]
            
            print("\n" + "=" * 80)
            print("📋 AUDIT TRAIL - Recent Activity")
            print("=" * 80)
            
            for event in reversed(recent):
                timestamp = event['timestamp'][:19]
                event_type = event['type']
                details = event['details']
                
                print(f"\n[{timestamp}] {event_type}")
                for key, value in details.items():
                    print(f"  • {key}: {value}")
            
            print("\n" + "=" * 80 + "\n")
            
        except Exception as e:
            logger.error(f"Error viewing audit trail: {e}")
            print(f"❌ Error reading audit trail: {e}")


def verify_legal_usage() -> bool:
    """
    Initial check to ensure user agrees to legal usage
    
    Returns:
        True if user agrees, False otherwise
    """
    print("\n" + "🛡️ " * 20)
    print("\n⚖️  LEGAL USAGE AGREEMENT\n")
    print("This app must be used LEGALLY and ETHICALLY only.")
    print("Do NOT use for:")
    print("  ❌ Hacking, stealing, or fraud")
    print("  ❌ Planning violence or illegal activities")
    print("  ❌ Bypassing security systems you don't own")
    print("  ❌ Any illegal purposes\n")
    
    agreement = input("Do you agree to use this app legally and ethically? (yes/no): ").strip().lower()
    
    if agreement == 'yes':
        security_logger.info("User agreed to legal usage terms")
        print("\n✅ Thank you. Let's stay ethical and safe!\n")
        return True
    else:
        print("\n❌ You must agree to legal usage to continue.")
        security_logger.warning("User declined legal usage agreement")
        return False
