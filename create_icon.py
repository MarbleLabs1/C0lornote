#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C0lorNote Icon Generator

This script generates a colorful, modern icon for the C0lorNote application
using matplotlib. It includes the @marbleceo branding.
"""

import os
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-GUI environments
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.colors import LinearSegmentedColormap

def generate_icon(output_path, size=512):
    """Generate the C0lorNote icon with @marbleceo branding"""

    # Set up the figure with transparent background
    fig = plt.figure(figsize=(size/100, size/100), dpi=100)
    ax = fig.add_subplot(111)

    # Set axis limits
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Remove axes and set transparent background
    ax.set_axis_off()
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Define colors from our three themes
    matrix_green = "#00FF41"
    dreamcore_purple = "#C147E9"
    minimalist_yellow = "#FFDA79"

    # Create a custom colormap combining our theme colors
    colors = [(0, matrix_green), (0.5, dreamcore_purple), (1, minimalist_yellow)]
    cmap = LinearSegmentedColormap.from_list("C0lorNote", colors, N=256)

    # Create a notepad base shape
    notepad = patches.Rectangle(
        (0.15, 0.1), 0.7, 0.8,
        facecolor='white',
        edgecolor='#333333',
        linewidth=2,
        alpha=0.95,
        zorder=1
    )
    ax.add_patch(notepad)

    # Add notepad lines
    for i in range(1, 8):
        y = 0.1 + i * 0.1
        ax.plot([0.2, 0.8], [y, y], color='#CCCCCC', linestyle='-', linewidth=1, zorder=2)

    # Add a colorful corner fold
    corner_fold_x = [0.85, 0.85, 0.7]
    corner_fold_y = [0.9, 0.75, 0.9]
    corner_fold = patches.Polygon(
        xy=list(zip(corner_fold_x, corner_fold_y)),
        facecolor='#EEEEEE',
        edgecolor='#333333',
        linewidth=1.5,
        zorder=3
    )
    ax.add_patch(corner_fold)

    # Add colorful accent shapes representing our three themes
    # Matrix theme element (code brackets)
    code_bracket_left = patches.Arc(
        (0.3, 0.5), 0.2, 0.6,
        theta1=90, theta2=270,
        linewidth=4, color=matrix_green,
        zorder=4
    )
    code_bracket_right = patches.Arc(
        (0.7, 0.5), 0.2, 0.6,
        theta1=270, theta2=90,
        linewidth=4, color=matrix_green,
        zorder=4
    )
    ax.add_patch(code_bracket_left)
    ax.add_patch(code_bracket_right)

    # Dreamcore theme element (wavy line)
    x = np.linspace(0.3, 0.7, 100)
    y = 0.5 + 0.1 * np.sin(x * 20)
    ax.plot(x, y, color=dreamcore_purple, linewidth=3, zorder=5)

    # Minimalist theme element (circle)
    circle = patches.Circle(
        (0.5, 0.5), 0.15,
        facecolor=minimalist_yellow,
        alpha=0.5,
        zorder=2
    )
    ax.add_patch(circle)

    # Add "C0" text in a dynamic style
    ax.text(
        0.5, 0.5, "C0",
        fontsize=min(50, size * 0.1), fontweight='bold', # Adjusted fontsize based on size
        ha='center', va='center',
        color='#333333',
        zorder=6
    )

    # Add @marbleceo branding
    ax.text(
        0.5, 0.15, "@marbleceo",
        fontsize=min(15, size * 0.03), fontweight='bold', # Adjusted fontsize based on size
        ha='center', va='center',
        color='#333333',
        zorder=6
    )

    # Save the icon
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0, transparent=True, dpi=100)
    plt.close(fig) # Close the specific figure

def generate_all_sizes(base_path, sizes=[512, 256, 128, 64, 32, 16]):
    """Generate icons for all specified sizes."""
    base_dir = os.path.dirname(base_path)
    base_name = os.path.basename(base_path).replace('.png', '')

    for size in sizes:
        icon_name = os.path.join(base_dir, f"{base_name}_{size}x{size}.png")
        print(f"Generating {size}x{size} icon...")
        generate_icon(icon_name, size)
    print("Finished generating all icon sizes.")

if __name__ == "__main__":
    # Check if matplotlib is installed
    try:
        import matplotlib
    except ImportError:
        print("Error: Matplotlib is not installed. Please install it using:")
        print("  pip install matplotlib")
        exit(1)

    # Create assets directory if it doesn't exist
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)

    # Generate the main 512x512 icon
    main_icon_path = os.path.join(assets_dir, "c0lornote_icon.png")
    print("Generating main 512x512 icon...")
    generate_icon(main_icon_path, 512)
    print(f"Main icon generated and saved to {main_icon_path}")

    # Generate icons for other standard sizes
    generate_all_sizes(main_icon_path)

