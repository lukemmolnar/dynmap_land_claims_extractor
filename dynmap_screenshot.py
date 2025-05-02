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

def capture_dynmap(url, output_path=None, wait_time=10, viewport_width=1920, viewport_height=1080):
    """
    Captures a screenshot of a dynmap webpage using Playwright.
    
    Args:
        url (str): The URL of the dynmap to capture
        output_path (str, optional): Path to save the screenshot. If None, a timestamped filename is used.
        wait_time (int, optional): Time in seconds to wait for the map to load. Default is 10.
        viewport_width (int, optional): Width of the viewport. Default is 1920.
        viewport_height (int, optional): Height of the viewport. Default is 1080.
        
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
        
        # Wait for the map to load
        print(f"Waiting {wait_time} seconds for map to fully load...")
        time.sleep(wait_time)
        
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
    
    args = parser.parse_args()
    
    capture_dynmap(
        args.url, 
        args.output, 
        args.wait, 
        args.width, 
        args.height
    )

if __name__ == "__main__":
    main()
