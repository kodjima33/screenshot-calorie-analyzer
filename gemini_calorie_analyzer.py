#!/usr/bin/env python3
"""
Gemini Calorie Analyzer - Uses Google's Gemini 2.0 Flash model to detect food in screenshots and estimate calories
"""

import os
import glob
import argparse
import time
import base64
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import google.generativeai as genai

class GeminiCalorieAnalyzer:
    def __init__(self, screenshots_dir="screenshots", api_key=None):
        """
        Initialize the Gemini-powered calorie analyzer
        
        Args:
            screenshots_dir (str): Directory containing screenshots
            api_key (str): API key for Gemini model
        """
        self.screenshots_dir = screenshots_dir
        self.api_key = api_key
        
        # Configure the Gemini API
        if not api_key:
            raise ValueError("API key is required for Gemini API")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.0 Flash model for image analysis
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
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
    
    def image_to_base64(self, image_path):
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_screenshot(self, screenshot_path):
        """
        Analyze a single screenshot for food items and calories using Gemini
        """
        try:
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
            
            # Process the response - extract the JSON part
            # This is a simplified extraction and would need better handling in production
            import json
            import re
            
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
            
            # Create result object
            if result_json.get("food_detected", False):
                food_items = result_json.get("food_items", [])
                total_calories = result_json.get("total_calories", 0)
                food_names = [item["name"] for item in food_items]
                
                return {
                    'filename': os.path.basename(screenshot_path),
                    'calories': total_calories,
                    'food_items': food_names,
                    'detailed_items': food_items,
                    'status': 'success'
                }
            else:
                return {
                    'filename': os.path.basename(screenshot_path),
                    'calories': 0,
                    'food_items': [],
                    'detailed_items': [],
                    'status': 'success'
                }
                
        except Exception as e:
            print(f"Error processing {screenshot_path}: {str(e)}")
            return {
                'filename': os.path.basename(screenshot_path),
                'calories': 0,
                'food_items': [],
                'detailed_items': [],
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_all_screenshots(self):
        """Analyze all screenshots and return results"""
        screenshot_files = self.get_screenshots()
        
        if not screenshot_files:
            print(f"No screenshots found in '{self.screenshots_dir}'")
            return []
        
        print(f"Analyzing {len(screenshot_files)} screenshots using Gemini 2.0 Flash...")
        
        # Process screenshots sequentially to avoid API rate limits
        results = []
        for screenshot in screenshot_files:
            print(f"Analyzing {os.path.basename(screenshot)}...")
            result = self.analyze_screenshot(screenshot)
            results.append(result)
            
            # Print calorie information immediately for this screenshot
            if result['calories'] > 0:
                foods_str = ", ".join(result['food_items'])
                print(f"✓ {os.path.basename(screenshot)}: {result['calories']} calories")
                print(f"  Detected items: {foods_str}")
                # Print detailed item breakdown
                if result.get('detailed_items'):
                    for item in result['detailed_items']:
                        print(f"    - {item['name']}: {item['calories']} calories")
            else:
                print(f"✓ {os.path.basename(screenshot)}: No food detected (0 calories)")
            
            # Small delay to prevent hitting API rate limits
            time.sleep(1)
        
        return results

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Gemini-powered Screenshot Calorie Analyzer')
    
    parser.add_argument('-d', '--directory', type=str, default='screenshots',
                        help='Directory containing screenshots (default: screenshots)')
    
    parser.add_argument('-k', '--api-key', type=str, required=True,
                        help='API key for Gemini model (required)')
    
    return parser.parse_args()

def print_calorie_report(results):
    """Print a report of calorie analysis"""
    if not results:
        print("No results to display")
        return
    
    total_calories = sum(r['calories'] for r in results)
    food_images = sum(1 for r in results if r['calories'] > 0)
    
    print("\n===== GEMINI 2.0 FLASH CALORIE ANALYSIS REPORT =====")
    print(f"Total screenshots analyzed: {len(results)}")
    print(f"Screenshots containing food: {food_images}")
    print(f"Estimated total calories: {total_calories}")
    print("=================================================")
    
    # Print details for images with calories
    if food_images > 0:
        print("\nDetailed breakdown:")
        for result in results:
            if result['calories'] > 0:
                foods_str = ", ".join(result['food_items'])
                print(f"- {result['filename']}: {result['calories']} calories")
                print(f"  Detected items: {foods_str}")
                
                # Print detailed item breakdown
                if result.get('detailed_items'):
                    print("  Item details:")
                    for item in result['detailed_items']:
                        print(f"    - {item['name']}: {item['calories']} calories")
                print()

if __name__ == "__main__":
    args = parse_arguments()
    
    analyzer = GeminiCalorieAnalyzer(
        screenshots_dir=args.directory,
        api_key=args.api_key
    )
    
    results = analyzer.analyze_all_screenshots()
    print_calorie_report(results) 