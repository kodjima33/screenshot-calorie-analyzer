# Screenshot Taker with Calorie Analysis

A Python application that captures screenshots of your screen at regular intervals and analyzes them for calorie content using simulated AI detection.

## Features

- Take screenshots at configurable intervals
- Automatically save screenshots with timestamps
- Run in the background until manually stopped
- Optional region selection (advanced version)
- Multiple output formats (advanced version)
- Compression settings (advanced version)
- Logging capabilities (advanced version)
- Calorie analysis of captured screenshots (simulated AI)
- Periodic reporting of detected food items and calorie estimates

## Requirements

- Python 3.6+
- PyAutoGUI
- Pillow (PIL)
- NumPy
- Requests

## Installation

1. Clone this repository or download the files
2. Create and activate a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your Gemini API key:
   - Create a `.env` file in the project directory based on the provided `.env.example`
   - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`

## Usage

### Basic Screenshot Taker

Run the basic script from the command line:

```bash
python screenshot_taker.py
```

The application will:
- Create a "screenshots" directory (if it doesn't exist)
- Take a screenshot every 10 seconds
- Save each screenshot with a timestamp
- Display a message for each captured screenshot

### Advanced Screenshot Taker

The advanced version provides more flexibility and features:

```bash
python advanced_screenshot.py [options]
```

Available options:
- `-d, --directory`: Directory to save screenshots (default: screenshots)
- `-i, --interval`: Time between screenshots in seconds (default: 10)
- `-f, --format`: Image format - png, jpg, jpeg, bmp (default: png)
- `-p, --prefix`: Prefix for screenshot filenames (default: screenshot)
- `-r, --region`: Region to capture as left,top,width,height (default: full screen)
- `-c, --compress`: Compression level 0-9, PNG only (default: 0)
- `-l, --log-level`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

### Calorie Analyzer

The calorie analyzer can be run separately to analyze existing screenshots:

```bash
python calorie_analyzer.py [options]
```

Available options:
- `-d, --directory`: Directory containing screenshots (default: screenshots)
- `-s, --seed`: Random seed for reproducible results (default: none)

This will:
- Scan the specified directory for screenshot images
- Analyze each image for food content using simulated AI detection
- Generate a report of total calories and detected food items

### Combined: Screenshot with Calorie Analysis

The combined script takes screenshots and periodically analyzes them:

```bash
python screenshot_with_calories.py [options]
```

Available options:
- `-d, --directory`: Directory to save screenshots (default: screenshots)
- `-i, --interval`: Time between screenshots in seconds (default: 10)
- `-a, --analysis-interval`: Time between calorie analyses in seconds (default: 60)
- `-s, --seed`: Random seed for reproducible calorie analysis (default: 42)

This will:
- Take screenshots at the specified interval
- Run calorie analysis periodically at the specified analysis interval
- Print calorie reports to the terminal
- Continue until stopped with Ctrl+C

Example to take screenshots every 5 seconds and analyze every 30 seconds:
```bash
python screenshot_with_calories.py -i 5 -a 30
```

To stop any of these applications, press `Ctrl+C` in the terminal.

### All-in-One Calorie Monitor (Unified Script)

A single unified script that both takes screenshots and analyzes them immediately:

```bash
python calorie_monitor.py [options]
```

Available options:
- `-d, --directory`: Directory to save screenshots (default: screenshots)
- `-i, --interval`: Time between screenshots in seconds (default: 10)
- `-k, --api-key`: API key for Gemini model (optional if set in .env file)
- `-s, --screen-half`: Which half of screen to capture (left or right, default: left)

This will:
- Take a screenshot of the specified half of the screen at the given interval
- Immediately analyze each screenshot with Gemini 2.0 Flash
- Print results as soon as the analysis is complete
- Continue until stopped with Ctrl+C

Example:
```bash
# Using API key from .env file (recommended)
python calorie_monitor.py -i 15 -s right

# Explicitly providing API key
python calorie_monitor.py -k YOUR_API_KEY -i 15 -s right
```

This simplified approach performs everything in a single process and provides immediate feedback after each screenshot is analyzed.

## Customization

You can modify the scripts to:
- Change default values for any parameter
- Implement real AI models for food detection
- Connect to actual calorie databases
- Add support for more image formats
- Implement additional features like uploading to cloud storage
- Add GUI for easier configuration and monitoring

## Notes on Calorie Analysis

The calorie analysis in this application has two implementations:

1. **Simulated Analysis** (in `calorie_analyzer.py`):
   - Uses random generation to simulate food detection
   - No actual image analysis is performed
   - For demonstration purposes only

2. **Gemini 2.0 Flash Analysis** (in `gemini_calorie_analyzer.py`):
   - Uses Google's Gemini 2.0 Flash AI model for actual food detection
   - Provides more accurate food identification and calorie estimates
   - Requires a Google API key

### Using Gemini 2.0 Flash

To use the Gemini-powered calorie analyzer:

```bash
python gemini_calorie_analyzer.py -k YOUR_API_KEY -d screenshots
```

For the combined screenshot and Gemini analysis:

```bash
python screenshot_with_gemini.py -k YOUR_API_KEY -i 10 -a 60
```

This will:
- Take screenshots every 10 seconds
- Analyze them with Gemini 2.0 Flash every 60 seconds
- Provide detailed calorie estimates for any detected food items

## License

Open source, feel free to use and modify! 