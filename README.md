# Dynmap Land Claims Detector

A Python script that captures screenshots of Minecraft dynmap webpages and monitors for disappeared land claims.

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

#### Screenshot Capture Options
- `-o, --output`: Path to save the screenshot (optional)
- `-w, --wait`: Time in seconds to wait for the map to load (default: 10)
- `--width`: Width of the viewport (default: 1920)
- `--height`: Height of the viewport (default: 1080)
- `-x, --x-coord`: X coordinate to navigate to before taking screenshot (optional)
- `-z, --z-coord`: Z coordinate to navigate to before taking screenshot (optional)
- `--zoom-out`: Number of times to click the zoom-out button (default: 2)
- `--crop`: Crop the image to the content inside the red border

#### Sequential Numbering
- `--seq`: Use sequential numbering for output filenames (dynmap_001.png, dynmap_002.png, etc.)

#### Image Processing 
- `--posterize`: Reduce image to specified number of colors (e.g., 16) for better land claim detection

#### Land Claim Change Detection
- `--compare`: Compare with previous image to detect land claim changes
- `--changes-output`: Path to save visualization of detected changes
- `--json-output`: Path to save change detection results as JSON
- `--min-area`: Minimum area in pixels for a change to be considered significant (default: 20)
- `--threshold`: Threshold for pixel difference to be considered significant (default: 50)
- `--focus-on-claims`: Focus only on land claim colors for change detection
- `--color-tolerance`: How closely a pixel needs to match a land claim color (default: 30)
- `--use-pixel-count`: Use color pixel count analysis to detect disappeared land claims
- `--percent-threshold`: Percentage decrease threshold for pixel count analysis (default: 10.0)

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

Navigate to specific coordinates before taking the screenshot:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093
```

Navigate to coordinates and control zoom level:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --zoom-out 3
```

Disable zooming out (take screenshot at default zoom level):

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --zoom-out 0
```

#### Basic Screenshot with Cropping

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop
```

#### Sequential Numbering for Automation

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --seq
```

#### Image Posterization for Better Land Claim Analysis

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq
```

#### Land Claim Change Detection (Generic)

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare
```

#### Land Claim Color-Specific Detection

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --focus-on-claims --color-tolerance 30
```

#### Pixel Count Analysis for Disappeared Claims

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --use-pixel-count --percent-threshold 10
```

#### Complete Example with Change Visualization and JSON Output

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --zoom-out 2 --width 2048 --height 1200 --crop --posterize 16 --seq --compare --changes-output changes.png --json-output changes.json
```

## Exit Codes

The script uses exit codes to indicate the result of the operation:

- `0`: Successful completion (no changes detected or comparison not enabled)
- `1`: Land claim changes detected (when using `--compare`)

This allows you to use the script in automated workflows or with a Discord bot that can notify when changes are detected.

## Tips for Automated Monitoring

1. **Set up a scheduled task** to run the script every few minutes:
   ```bash
   # Example cron job (runs every 5 minutes)
   */5 * * * * cd /path/to/dynmap_land_claims_extractor && python dynmap_screenshot.py <ARGS> >> dynmap_monitor.log 2>&1
   ```

2. **Use sequential numbering** (`--seq`) to maintain a history of screenshots.

3. **Optimize image processing**:
   - Adjust the posterization level (`--posterize`) based on your map's colors
   - Tune the detection threshold (`--threshold`) and minimum area (`--min-area`) to reduce false positives

4. **Discord bot integration**:
   - Use the JSON output (`--json-output`) to get structured data about changes
   - Send the visualization image (`--changes-output`) to Discord when changes are detected
   - Check the exit code to determine if changes were found

## Troubleshooting

- If the map doesn't load properly, try increasing the wait time using the `-w` option
- For high-resolution displays, you might want to increase the viewport size with `--width` and `--height`
- If you encounter any browser-related issues, make sure you've installed the Playwright browsers with `python -m playwright install chromium`
- If you're getting false positives in change detection, try:
  - Using `--use-pixel-count` to count pixels of specific land claim colors
  - Adjusting `--percent-threshold` to require a higher percentage of pixel decrease
  - Enabling `--focus-on-claims` to only detect changes in land claim colors
  - Adjusting `--color-tolerance` to fine-tune how strictly to match land claim colors (lower = stricter)
  - Increasing the `--threshold` and `--min-area` values
- If land claims aren't being detected properly, try:
  - Adjusting the `--posterize` value to better distinguish claim colors
  - Decreasing `--color-tolerance` if using color-specific detection
  - Lowering `--percent-threshold` if using pixel count analysis
