#!/usr/bin/env python3
"""
Screenshot Taker - A tool to capture screenshots at regular intervals
"""

import os
import time
import datetime
from pathlib import Path
import pyautogui

class ScreenshotTaker:
    def __init__(self, output_dir="screenshots", interval=10):
        """
        Initialize the screenshot taker
        
        Args:
            output_dir (str): Directory to save screenshots
            interval (int): Time between screenshots in seconds
        """
        self.output_dir = output_dir
        self.interval = interval
        self.counter = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Screenshots will be saved to: {os.path.abspath(self.output_dir)}")
        
    def take_screenshot(self):
        """Take a screenshot and save it with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_{self.counter}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        self.counter += 1
        print(f"Screenshot #{self.counter} saved: {filename}")
        return filepath
        
    def run(self):
        """Run the screenshot taker at regular intervals"""
        print(f"Starting screenshot capture every {self.interval} seconds.")
        print("Press Ctrl+C to stop.")
        
        try:
            while True:
                self.take_screenshot()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nScreenshot capture stopped.")
            print(f"Total screenshots taken: {self.counter}")


if __name__ == "__main__":
    # Create and run the screenshot taker
    screenshot_taker = ScreenshotTaker()
    screenshot_taker.run() 