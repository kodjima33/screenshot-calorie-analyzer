#!/usr/bin/env python3
"""
Screenshot with Gemini - Takes screenshots and analyzes them for calorie content using Gemini 2.0 Flash
"""

import os
import time
import datetime
import argparse
import threading
import signal
import sys
from pathlib import Path

# Import from our other modules
from screenshot_taker import ScreenshotTaker
from gemini_calorie_analyzer import GeminiCalorieAnalyzer, print_calorie_report

class ScreenshotWithGemini:
    def __init__(self, output_dir="screenshots", interval=10, analysis_interval=60, api_key=None):
        """
        Initialize the combined screenshot and Gemini analyzer
        
        Args:
            output_dir (str): Directory to save screenshots
            interval (int): Time between screenshots in seconds
            analysis_interval (int): Time between calorie analyses in seconds
            api_key (str): API key for Gemini model
        """
        self.output_dir = output_dir
        self.interval = interval
        self.analysis_interval = analysis_interval
        self.api_key = api_key
        
        if not api_key:
            raise ValueError("API key is required for Gemini API")
            
        self.screenshot_taker = ScreenshotTaker(output_dir=output_dir, interval=interval)
        self.analyzer = GeminiCalorieAnalyzer(screenshots_dir=output_dir, api_key=api_key)
        self.stop_event = threading.Event()
        self.screenshot_thread = None
        self.analysis_thread = None
    
    def start_screenshot_thread(self):
        """Start the screenshot taking thread"""
        def take_screenshots():
            print(f"Starting screenshot capture every {self.interval} seconds.")
            while not self.stop_event.is_set():
                self.screenshot_taker.take_screenshot()
                # Sleep until next interval or until stop is requested
                self.stop_event.wait(self.interval)
        
        self.screenshot_thread = threading.Thread(target=take_screenshots)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
    
    def start_analysis_thread(self):
        """Start the Gemini-powered calorie analysis thread"""
        def analyze_periodically():
            print(f"Gemini 2.0 Flash calorie analysis will run every {self.analysis_interval} seconds.")
            
            # Wait for first interval before starting analysis
            if not self.stop_event.wait(self.analysis_interval):
                while not self.stop_event.is_set():
                    print("\n--- Running Gemini 2.0 Flash calorie analysis ---")
                    
                    # Get analysis results (now with immediate per-image calorie printing)
                    results = self.analyzer.analyze_all_screenshots()
                    
                    # Just print the summary report
                    if results:
                        total_calories = sum(r['calories'] for r in results)
                        food_images = sum(1 for r in results if r['calories'] > 0)
                        
                        print("\n===== CALORIE ANALYSIS SUMMARY =====")
                        print(f"Total screenshots analyzed: {len(results)}")
                        print(f"Screenshots containing food: {food_images}")
                        print(f"Estimated total calories: {total_calories}")
                        print("===================================")
                    
                    # Sleep until next interval or until stop is requested
                    self.stop_event.wait(self.analysis_interval)
        
        self.analysis_thread = threading.Thread(target=analyze_periodically)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def run(self):
        """Run both screenshot capturing and Gemini analysis"""
        # Set up signal handling for graceful shutdown
        def signal_handler(sig, frame):
            print("\nStopping all processes...")
            self.stop_event.set()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Screenshots will be saved to: {os.path.abspath(self.output_dir)}")
        
        # Start both threads
        self.start_screenshot_thread()
        self.start_analysis_thread()
        
        print("Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop_event.set()
            sys.exit(0)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Screenshot Taker with Gemini Calorie Analysis')
    
    parser.add_argument('-d', '--directory', type=str, default='screenshots',
                        help='Directory to save screenshots (default: screenshots)')
    
    parser.add_argument('-i', '--interval', type=int, default=10,
                        help='Time between screenshots in seconds (default: 10)')
    
    parser.add_argument('-a', '--analysis-interval', type=int, default=60,
                        help='Time between calorie analyses in seconds (default: 60)')
    
    parser.add_argument('-k', '--api-key', type=str, required=True,
                        help='API key for Gemini model (required)')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Create and run the combined app
    app = ScreenshotWithGemini(
        output_dir=args.directory,
        interval=args.interval,
        analysis_interval=args.analysis_interval,
        api_key=args.api_key
    )
    
    app.run() 