#!/usr/bin/env python3
"""
Dynmap Screenshot Bot
---------------------
A script to capture screenshots of a Minecraft dynmap webpage.
"""

from playwright.sync_api import sync_playwright
import time
import os
import argparse
import glob
import re
import json
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage

def capture_dynmap(url, output_path=None, wait_time=10, viewport_width=1920, viewport_height=1080, 
                   x_coord=None, z_coord=None, zoom_out_clicks=1):
    """
    Captures a screenshot of a dynmap webpage using Playwright.
    
    Args:
        url (str): The URL of the dynmap to capture
        output_path (str, optional): Path to save the screenshot. If None, a timestamped filename is used.
        wait_time (int, optional): Time in seconds to wait for the map to load. Default is 10.
        viewport_width (int, optional): Width of the viewport. Default is 1920.
        viewport_height (int, optional): Height of the viewport. Default is 1080.
        x_coord (int, optional): X coordinate to navigate to before taking screenshot.
        z_coord (int, optional): Z coordinate to navigate to before taking screenshot.
        zoom_out_clicks (int, optional): Number of times to click the zoom-out button. Default is 2.
        
    Returns:
        str: Path to the saved screenshot
    """
    # Create default output path if none provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"dynmap_screenshot_{timestamp}.png"
    
    print(f"Navigating to: {url}")
    print(f"Will save screenshot to: {output_path}")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        
        # Create page with specified viewport
        page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
        
        # Go to the URL
        page.goto(url)
        
        # Wait for the map to initially load
        print(f"Waiting {wait_time} seconds for map to initially load...")
        time.sleep(wait_time)
        
        # If coordinates are provided, navigate to them
        if x_coord is not None and z_coord is not None:
            print(f"Navigating to coordinates X: {x_coord}, Z: {z_coord}...")
            
            # Wait for the coordinate input elements to be available
            page.wait_for_selector('div.position-input.pos-input input[type="number"]')
            
            # Get the input elements (first is X, second is Z)
            input_elements = page.query_selector_all('div.position-input.pos-input input[type="number"]')
            if len(input_elements) >= 2:
                x_input = input_elements[0]
                z_input = input_elements[1]
                
                # Clear existing values and enter new coordinates
                x_input.fill("")  # Clear first
                x_input.type(str(x_coord))
                z_input.fill("")  # Clear first
                z_input.type(str(z_coord))
                
                # Press Enter to trigger the coordinate change
                z_input.press("Enter")
                
                # Wait additional time for the map to update to the new position
                print(f"Waiting for map to update to the new position...")
                time.sleep(5)  # Additional wait time after entering coordinates
            else:
                print("Warning: Could not find coordinate input fields. Taking screenshot without navigating.")
        
        # If zoom_out_clicks is specified, click the zoom-out button that many times
        if zoom_out_clicks > 0:
            print(f"Zooming out {zoom_out_clicks} time(s) for better view...")
            zoom_out_button = page.query_selector("#zoom-buttons > div.svg-button:nth-child(2)")
            
            if zoom_out_button:
                for i in range(zoom_out_clicks):
                    zoom_out_button.click()
                    print(f"Zoom out click {i+1}/{zoom_out_clicks}")
                    # Wait for the map to update after zoom
                    time.sleep(2)
            else:
                print("Warning: Could not find zoom-out button. Taking screenshot without zooming.")
        
        # Take screenshot
        print("Taking screenshot...")
        page.screenshot(path=output_path)
        
        # Close browser
        browser.close()
    
    print(f"Screenshot saved to: {output_path}")
    return output_path

def get_next_image_number():
    """
    Get the next sequential image number by examining existing files.
    
    Returns:
        int: The next available image number
    """
    # Check for existing numbered images and find highest
    files = glob.glob("dynmap_*.png")
    if files:
        numbers = []
        for f in files:
            match = re.search(r'dynmap_(\d+)\.png', f)
            if match:
                numbers.append(int(match.group(1)))
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1
    
    print(f"Using image number: {next_num}")
    return next_num

