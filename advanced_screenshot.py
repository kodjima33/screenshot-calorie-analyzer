#!/usr/bin/env python3
"""
Advanced Screenshot Taker - A tool to capture screenshots at regular intervals with more features
"""

import os
import time
import datetime
import argparse
import logging
from pathlib import Path
import pyautogui

class AdvancedScreenshotTaker:
    def __init__(self, output_dir="screenshots", interval=10, format="png", prefix="screenshot", 
                 region=None, compress_level=0, log_level="INFO"):
        """
        Initialize the advanced screenshot taker
        
        Args:
            output_dir (str): Directory to save screenshots
            interval (int): Time between screenshots in seconds
            format (str): Image format (png, jpg, etc.)
            prefix (str): Prefix for screenshot filenames
            region (tuple): Region to capture (left, top, width, height)
            compress_level (int): Compression level (0-9, PNG only)
            log_level (str): Logging level
        """
        self.output_dir = output_dir
        self.interval = interval
        self.format = format.lower()
        self.prefix = prefix
        self.region = region
        self.compress_level = compress_level
        self.counter = 0
        
        # Set up logging
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO
        
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{output_dir}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(f"Screenshots will be saved to: {os.path.abspath(self.output_dir)}")
        
    def take_screenshot(self):
        """Take a screenshot and save it with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.prefix}_{timestamp}_{self.counter}.{self.format}"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if self.region:
                screenshot = pyautogui.screenshot(region=self.region)
            else:
                screenshot = pyautogui.screenshot()
                
            # Save with compression if PNG
            if self.format == 'png' and self.compress_level > 0:
                screenshot.save(filepath, format='PNG', 
                               compress_level=min(self.compress_level, 9))
            else:
                screenshot.save(filepath)
            
            self.counter += 1
            self.logger.info(f"Screenshot #{self.counter} saved: {filename}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None
        
    def run(self):
        """Run the screenshot taker at regular intervals"""
        self.logger.info(f"Starting screenshot capture every {self.interval} seconds.")
        self.logger.info("Press Ctrl+C to stop.")
        
        try:
            start_time = time.time()
            while True:
                self.take_screenshot()
                
                # Calculate sleep time to maintain consistent interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval - (elapsed % self.interval))
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("\nScreenshot capture stopped.")
            self.logger.info(f"Total screenshots taken: {self.counter}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Advanced Screenshot Taker')
    
    parser.add_argument('-d', '--directory', type=str, default='screenshots',
                        help='Directory to save screenshots (default: screenshots)')
    
    parser.add_argument('-i', '--interval', type=float, default=10,
                        help='Time between screenshots in seconds (default: 10)')
    
    parser.add_argument('-f', '--format', type=str, default='png', choices=['png', 'jpg', 'jpeg', 'bmp'],
                        help='Image format (default: png)')
    
    parser.add_argument('-p', '--prefix', type=str, default='screenshot',
                        help='Prefix for screenshot filenames (default: screenshot)')
    
    parser.add_argument('-r', '--region', type=str,
                        help='Region to capture (format: left,top,width,height)')
    
    parser.add_argument('-c', '--compress', type=int, default=0,
                        help='Compression level 0-9, PNG only (default: 0)')
    
    parser.add_argument('-l', '--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level (default: INFO)')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Parse region if provided
    region = None
    if args.region:
        try:
            region = tuple(map(int, args.region.split(',')))
            if len(region) != 4:
                raise ValueError("Region must have 4 values: left,top,width,height")
        except Exception as e:
            print(f"Error parsing region: {str(e)}")
            print("Using full screen instead.")
    
    # Create and run the screenshot taker
    screenshot_taker = AdvancedScreenshotTaker(
        output_dir=args.directory,
        interval=args.interval,
        format=args.format,
        prefix=args.prefix,
        region=region,
        compress_level=args.compress,
        log_level=args.log_level
    )
    
    screenshot_taker.run() 