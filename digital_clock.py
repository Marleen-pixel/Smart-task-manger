"""
Digital Clock with Multi-Timezone Support
Display current time in different time zones with a beautiful CLI interface
"""

import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict
import os
import sys


class DigitalClock:
    """A digital clock that displays time in multiple time zones"""
    
    # Popular timezones
    DEFAULT_TIMEZONES = {
        "UTC": "UTC",
        "EST": "America/New_York",
        "CST": "America/Chicago",
        "MST": "America/Denver",
        "PST": "America/Los_Angeles",
        "GMT": "Europe/London",
        "CET": "Europe/Paris",
        "IST": "Asia/Kolkata",
        "JST": "Asia/Tokyo",
        "AEST": "Australia/Sydney",
        "NZST": "Pacific/Auckland",
    }
    
    def __init__(self):
        """Initialize the digital clock"""
        self.selected_zones: List[str] = ["UTC"]
        self.running = True
    
    def add_timezone(self, zone_name: str) -> bool:
        """Add a timezone to display"""
        try:
            if zone_name in self.selected_zones:
                print(f"⚠️  '{zone_name}' is already being displayed!")
                return False
            
            # Verify the timezone exists
            ZoneInfo(zone_name)
            self.selected_zones.append(zone_name)
            print(f"✅ Added timezone: {zone_name}")
            return True
        except Exception as e:
            print(f"❌ Error: Invalid timezone '{zone_name}'")
            return False
    
    def remove_timezone(self, zone_name: str) -> bool:
        """Remove a timezone from display"""
        if zone_name not in self.selected_zones:
            print(f"❌ Timezone '{zone_name}' is not in the display list!")
            return False
        
        if len(self.selected_zones) == 1:
            print("❌ You must keep at least one timezone!")
            return False
        
        self.selected_zones.remove(zone_name)
        print(f"✅ Removed timezone: {zone_name}")
        return True
    
    def get_time_in_zone(self, zone_name: str) -> str:
        """Get formatted time for a specific timezone"""
        try:
            tz = ZoneInfo(zone_name)
            now = datetime.now(tz)
            return now.strftime("%H:%M:%S")
        except Exception:
            return "ERROR"
    
    def get_date_in_zone(self, zone_name: str) -> str:
        """Get formatted date for a specific timezone"""
        try:
            tz = ZoneInfo(zone_name)
            now = datetime.now(tz)
            return now.strftime("%Y-%m-%d")
        except Exception:
            return "ERROR"
    
    def get_timezone_offset(self, zone_name: str) -> str:
        """Get UTC offset for a timezone"""
        try:
            tz = ZoneInfo(zone_name)
            now = datetime.now(tz)
            offset = now.strftime("%z")
            return f"{offset[:3]}:{offset[3:]}"
        except Exception:
            return "ERROR"
    
    def display_clock(self) -> None:
        """Display the digital clock with all selected timezones"""
        self.clear_screen()
        
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "🕐 DIGITAL CLOCK - MULTI TIMEZONE 🕐" + " " * 22 + "║")
        print("╚" + "═" * 78 + "╝\n")
        
        # Display each timezone
        for idx, zone in enumerate(self.selected_zones, 1):
            time_str = self.get_time_in_zone(zone)
            date_str = self.get_date_in_zone(zone)
            offset = self.get_timezone_offset(zone)
            
            print(f"  {idx}. {zone:20} | 🕐 {time_str}  📅 {date_str}  UTC{offset}")
        
        print("\n" + "─" * 80)
    
    def display_menu(self) -> None:
        """Display the control menu"""
        print("\nCommands:")
        print("  [add]      - Add a new timezone")
        print("  [remove]   - Remove a timezone")
        print("  [list]     - List all available timezones")
        print("  [preset]   - Show preset timezones")
        print("  [clear]    - Clear screen")
        print("  [help]     - Show this menu")
        print("  [exit]     - Exit the application\n")
    
    def list_all_timezones(self) -> None:
        """List all available timezones"""
        try:
            from zoneinfo import available_timezones
            zones = sorted(available_timezones())
            
            print(f"\n📍 Available Timezones ({len(zones)} total):\n")
            for i, zone in enumerate(zones, 1):
                if i % 3 == 0:
                    print(f"{zone:<30}")
                else:
                    print(f"{zone:<30}", end="")
            print("\n")
        except Exception as e:
            print(f"❌ Error listing timezones: {e}")
    
    def show_preset_timezones(self) -> None:
        """Show preset timezone options"""
        print("\n📍 Preset Timezones:\n")
        for abbr, zone in sorted(self.DEFAULT_TIMEZONES.items()):
            print(f"  {abbr:6} → {zone}")
        print()
    
    def clear_screen(self) -> None:
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def run_live_clock(self, duration: int = 10) -> None:
        """Run a live updating clock for specified seconds"""
        print(f"\n⏱️  Live clock mode (updates every 1 second, runs for {duration}s)...")
        print("Press Ctrl+C to exit early.\n")
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                self.display_clock()
                print("[Press Ctrl+C to stop]")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Live clock stopped.")
    
    def run(self) -> None:
        """Main application loop"""
        print("\n👋 Welcome to Digital Clock with Multi-Timezone Support!")
        print("Type 'help' to see all commands.\n")
        
        while self.running:
            try:
                self.display_clock()
                command = input("Enter command: ").strip().lower()
                
                if command == "add":
                    self.show_preset_timezones()
                    zone = input("Enter timezone name (e.g., 'Asia/Tokyo'): ").strip()
                    if zone:
                        self.add_timezone(zone)
                
                elif command == "remove":
                    if len(self.selected_zones) == 1:
                        print("❌ You must keep at least one timezone!")
                        continue
                    
                    zone = input("Enter timezone to remove: ").strip()
                    self.remove_timezone(zone)
                
                elif command == "list":
                    self.list_all_timezones()
                
                elif command == "preset":
                    self.show_preset_timezones()
                
                elif command == "clear":
                    self.clear_screen()
                
                elif command == "live":
                    duration = input("Enter duration in seconds (default 10): ").strip()
                    try:
                        duration = int(duration) if duration else 10
                        self.run_live_clock(duration)
                    except ValueError:
                        print("❌ Please enter a valid number")
                
                elif command == "help":
                    self.display_menu()
                
                elif command == "exit":
                    print("\n👋 Goodbye! Stay on time! ⏰\n")
                    self.running = False
                
                else:
                    print("❌ Invalid command! Type 'help' for available commands.")
                
                if self.running:
                    input("Press Enter to continue...")
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Application interrupted.")
                self.running = False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                input("Press Enter to continue...")


def main():
    """Entry point of the application"""
    clock = DigitalClock()
    clock.run()


if __name__ == "__main__":
    main()
