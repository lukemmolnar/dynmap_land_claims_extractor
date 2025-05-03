#!/usr/bin/env python3
"""
Test script for visualizing disappeared claim pixels.
"""

import os
from PIL import Image, ImageDraw
import numpy as np
from datetime import datetime

def get_disappeared_mask(current, previous, color_name):
    """
    Create a mask of pixels where a specific color disappeared between images.
    """
    # Define land claim colors with common variations
    land_claim_colors = {
        "red": [(163, 9, 7), (162, 8, 6), (164, 10, 8)],
        "green": [(10, 166, 40), (9, 165, 39), (11, 167, 41)],
        "purple": [(164, 5, 165), (163, 4, 164), (165, 6, 166)],
        "blue": [(7, 9, 164), (6, 8, 163), (8, 10, 165)],
        "orange": [(244, 166, 6), (243, 165, 5), (245, 167, 7)],
        "yellow": [(243, 242, 86), (242, 241, 85), (244, 243, 87), (240, 240, 80), (245, 245, 90)],
        "white": [(243, 244, 243), (242, 243, 242), (244, 245, 244)],
        "coral": [(240, 87, 85), (239, 86, 84), (241, 88, 86)]
    }
    
    # Get color variations for this color
    color_variations = land_claim_colors.get(color_name, [])
    if not color_variations:
        print(f"Warning: Unknown color name: {color_name}")
        return np.zeros((current.shape[0], current.shape[1]), dtype=bool)
    
    # Create masks for this color in both images
    current_mask = np.zeros((current.shape[0], current.shape[1]), dtype=bool)
    previous_mask = np.zeros((previous.shape[0], previous.shape[1]), dtype=bool)
    
    # Add each variation to the mask
    for color_rgb in color_variations:
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
    
    # Find areas where color existed before but not now
    disappeared_mask = previous_mask & ~current_mask
    
    return disappeared_mask

def analyze_color_pixel_counts(current, previous):
    """
    Analyze changes in pixel counts for each land claim color.
    """
    # Define land claim colors with common variations
    land_claim_colors = {
        "red": [(163, 9, 7), (162, 8, 6), (164, 10, 8)],
        "green": [(10, 166, 40), (9, 165, 39), (11, 167, 41)],
        "purple": [(164, 5, 165), (163, 4, 164), (165, 6, 166)],
        "blue": [(7, 9, 164), (6, 8, 163), (8, 10, 165)],
        "orange": [(244, 166, 6), (243, 165, 5), (245, 167, 7)],
        "yellow": [(243, 242, 86), (242, 241, 85), (244, 243, 87), (240, 240, 80), (245, 245, 90)],
        "white": [(243, 244, 243), (242, 243, 242), (244, 245, 244)],
        "coral": [(240, 87, 85), (239, 86, 84), (241, 88, 86)]
    }
    
    # Get pixel counts for each color
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
    
    # Detect decreases in pixel counts
    disappeared_claims = {}
    total_disappeared_pixels = 0
    
    for color_name in land_claim_colors:
        if previous_counts[color_name] > 0:  # Avoid division by zero
            decrease = previous_counts[color_name] - current_counts[color_name]
            percent_decrease = (decrease / previous_counts[color_name]) * 100
            
            # Any decrease > 0 is significant for this test
            if decrease > 0:
                disappeared_claims[color_name] = {
                    'previous_count': int(previous_counts[color_name]),
                    'current_count': int(current_counts[color_name]),
                    'decrease': int(decrease),
                    'percent_decrease': float(percent_decrease)
                }
                total_disappeared_pixels += int(decrease)
                print(f"Detected disappearance in {color_name}: {decrease} pixels ({percent_decrease:.1f}%)")
    
    return disappeared_claims, total_disappeared_pixels

def main():
    # Use existing images for testing
    current_image_path = "dynmap_010.png"  # Replace with your current image
    previous_image_path = "dynmap_011.png"  # Replace with your previous image
    
    if not os.path.exists(current_image_path) or not os.path.exists(previous_image_path):
        print(f"Error: Couldn't find test images. Please make sure {current_image_path} and {previous_image_path} exist.")
        return
    
    # Load and convert images to RGB
    current_img = Image.open(current_image_path).convert('RGB')
    previous_img = Image.open(previous_image_path).convert('RGB')
    
    # Convert to numpy arrays
    current = np.array(current_img)
    previous = np.array(previous_img)
    
    print("Analyzing color pixel counts...")
    disappeared_claims, total_disappeared_pixels = analyze_color_pixel_counts(current, previous)
    
    if total_disappeared_pixels > 0:
        print(f"Found {total_disappeared_pixels} total disappeared claim pixels across {len(disappeared_claims)} colors")
        
        # Create visualization
        print("Creating pixel-perfect visualization...")
        vis_img = current_img.copy()
        draw = ImageDraw.Draw(vis_img)
        
        # For each color that disappeared, highlight its pixels in red
        for color_name in disappeared_claims.keys():
            print(f"  - Highlighting disappeared {color_name} pixels")
            
            # Get mask for this color
            disappeared_mask = get_disappeared_mask(current, previous, color_name)
            
            # Color each disappeared pixel bright red
            y_indices, x_indices = np.where(disappeared_mask)
            for i in range(len(y_indices)):
                y, x = y_indices[i], x_indices[i]
                vis_img.putpixel((x, y), (255, 0, 0))  # Bright red
        
        # Add a legend
        legend_text = "Disappeared claims:"
        draw.text((10, 10), legend_text, fill=(255, 0, 0))
        y_offset = 30
        for color_name, stats in disappeared_claims.items():
            info_text = f"  {color_name}: {stats['decrease']} pixels"
            draw.text((10, y_offset), info_text, fill=(255, 0, 0))
            y_offset += 20
        
        # Save visualization
        os.makedirs("claim_disappearances", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"claim_disappearances/test_visualization_{timestamp}.png"
        vis_img.save(output_path)
        print(f"Visualization saved to: {output_path}")
    else:
        print("No pixel differences found between the images.")

if __name__ == "__main__":
    main()