def posterize_image(image_path, output_path=None, colors=16):
    """
    Reduce the image to a specified number of colors to make land claims more distinct.
    
    Args:
        image_path: Path to the input image
        output_path: Path for the posterized output image (if None, overwrites original)
        colors: Number of colors to reduce the image to (default: 16)
        
    Returns:
        Path to the posterized image
    """
    if output_path is None:
        output_path = image_path
        
    print(f"Posterizing image to {colors} colors...")
    
    # Open the image
    img = Image.open(image_path)
    
    # Convert to P mode with limited palette
    posterized = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
    posterized.save(output_path)
    
    print(f"Image posterized and saved to: {output_path}")
    return output_path

def analyze_color_pixel_counts(current, previous, percent_threshold=10):
    """
    Analyze changes in pixel counts for each land claim color between two images.
    
    Args:
        current: Numpy array of current image
        previous: Numpy array of previous image
        percent_threshold: Percentage decrease threshold to consider significant (default: 10)
        
    Returns:
        Dictionary with information about disappeared claims
    """
    # Define land claim colors with common variations
    land_claim_colors = {
        "red": [(163, 9, 7), (162, 8, 6), (164, 10, 8)],
        "green": [(10, 166, 40), (9, 165, 39), (11, 167, 41)],
        "purple": [(164, 5, 165), (163, 4, 164), (165, 6, 166)],
        "blue": [(7, 9, 164), (6, 8, 163), (8, 10, 165)],
        "orange": [(244, 166, 6), (243, 165, 5), (245, 167, 7)],
        "yellow": [(243, 242, 86), (242, 241, 85), (244, 243, 87)],
        "white": [(243, 244, 243), (242, 243, 242), (244, 245, 244)],
        "coral": [(240, 87, 85), (239, 86, 84), (241, 88, 86)]
    }
    
    # Get pixel counts for each color group in both images
    current_counts = {}
    previous_counts = {}
    
    for color_name, variations in land_claim_colors.items():
        # Initialize masks
        current_mask = np.zeros((current.shape[0], current.shape[1]), dtype=bool)
        previous_mask = np.zeros((previous.shape[0], previous.shape[1]), dtype=bool)
        
        # Add each variation to the mask
        for color_rgb in variations:
            r, g, b = color_rgb
            
            # Exact matching for current image
            current_color_mask = (
                (current[:,:,0] == r) & 
                (current[:,:,1] == g) & 
                (current[:,:,2] == b)
            )
            current_mask = current_mask | current_color_mask
            
            # Exact matching for previous image
            previous_color_mask = (
                (previous[:,:,0] == r) & 
                (previous[:,:,1] == g) & 
                (previous[:,:,2] == b)
            )
            previous_mask = previous_mask | previous_color_mask
        
        # Count pixels for this color
        current_counts[color_name] = np.sum(current_mask)
        previous_counts[color_name] = np.sum(previous_mask)
    
    # Detect significant decreases in pixel counts
    disappeared_claims = {}
    total_disappeared_pixels = 0
    
    for color_name in land_claim_colors:
        if previous_counts[color_name] > 0:  # Avoid division by zero
            decrease = previous_counts[color_name] - current_counts[color_name]
            percent_decrease = (decrease / previous_counts[color_name]) * 100
            
            if decrease > 0 and percent_decrease > percent_threshold:
                disappeared_claims[color_name] = {
                    'previous_count': int(previous_counts[color_name]),
                    'current_count': int(current_counts[color_name]),
                    'decrease': int(decrease),
                    'percent_decrease': float(percent_decrease)
                }
                total_disappeared_pixels += int(decrease)
    
    return disappeared_claims, total_disappeared_pixels

