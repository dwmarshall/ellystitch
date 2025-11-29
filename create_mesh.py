#!/usr/bin/env python3
"""
Creates a PNG image of a 40x40 mesh for embroidery.
"""

from PIL import Image, ImageDraw
import yaml
import os


def load_threads(threads_file):
    """
    Load thread specifications from a YAML file.

    Args:
        threads_file: Path to YAML file containing thread definitions

    Returns:
        List of thread dictionaries. Each thread can have:
        - 'color': color name
        - 'paths': list of dictionaries with 'start' and 'end' keys (new format)
        - OR 'start' and 'end' keys directly (old format, for backward compatibility)
    """
    if not os.path.exists(threads_file):
        return []

    with open(threads_file, "r") as f:
        data = yaml.safe_load(f)
        return data.get("threads", [])


def calculate_grid_size(threads):
    """
    Calculate the minimum grid size needed to contain all threads.

    Args:
        threads: List of thread dictionaries

    Returns:
        Tuple of (max_x, max_y) coordinates, or (40, 40) if no threads
    """
    if not threads:
        return 40, 40

    max_x = 0
    max_y = 0

    for thread in threads:
        # Support both old format (single start/end) and new format (paths list)
        if "paths" in thread:
            # New format: multiple paths per color
            paths = thread.get("paths", [])
            for path in paths:
                start = path.get("start", [0, 0])
                end = path.get("end", [0, 0])
                max_x = max(max_x, start[0], end[0])
                max_y = max(max_y, start[1], end[1])
        else:
            # Old format: single start/end (backward compatibility)
            start = thread.get("start", [0, 0])
            end = thread.get("end", [0, 0])
            max_x = max(max_x, start[0], end[0])
            max_y = max(max_y, start[1], end[1])

    # Add 1 to include the edge, and ensure minimum size
    return max(max_x + 1, 1), max(max_y + 1, 1)


def create_embroidery_mesh(
    size=None,
    cell_size=20,
    line_width=1,
    output_file="embroidery_mesh.png",
    threads_file=None,
    thread_width=3,
):
    """
    Create a PNG image of an embroidery mesh grid.

    Args:
        size: Number of cells per side (default: None, auto-calculate from threads)
        cell_size: Size of each cell in pixels (default: 20)
        line_width: Width of grid lines in pixels (default: 1)
        output_file: Output PNG filename
        threads_file: Optional path to YAML file with thread specifications
        thread_width: Width of thread lines in pixels (default: 3)
    """
    # Load threads first to calculate size if needed
    threads = []
    if threads_file:
        threads = load_threads(threads_file)

    # Calculate grid size from threads if not provided
    if size is None:
        if threads:
            max_x, max_y = calculate_grid_size(threads)
            # Use rectangular grid based on actual dimensions
            width = max_x
            height = max_y
        else:
            width = 40  # Default if no threads
            height = 40
    else:
        # If size is provided, use it for both dimensions (square)
        width = size
        height = size

    # Calculate image dimensions
    image_width = width * cell_size + 1  # +1 for the final line
    image_height = height * cell_size + 1
    padding = 20  # Padding around the grid

    # Create image with white background
    img = Image.new(
        "RGB",
        (image_width + 2 * padding, image_height + 2 * padding),
        "white",
    )
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    # Vertical lines
    for i in range(width + 1):
        x = padding + i * cell_size
        draw.line(
            [(x, padding), (x, padding + image_height - 1)],
            fill="black",
            width=line_width,
        )

    # Horizontal lines
    for i in range(height + 1):
        y = padding + i * cell_size
        draw.line(
            [(padding, y), (padding + image_width - 1, y)],
            fill="black",
            width=line_width,
        )

    # Optionally mark intersection points (stitch points)
    point_radius = 1
    for i in range(width + 1):
        for j in range(height + 1):
            x = padding + i * cell_size
            y = padding + j * cell_size
            draw.ellipse(
                [
                    x - point_radius,
                    y - point_radius,
                    x + point_radius,
                    y + point_radius,
                ],
                fill="black",
            )

    # Draw each thread from center of start square to center of end square
    for thread in threads:
        color = thread.get("color", "black")

        # Support both old format (single start/end) and new format (paths list)
        if "paths" in thread:
            # New format: multiple paths per color
            paths = thread.get("paths", [])
            for path in paths:
                start = path.get("start", [0, 0])
                end = path.get("end", [0, 0])

                # Convert grid coordinates to pixel coordinates (center of each square)
                start_x = padding + start[0] * cell_size + cell_size / 2
                start_y = padding + start[1] * cell_size + cell_size / 2
                end_x = padding + end[0] * cell_size + cell_size / 2
                end_y = padding + end[1] * cell_size + cell_size / 2

                draw.line(
                    [(start_x, start_y), (end_x, end_y)],
                    fill=color,
                    width=thread_width,
                )
        else:
            # Old format: single start/end (backward compatibility)
            start = thread.get("start", [0, 0])
            end = thread.get("end", [0, 0])

            # Convert grid coordinates to pixel coordinates (center of each square)
            start_x = padding + start[0] * cell_size + cell_size / 2
            start_y = padding + start[1] * cell_size + cell_size / 2
            end_x = padding + end[0] * cell_size + cell_size / 2
            end_y = padding + end[1] * cell_size + cell_size / 2

            draw.line(
                [(start_x, start_y), (end_x, end_y)],
                fill=color,
                width=thread_width,
            )

    # Save the image
    img.save(output_file, "PNG")
    print(
        f"Created {output_file} with {width}x{height} mesh ({image_width}x{image_height} pixels)"
    )
    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an embroidery mesh PNG image")
    parser.add_argument(
        "--threads", "-t", type=str, help="YAML file with thread specifications"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=None,
        help="Number of cells per side (default: auto-calculate from threads)",
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=20,
        help="Size of each cell in pixels (default: 20)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="embroidery_mesh.png",
        help="Output PNG filename",
    )
    parser.add_argument(
        "--thread-width",
        type=int,
        default=3,
        help="Width of thread lines in pixels (default: 3)",
    )

    args = parser.parse_args()

    output = create_embroidery_mesh(
        size=args.size,
        cell_size=args.cell_size,
        line_width=1,
        output_file=args.output,
        threads_file=args.threads,
        thread_width=args.thread_width,
    )
    print(f"Mesh image saved as: {output}")
