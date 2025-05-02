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
from datetime import datetime

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

def main():
    """Main function to parse command line arguments and capture the screenshot."""
    parser = argparse.ArgumentParser(description="Capture screenshots of Minecraft dynmap webpages")
    
    parser.add_argument("url", help="The URL of the dynmap to capture")
    parser.add_argument(
        "-o", "--output", 
        help="Path to save the screenshot. If not provided, a timestamped filename is used."
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
    
    args = parser.parse_args()
    
    capture_dynmap(
        args.url, 
        args.output, 
        args.wait, 
        args.width, 
        args.height,
        args.x_coord,
        args.z_coord,
        args.zoom_out
    )

if __name__ == "__main__":
    main()