def detect_claim_changes(current_image, previous_image, output_path=None, threshold=50, min_area=20, 
                       focus_on_claims=False, color_tolerance=30, use_pixel_count=False, percent_threshold=10):
    """
    Compare two consecutive map images to detect disappeared land claims.
    
    Args:
        current_image: Path to the current map image
        previous_image: Path to the previous map image
        output_path: Path to save visualization of changes (if None, no visualization is saved)
        threshold: Threshold for pixel difference to be considered significant (default: 50)
        min_area: Minimum area in pixels for a change to be considered significant (default: 20)
        focus_on_claims: Whether to focus only on land claim colors (default: False)
        color_tolerance: How closely a pixel needs to match a land claim color (default: 30)
        use_pixel_count: Whether to use pixel count analysis (default: False)
        percent_threshold: Percentage decrease threshold for pixel count analysis (default: 10)
        
    Returns:
        Dictionary with results containing change information
    """
    print(f"Comparing with previous image: {previous_image}")
    
    # Define land claim colors (RGB values) for mask-based detection
    land_claim_colors = [
        (163, 9, 7),     # Red
        (10, 166, 40),   # Green
        (164, 5, 165),   # Purple
        (7, 9, 164),     # Blue
        (244, 166, 6),   # Orange
        (243, 242, 86),  # Yellow
        (243, 244, 243), # White
        (240, 87, 85),   # Coral
    ]
    
    # Load images and ensure they're in RGB mode
    current_img = Image.open(current_image)
    previous_img = Image.open(previous_image)
    
    # Convert to RGB mode if they're not already
    if current_img.mode != 'RGB':
        print(f"Converting current image from {current_img.mode} to RGB mode")
        current_img = current_img.convert('RGB')
    if previous_img.mode != 'RGB':
        print(f"Converting previous image from {previous_img.mode} to RGB mode")
        previous_img = previous_img.convert('RGB')
    
    # Convert to numpy arrays
    current = np.array(current_img)
    previous = np.array(previous_img)
    
    # Make sure images are the same size
    if current.shape != previous.shape:
        print("Error: Images have different dimensions, cannot compare")
        return {
            'timestamp': datetime.now().isoformat(),
            'changes_detected': False,
            'error': 'Images have different dimensions'
        }
    
    # Determine which detection method to use
    if use_pixel_count:
        # Use color pixel count analysis
        print(f"Using color pixel count analysis with percent threshold: {percent_threshold}%")
        disappeared_claims, total_disappeared_pixels = analyze_color_pixel_counts(
            current, previous, percent_threshold
        )
        
        # Create a simple visualization of disappeared claims
        changes = []
        if total_disappeared_pixels > 0:
            print(f"Found {total_disappeared_pixels} total disappeared claim pixels across {len(disappeared_claims)} colors")
            for color_name, stats in disappeared_claims.items():
                print(f"  - {color_name}: {stats['decrease']} pixels ({stats['percent_decrease']:.1f}% decrease)")
            
            # Create a simple region for visualization
            region = {
                'x_min': 0, 'y_min': 0,
                'x_max': current.shape[1] - 1, 'y_max': current.shape[0] - 1,
                'center_x': current.shape[1] // 2, 'center_y': current.shape[0] // 2,
                'area': total_disappeared_pixels,
                'colors': list(disappeared_claims.keys())
            }
            changes.append(region)
        
    elif focus_on_claims:
        print(f"Focusing detection on land claim colors with tolerance: {color_tolerance}")
        
        # Create masks for land claim colors
        current_mask = np.zeros((current.shape[0], current.shape[1]), dtype=bool)
        previous_mask = np.zeros((previous.shape[0], previous.shape[1]), dtype=bool)
        
        # For each land claim color, create a mask where that color exists
        for color in land_claim_colors:
            r, g, b = color
            
            # Create mask for current image
            current_color_mask = (
                (np.abs(current[:,:,0] - r) < color_tolerance) & 
                (np.abs(current[:,:,1] - g) < color_tolerance) & 
                (np.abs(current[:,:,2] - b) < color_tolerance)
            )
            current_mask = current_mask | current_color_mask
            
            # Create mask for previous image
            previous_color_mask = (
                (np.abs(previous[:,:,0] - r) < color_tolerance) & 
                (np.abs(previous[:,:,1] - g) < color_tolerance) & 
                (np.abs(previous[:,:,2] - b) < color_tolerance)
            )
            previous_mask = previous_mask | previous_color_mask
        
        # Find disappeared land claims (in previous but not in current)
        change_mask = previous_mask & ~current_mask
        print(f"Found {np.sum(change_mask)} pixels of potential disappeared land claims")
        
        # Find connected regions and extract changes
        labeled, num_features = ndimage.label(change_mask)
        changes = []
        for label in range(1, num_features+1):
            y, x = np.where(labeled == label)
            if len(y) > min_area:  # Minimum size threshold
                region = {
                    'x_min': int(np.min(x)), 'y_min': int(np.min(y)),
                    'x_max': int(np.max(x)), 'y_max': int(np.max(y)),
                    'center_x': int((np.min(x) + np.max(x)) / 2),
                    'center_y': int((np.min(y) + np.max(y)) / 2),
                    'area': int(len(y))
                }
                changes.append(region)
    else:
        # Use the original difference-based approach
        print(f"Using general pixel difference detection with threshold: {threshold}")
        diff = np.abs(current.astype(int) - previous.astype(int))
        diff_sum = diff.sum(axis=2)  # Sum across RGB channels
        change_mask = diff_sum > threshold
        
        # Find connected regions and extract changes
        labeled, num_features = ndimage.label(change_mask)
        changes = []
        for label in range(1, num_features+1):
            y, x = np.where(labeled == label)
            if len(y) > min_area:  # Minimum size threshold
                region = {
                    'x_min': int(np.min(x)), 'y_min': int(np.min(y)),
                    'x_max': int(np.max(x)), 'y_max': int(np.max(y)),
                    'center_x': int((np.min(x) + np.max(x)) / 2),
                    'center_y': int((np.min(y) + np.max(y)) / 2),
                    'area': int(len(y))
                }
                changes.append(region)
    
    
    # Save visualization if requested
    if output_path and changes:
        vis_img = Image.open(current_image).copy()
        draw = ImageDraw.Draw(vis_img)
        for r in changes:
            draw.rectangle([r['x_min'], r['y_min'], r['x_max'], r['y_max']], 
                          outline="red", width=2)
        vis_img.save(output_path)
        print(f"Change visualization saved to: {output_path}")
    
    # Generate result dictionary
    result = {
        'timestamp': datetime.now().isoformat(),
        'changes_detected': len(changes) > 0,
        'num_changes': len(changes),
        'changes': changes,
        'current_image': current_image,
        'previous_image': previous_image,
        'visualization': output_path if (output_path and changes) else None
    }
    
    # Print summary
    if changes:
        print(f"Found {len(changes)} areas with disappeared land claims!")
        for i, region in enumerate(changes):
            print(f"Region {i+1}: Center at approx. ({region['center_x']}, {region['center_y']}), "
                  f"Area: {region['area']} pixels")
    else:
        print("No significant land claim changes detected")
    
    return result

