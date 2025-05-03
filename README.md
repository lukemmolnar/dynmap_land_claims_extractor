# Dynmap Land Claims Detector

A Python script that captures screenshots of Minecraft dynmap webpages and monitors for disappeared land claims across multiple maps.

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

#### Map Selection
- `--map`: The ID of the map to process (e.g., abex1, abex2)
- `--all-maps`: Process all maps defined in the config file
- `--config-file`: Path to the map configuration file (default: maps.json)

#### Screenshot Capture Options
- `-o, --output`: Path to save the screenshot (optional)
- `-w, --wait`: Time in seconds to wait for the map to load after navigation completes (default: 10)
- `--navigation-timeout`: Playwright navigation timeout in seconds (default: 60)
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
- `--percent-threshold`: Percentage decrease threshold for pixel count analysis (default: 1.0)
- `--detect-any-change`: Detect ANY non-zero change in land claim colors, regardless of percentage

### Examples

Specify an output filename:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -o my_map.png
```

Adjust the wait time for slow connections:

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -w 15 --navigation-timeout 120
```

This increases both the navigation timeout (to 120 seconds) and the post-navigation wait time (to 15 seconds).

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
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --use-pixel-count --percent-threshold 1
```

#### Detect ANY Change in Land Claims

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --use-pixel-count --detect-any-change
```

This mode will detect even the smallest changes in land claim colors (1 pixel or more), ideal for monitoring when claims have disappeared.

#### Supported Land Claim Colors

The script can detect the following land claim colors:

- Red (163, 9, 7)
- Green (10, 166, 40)
- Purple (164, 5, 165)
- Blue (7, 9, 164)
- Orange (244, 166, 6)
- Yellow (243, 242, 86)
- White (243, 244, 243)
- Coral (240, 87, 85)
- Black (18, 17, 11)
- Light Blue (85, 86, 245)
- Teal (6, 165, 163)
- Ice Blue (169, 234, 243)

For each color, the script includes small variations to handle slight rendering differences.

#### Debug Mode for Color Detection

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --use-pixel-count --debug
```

This mode will:
- Print detailed information about exactly which colors are found in both images
- Save mask images to the `debug` folder showing which pixels match each color
- Show pixel counts for all colors and their differences between images

#### Pixel-Perfect Visualization of Disappeared Claims

All detected claim disappearances are now automatically saved to the `claim_disappearances` folder with **pixel-perfect accuracy**. Instead of approximate circles, the script now highlights the exact pixels that disappeared in bright red, showing the precise shape and location of the claim.

```bash
python dynmap_screenshot.py https://map.stoneworks.gg/abex3/#abex_3:-1874:0:143:1500:0:0:0:0:perspective -x -6780 -z 5093 --crop --posterize 16 --seq --compare --use-pixel-count
```

This makes it extremely easy to pinpoint exactly where to look for loot in-game, as you can see the exact shape and position of the disappeared claim.

#### Multi-Map Monitoring

Process a specific map defined in maps.json:
```bash
python dynmap_screenshot.py --map abex1 --crop --posterize 16 --seq --compare --use-pixel-count --detect-any-change
```

Process all maps defined in maps.json:
```bash
python dynmap_screenshot.py --all-maps --crop --posterize 16 --seq --compare --use-pixel-count --detect-any-change
```

Using a custom configuration file:
```bash
python dynmap_screenshot.py --all-maps --config-file my_maps.json --crop --posterize 16 --seq --compare --use-pixel-count
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
