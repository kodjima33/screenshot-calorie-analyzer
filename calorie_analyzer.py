#!/usr/bin/env python3
"""
Calorie Analyzer - Analyzes screenshots to detect food items and estimate calories
"""

import os
import glob
import argparse
from PIL import Image
import numpy as np
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import random

class CalorieAnalyzer:
    def __init__(self, screenshots_dir="screenshots", api_key=None):
        """
        Initialize the calorie analyzer
        
        Args:
            screenshots_dir (str): Directory containing screenshots
            api_key (str): API key for image recognition (if needed)
        """
        self.screenshots_dir = screenshots_dir
        self.api_key = api_key
        
        # Check if the directory exists
        if not os.path.exists(screenshots_dir):
            raise ValueError(f"Screenshots directory '{screenshots_dir}' does not exist")
    
    def get_screenshots(self):
        """Get all screenshots in the directory"""
        # Find all image files in the directory
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp']
        screenshot_files = []
        
        for ext in image_extensions:
            pattern = os.path.join(self.screenshots_dir, ext)
            screenshot_files.extend(glob.glob(pattern))
        
        return sorted(screenshot_files)
    
    def analyze_screenshot(self, screenshot_path):
        """
        Analyze a single screenshot for food items and calories
        Using a simple AI-like analysis for demo purposes
        """
        try:
            # Use image analysis to detect potential food
            calories, food_items = self._analyze_for_food(screenshot_path)
            return {
                'filename': os.path.basename(screenshot_path),
                'calories': calories,
                'food_items': food_items,
                'status': 'success'
            }
        except Exception as e:
            return {
                'filename': os.path.basename(screenshot_path),
                'calories': 0,
                'food_items': [],
                'status': 'error',
                'error': str(e)
            }
    
    def _analyze_for_food(self, image_path):
        """
        Analyze image for food content using image processing techniques
        
        For demonstration purposes this uses a simulated approach
        A real implementation would use computer vision or deep learning models
        """
        try:
            # Open and process image
            img = Image.open(image_path)
            img = img.resize((200, 200))  # Resize for faster processing
            img_array = np.array(img)
            
            # Simple image analysis (not actual food detection)
            # Extract color features (real systems would use CNN-based models)
            r_channel = img_array[:,:,0].mean()
            g_channel = img_array[:,:,1].mean()
            b_channel = img_array[:,:,2].mean()
            
            # Color variation (standard deviation across channels)
            color_variation = np.std([r_channel, g_channel, b_channel])
            
            # Simulate food detection based on image properties
            # For demonstration - a real system would use actual food recognition
            
            # Randomly determine if image contains food (biased toward finding food)
            contains_food = random.random() < 0.7  # 70% chance to detect food
            
            if contains_food:
                # Simulate "detected" food items
                possible_foods = [
                    "sandwich", "salad", "pasta", "fruit", "pizza", 
                    "burger", "coffee", "cake", "bread", "rice",
                    "chicken", "vegetables", "soup", "steak", "fish"
                ]
                
                # "Detect" 1-3 food items
                num_foods = random.randint(1, 3)
                detected_foods = random.sample(possible_foods, num_foods)
                
                # Assign calories based on "detected" foods
                food_calories = {
                    "sandwich": random.randint(300, 500),
                    "salad": random.randint(150, 300),
                    "pasta": random.randint(400, 700),
                    "fruit": random.randint(80, 150),
                    "pizza": random.randint(250, 400),
                    "burger": random.randint(500, 800),
                    "coffee": random.randint(5, 150),
                    "cake": random.randint(300, 500),
                    "bread": random.randint(80, 200),
                    "rice": random.randint(150, 300),
                    "chicken": random.randint(200, 400),
                    "vegetables": random.randint(50, 150),
                    "soup": random.randint(100, 300),
                    "steak": random.randint(300, 600),
                    "fish": random.randint(200, 400)
                }
                
                total_calories = sum(food_calories[food] for food in detected_foods)
                return total_calories, detected_foods
            else:
                return 0, []
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return 0, []
    
    def analyze_all_screenshots(self):
        """Analyze all screenshots and return results"""
        screenshot_files = self.get_screenshots()
        
        if not screenshot_files:
            print(f"No screenshots found in '{self.screenshots_dir}'")
            return []
        
        print(f"Analyzing {len(screenshot_files)} screenshots...")
        
        # Process screenshots in parallel for faster analysis
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.analyze_screenshot, screenshot_files))
        
        return results

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Screenshot Calorie Analyzer')
    
    parser.add_argument('-d', '--directory', type=str, default='screenshots',
                        help='Directory containing screenshots (default: screenshots)')
    
    parser.add_argument('-k', '--api-key', type=str,
                        help='API key for image recognition service (if needed)')
    
    parser.add_argument('-s', '--seed', type=int,
                        help='Random seed for reproducible results')
    
    return parser.parse_args()

def print_calorie_report(results):
    """Print a report of calorie analysis"""
    if not results:
        print("No results to display")
        return
    
    total_calories = sum(r['calories'] for r in results)
    food_images = sum(1 for r in results if r['calories'] > 0)
    
    print("\n===== CALORIE ANALYSIS REPORT =====")
    print(f"Total screenshots analyzed: {len(results)}")
    print(f"Screenshots containing food: {food_images}")
    print(f"Estimated total calories: {total_calories}")
    print("==================================")
    
    # Print details for images with calories
    if food_images > 0:
        print("\nDetailed breakdown:")
        for result in results:
            if result['calories'] > 0:
                foods_str = ", ".join(result['food_items'])
                print(f"- {result['filename']}: {result['calories']} calories")
                print(f"  Detected items: {foods_str}")
        print("\nNOTE: This analysis is simulated for demonstration purposes.")
        print("A real implementation would use actual AI models trained on food recognition.")

if __name__ == "__main__":
    args = parse_arguments()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    
    analyzer = CalorieAnalyzer(
        screenshots_dir=args.directory,
        api_key=args.api_key
    )
    
    results = analyzer.analyze_all_screenshots()
    print_calorie_report(results) 