def crop_to_red_border(image_path, output_path=None):
    """
    Crops an image to the content inside a red border.
    
    Args:
        image_path: Path to the input image
        output_path: Path for the cropped output image (if None, overwrites original)
        
    Returns:
        Path to the cropped image
    """
    if output_path is None:
        output_path = image_path
        
    print(f"Analyzing image for red border...")
    
    # Open the image
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Define red color threshold (with some tolerance)
    # Red channel high, green and blue channels low
    red_mask = (img_array[:,:,0] > 180) & (img_array[:,:,1] < 80) & (img_array[:,:,2] < 80)
    
    # Find coordinates where red border exists
    y_indices, x_indices = np.where(red_mask)
    
    if len(y_indices) > 0 and len(x_indices) > 0:
        # Find the bounding box of the red border
        top = np.min(y_indices)
        bottom = np.max(y_indices)
        left = np.min(x_indices)
        right = np.max(x_indices)
        
        # Find inner content (slightly inside the red border)
        margin = 5
        inner_top = top + margin
        inner_bottom = bottom - margin
        inner_left = left + margin
        inner_right = right - margin
        
        # Make sure we have a valid box
        if inner_bottom > inner_top and inner_right > inner_left:
            # Crop the image to the inner content
            cropped_img = img.crop((inner_left, inner_top, inner_right, inner_bottom))
            cropped_img.save(output_path)
            print(f"Image cropped to {inner_right-inner_left}x{inner_bottom-inner_top} pixels")
            print(f"Cropped image saved to: {output_path}")
            return output_path
    
    print("Could not detect red border clearly. Saving original image.")
    img.save(output_path)
    return output_path

