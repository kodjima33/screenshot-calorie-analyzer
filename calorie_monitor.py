#!/usr/bin/env python3
"""
Calorie Monitor - A single script that takes screenshots and analyzes them for calorie content using Gemini 2.0 Flash
"""

import os
import time
import datetime
import argparse
import signal
import sys
import base64
import json
import re
from pathlib import Path
from PIL import Image
import pyautogui
import google.generativeai as genai
from dotenv import load_dotenv

# For macOS notifications
try:
    import pync
    NOTIFICATIONS_ENABLED = True
    print("pync installed. macOS notifications enabled.")
except ImportError:
    print("pync not installed. macOS notifications will be disabled.")
    print("Install with: pip install pync")
    NOTIFICATIONS_ENABLED = False

# Load environment variables from .env file
load_dotenv()

class CalorieMonitor:
    def __init__(self, output_dir="screenshots", interval=10, api_key=None, screen_half="left"):
        """
        Initialize the calorie monitor
        
        Args:
            output_dir (str): Directory to save screenshots
            interval (int): Time between screenshots in seconds
            api_key (str): API key for Gemini model (if None, will try to use GEMINI_API_KEY from .env)
            screen_half (str): Which half of screen to capture ('left' or 'right')
        """
        self.output_dir = output_dir
        self.interval = interval
        self.counter = 0
        self.screen_half = screen_half.lower()
        
        if self.screen_half not in ['left', 'right']:
            print(f"Invalid screen half '{screen_half}'. Using 'left' as default.")
            self.screen_half = 'left'
        
        # Get API key from argument or environment variable
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        # Validate API key
        if not self.api_key:
            raise ValueError("API key is required. Either provide it with -k/--api-key or set GEMINI_API_KEY in .env file")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.0 Flash model for image analysis
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Screenshots will be saved to: {os.path.abspath(self.output_dir)}")
        print(f"Capturing the {self.screen_half} half of the screen")
        
        # Notify that the application has started
        if NOTIFICATIONS_ENABLED:
            # Try both notification methods
            show_notification(
                "Calorie Monitor Started",
                "Taking screenshots and analyzing for food"
            )
    
    def take_screenshot(self):
        """Take a screenshot of half of the screen and save it with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_{self.counter}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        half_width = screen_width // 2
        
        # Capture the specified half of the screen
        # The region parameter is (left, top, width, height)
        if self.screen_half == 'left':
            screenshot = pyautogui.screenshot(region=(0, 0, half_width, screen_height))
        else:  # right half
            screenshot = pyautogui.screenshot(region=(half_width, 0, half_width, screen_height))
            
        screenshot.save(filepath)
        
        self.counter += 1
        print(f"Screenshot #{self.counter} saved: {filename} ({self.screen_half} half of screen)")
        return filepath
    
    def analyze_screenshot(self, screenshot_path):
        """
        Analyze a screenshot for food items and calories using Gemini
        """
        try:
            print(f"Analyzing {os.path.basename(screenshot_path)}...")
            
            # Open the image
            img = Image.open(screenshot_path)
            
            # Create a prompt for Gemini
            prompt = """
            Analyze this image and identify any food items present. 
            If food is detected, provide:
            1. A list of each distinct food item
            2. Estimated calories for each item
            3. Total calories
            
            Output in JSON format like this:
            {
                "food_detected": true/false,
                "food_items": [
                    {"name": "item1", "calories": 123},
                    {"name": "item2", "calories": 456}
                ],
                "total_calories": 579
            }
            
            If no food is detected, simply return:
            {
                "food_detected": false,
                "food_items": [],
                "total_calories": 0
            }
            """
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, img])
            result_text = response.text
            
            # Try to extract JSON from response
            json_match = re.search(r'{.*}', result_text, re.DOTALL)
            if json_match:
                result_json = json.loads(json_match.group(0))
            else:
                # Fallback if no JSON pattern found
                result_json = {
                    "food_detected": False,
                    "food_items": [],
                    "total_calories": 0
                }
            
            # Process the result
            if result_json.get("food_detected", False):
                food_items = result_json.get("food_items", [])
                total_calories = result_json.get("total_calories", 0)
                food_names = [item["name"] for item in food_items]
                
                # Print result immediately
                foods_str = ", ".join(food_names)
                print(f"✓ {os.path.basename(screenshot_path)}: {total_calories} calories")
                print(f"  Detected items: {foods_str}")
                
                # Send notification for food detection
                if NOTIFICATIONS_ENABLED:
                    subtitle = foods_str[:50] + ("..." if len(foods_str) > 50 else "")
                    show_notification(
                        "Food Detected!",
                        f"{total_calories} calories detected",
                        subtitle
                    )
                
                # Print detailed item breakdown
                for item in food_items:
                    print(f"    - {item['name']}: {item['calories']} calories")
                
                return {
                    'filename': os.path.basename(screenshot_path),
                    'calories': total_calories,
                    'food_items': food_names,
                    'detailed_items': food_items,
                    'status': 'success'
                }
            else:
                print(f"✓ {os.path.basename(screenshot_path)}: No food detected (0 calories)")
                
                # Optionally notify about no food detection
                # Uncomment if you want notifications even when no food is found
                # if NOTIFICATIONS_ENABLED:
                #     pync.notify(
                #         "No food detected in screenshot",
                #         title="Calorie Monitor",
                #         sound=None
                #     )
                
                return {
                    'filename': os.path.basename(screenshot_path),
                    'calories': 0,
                    'food_items': [],
                    'detailed_items': [],
                    'status': 'success'
                }
                
        except Exception as e:
            print(f"Error processing {screenshot_path}: {str(e)}")
            
            # Notify about error
            if NOTIFICATIONS_ENABLED:
                show_notification(
                    "Calorie Monitor Error",
                    f"Error: {str(e)[:50]}..."
                )
                
            return {
                'filename': os.path.basename(screenshot_path),
                'calories': 0,
                'food_items': [],
                'detailed_items': [],
                'status': 'error',
                'error': str(e)
            }
    
    def run(self):
        """Run the calorie monitor"""
        print(f"Starting Calorie Monitor with Gemini 2.0 Flash")
        print(f"Taking screenshots every {self.interval} seconds")
        print("Press Ctrl+C to stop.")
        
        # Set up signal handling for graceful shutdown
        def signal_handler(sig, frame):
            print("\nStopping Calorie Monitor...")
            print(f"Total screenshots taken: {self.counter}")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while True:
                # Take a screenshot
                screenshot_path = self.take_screenshot()
                
                # Analyze the screenshot immediately
                self.analyze_screenshot(screenshot_path)
                
                # Wait for the next interval
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nCalorie Monitor stopped.")
            print(f"Total screenshots taken: {self.counter}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Calorie Monitor - Screenshots with Gemini 2.0 Flash Analysis')
    
    parser.add_argument('-d', '--directory', type=str, default='screenshots',
                        help='Directory to save screenshots (default: screenshots)')
    
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help='Time between screenshots in seconds (default: 10)')
    
    parser.add_argument('-k', '--api-key', type=str, required=False,
                        help='API key for Gemini model (optional if set in .env file)')
    
    parser.add_argument('-s', '--screen-half', type=str, default='left',
                        help='Which half of screen to capture (left or right, default: left)')
    
    return parser.parse_args()

# Fallback notification using AppleScript
def show_notification(title, message, subtitle=None):
    """Show a macOS notification using either pync or AppleScript as fallback"""
    if NOTIFICATIONS_ENABLED:
        try:
            if subtitle:
                pync.notify(message, title=title, subtitle=subtitle, sound="Ping")
            else:
                pync.notify(message, title=title, sound="Ping")
            print(f"Sent notification: {title} - {message}")
            return True
        except Exception as e:
            print(f"pync notification failed: {e}")
    
    # Fallback to AppleScript
    try:
        subtitle_str = f'subtitle "{subtitle}"' if subtitle else ""
        script = f'''
        osascript -e 'display notification "{message}" with title "{title}" {subtitle_str}'
        '''
        os.system(script)
        print(f"Sent AppleScript notification: {title} - {message}")
        return True
    except Exception as e:
        print(f"AppleScript notification failed: {e}")
        return False

if __name__ == "__main__":
    args = parse_arguments()
    
    # Create and run the calorie monitor
    monitor = CalorieMonitor(
        output_dir=args.directory,
        interval=args.interval,
        api_key=args.api_key,
        screen_half=args.screen_half
    )
    
    monitor.run() 