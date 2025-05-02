# Dynmap Screenshot Bot

A Python script that captures screenshots of Minecraft dynmap webpages using Playwright.

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install chromium
```

## Usage

Basic usage:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective
```

This will capture a screenshot of the specified dynmap URL and save it with a timestamped filename (e.g., `dynmap_screenshot_20250502_160500.png`).

### Command-line Options

- `-o, --output`: Path to save the screenshot (optional)
- `-w, --wait`: Time in seconds to wait for the map to load (default: 10)
- `--width`: Width of the viewport (default: 1920)
- `--height`: Height of the viewport (default: 1080)

### Examples

Specify an output filename:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -o my_map.png
```

Adjust the wait time for slow connections:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -w 15
```

Change the viewport size:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective --width 2560 --height 1440
```

## Troubleshooting

- If the map doesn't load properly, try increasing the wait time using the `-w` option
- For high-resolution displays, you might want to increase the viewport size with `--width` and `--height`
- If you encounter any browser-related issues, make sure you've installed the Playwright browsers with `python -m playwright install chromium`