def main():
    """Main function to parse command line arguments and capture the screenshot."""
    parser = argparse.ArgumentParser(description="Capture screenshots of Minecraft dynmap webpages")
    
    parser.add_argument("url", help="The URL of the dynmap to capture")
    parser.add_argument(
        "-o", "--output", 
        help="Path to save the screenshot. If not provided, a sequentially numbered filename is used."
    )
    parser.add_argument(
        "-w", "--wait", 
        type=int, 
        default=10, 
        help="Time in seconds to wait for the map to load. Default is 10."
    )
    parser.add_argument(
        "--width", 
        type=int, 
        default=1920, 
        help="Width of the viewport. Default is 1920."
    )
    parser.add_argument(
        "--height", 
        type=int, 
        default=1080, 
        help="Height of the viewport. Default is 1080."
    )
    parser.add_argument(
        "-x", "--x-coord",
        type=int,
        help="X coordinate to navigate to before taking screenshot."
    )
    parser.add_argument(
        "-z", "--z-coord",
        type=int,
        help="Z coordinate to navigate to before taking screenshot."
    )
    parser.add_argument(
        "--zoom-out",
        type=int,
        default=2,
        help="Number of times to click the zoom-out button (default: 2)"
    )
    parser.add_argument(
        "--crop",
        action="store_true",
        help="Crop the image to the content inside the red border"
    )
    parser.add_argument(
        "--posterize",
        type=int,
        default=0,
        help="Reduce the image to specified number of colors (0 to disable)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare with previous image to detect land claim changes"
    )
    parser.add_argument(
        "--changes-output",
        help="Path to save visualization of detected changes (requires --compare)"
    )
    parser.add_argument(
        "--json-output",
        help="Path to save change detection results as JSON (requires --compare)"
    )
    parser.add_argument(
        "--seq",
        action="store_true",
        help="Use sequential numbering for output filenames (dynmap_001.png, dynmap_002.png, etc.)"
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=20,
        help="Minimum area in pixels for a change to be considered significant (default: 20)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=50,
        help="Threshold for pixel difference to be considered significant (default: 50)"
    )
    parser.add_argument(
        "--focus-on-claims",
        action="store_true",
        help="Focus only on land claim colors for change detection"
    )
    parser.add_argument(
        "--color-tolerance",
        type=int,
        default=30,
        help="How closely a pixel needs to match a land claim color (default: 30)"
    )
    parser.add_argument(
        "--use-pixel-count",
        action="store_true",
        help="Use color pixel count analysis to detect disappeared land claims"
    )
    parser.add_argument(
        "--percent-threshold",
        type=float,
        default=10.0,
        help="Percentage decrease threshold for pixel count analysis (default: 10.0)"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    output_path = args.output
    if output_path is None:
        if args.seq:
            # Use sequential numbering
            num = get_next_image_number()
            output_path = f"dynmap_{num:03d}.png"
        else:
            # Use timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"dynmap_screenshot_{timestamp}.png"
    
    # Capture the screenshot
    screenshot_path = capture_dynmap(
        args.url, 
        output_path, 
        args.wait, 
        args.width, 
        args.height,
        args.x_coord,
        args.z_coord,
        args.zoom_out
    )
    
    # Process the screenshot based on command line options
    if args.crop and screenshot_path:
        screenshot_path = crop_to_red_border(screenshot_path)
    
    # Posterize the image if requested
    if args.posterize > 0 and screenshot_path:
        screenshot_path = posterize_image(screenshot_path, colors=args.posterize)
    
    # Compare with previous image if requested
    if args.compare and screenshot_path:
        # Get previous image path based on current image name
        if args.seq:
            # Extract current image number
            match = re.search(r'dynmap_(\d+)\.png', screenshot_path)
            if match:
                current_num = int(match.group(1))
                if current_num > 1:
                    prev_num = current_num - 1
                    prev_path = f"dynmap_{prev_num:03d}.png"
                    
                    if os.path.exists(prev_path):
                        # Generate visualization path if not specified
                        changes_output = args.changes_output
                        if changes_output is None and current_num > 1:
                            changes_output = f"changes_{current_num:03d}.png"
                        
                        # Compare and detect changes
                        results = detect_claim_changes(
                            screenshot_path, 
                            prev_path, 
                            changes_output,
                            threshold=args.threshold,
                            min_area=args.min_area,
                            focus_on_claims=args.focus_on_claims,
                            color_tolerance=args.color_tolerance,
                            use_pixel_count=args.use_pixel_count,
                            percent_threshold=args.percent_threshold
                        )
                        
                        # Save results to JSON if requested
                        if args.json_output and results['changes_detected']:
                            with open(args.json_output, 'w') as f:
                                json.dump(results, f, indent=2)
                            print(f"Results saved to: {args.json_output}")
                        
                        # Set exit code based on whether changes were detected
                        if results['changes_detected']:
                            print("Changes detected! Use exit code 1")
                            exit(1)  # Changes detected
                    else:
                        print(f"No previous image found: {prev_path}")
    
    print("Finished processing")
    return 0  # No changes detected or comparison not enabled

if __name__ == "__main__":
    main()
