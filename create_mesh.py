#!/usr/bin/env python3
"""
Creates a PNG image of a 40x40 mesh for embroidery.
"""

from PIL import Image, ImageDraw
import json
import os


def load_threads(threads_file):
    """
    Load thread specifications from a JSON file.

    Args:
        threads_file: Path to JSON file containing thread definitions

    Returns:
        List of thread dictionaries with 'color', 'start', and 'end' keys
    """
    if not os.path.exists(threads_file):
        return []

    with open(threads_file, "r") as f:
        data = json.load(f)
        return data.get("threads", [])


def create_embroidery_mesh(
    size=40,
    cell_size=20,
    line_width=1,
    output_file="embroidery_mesh.png",
    threads_file=None,
    thread_width=3,
):
    """
    Create a PNG image of an embroidery mesh grid.

    Args:
        size: Number of cells per side (default: 40)
        cell_size: Size of each cell in pixels (default: 20)
        line_width: Width of grid lines in pixels (default: 1)
        output_file: Output PNG filename
        threads_file: Optional path to JSON file with thread specifications
        thread_width: Width of thread lines in pixels (default: 3)
    """
    # Calculate image dimensions
    image_size = size * cell_size + 1  # +1 for the final line
    padding = 20  # Padding around the grid

    # Create image with white background
    img = Image.new(
        "RGB", (image_size + 2 * padding, image_size + 2 * padding), "white"
    )
    draw = ImageDraw.Draw(img)

    # Draw grid lines
    for i in range(size + 1):
        x = padding + i * cell_size
        y = padding + i * cell_size

        # Vertical lines
        draw.line(
            [(x, padding), (x, padding + image_size - 1)],
            fill="black",
            width=line_width,
        )

        # Horizontal lines
        draw.line(
            [(padding, y), (padding + image_size - 1, y)],
            fill="black",
            width=line_width,
        )

    # Optionally mark intersection points (stitch points)
    point_radius = 1
    for i in range(size + 1):
        for j in range(size + 1):
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

    # Draw threads from file if provided
    threads = []
    if threads_file:
        threads = load_threads(threads_file)

    # Draw each thread from center of start square to center of end square
    for thread in threads:
        color = thread.get("color", "black")
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
        f"Created {output_file} with {size}x{size} mesh ({image_size}x{image_size} pixels)"
    )
    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create an embroidery mesh PNG image")
    parser.add_argument(
        "--threads", "-t", type=str, help="JSON file with thread specifications"
    )
    parser.add_argument(
        "--size", type=int, default=40, help="Number of cells per side (default: 40)"
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
