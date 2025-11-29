#!/usr/bin/env python3
"""Generate 6x8 grid with 9 threads per unit (5x5 each)"""

# Base pattern: 9 threads from upper left corner
# [0,1] to [1,0], [0,2] to [2,0], [0,3] to [3,0], [0,4] to [4,0], [0,5] to [5,0]
# [1,5] to [5,1], [2,5] to [5,2], [3,5] to [5,3], [4,5] to [5,4]
base_paths = [
    {'start': [0, 1], 'end': [1, 0]},
    {'start': [0, 2], 'end': [2, 0]},
    {'start': [0, 3], 'end': [3, 0]},
    {'start': [0, 4], 'end': [4, 0]},
    {'start': [0, 5], 'end': [5, 0]},
    {'start': [1, 5], 'end': [5, 1]},
    {'start': [2, 5], 'end': [5, 2]},
    {'start': [3, 5], 'end': [5, 3]},
    {'start': [4, 5], 'end': [5, 4]},
]

def transform_path(path, row_parity, col_parity, unit_size=5):
    """Transform a path based on grid position orientation"""
    x, y = path['start']
    x_end, y_end = path['end']

    if row_parity == 0 and col_parity == 0:
        # (0, 0): upper left to lower right - use as is
        return {'start': [x, y], 'end': [x_end, y_end]}
    elif row_parity == 0 and col_parity == 1:
        # (0, 1): upper right to lower left - mirror horizontally
        return {'start': [unit_size - x, y], 'end': [unit_size - x_end, y_end]}
    elif row_parity == 1 and col_parity == 0:
        # (1, 0): lower left to upper right - mirror both axes
        return {'start': [x, unit_size - y], 'end': [x_end, unit_size - y_end]}
    else:  # row_parity == 1 and col_parity == 1
        # (1, 1): upper left to lower right - use as is
        return {'start': [x, y], 'end': [x_end, y_end]}

# Generate 6x8 grid (6 columns, 8 rows)
threads = []
for row in range(8):  # rows 0-7
    for col in range(6):  # columns 0-5
        x_offset = col * 5
        y_offset = row * 5
        # Checkerboard pattern: red if (row + col) is even, blue otherwise
        color = 'red' if (row + col) % 2 == 0 else 'blue'

        row_parity = row % 2
        col_parity = col % 2

        # Transform base paths and apply translation
        unit_paths = []
        for base_path in base_paths:
            transformed = transform_path(base_path, row_parity, col_parity)
            unit_paths.append({
                'start': [transformed['start'][0] + x_offset, transformed['start'][1] + y_offset],
                'end': [transformed['end'][0] + x_offset, transformed['end'][1] + y_offset]
            })

        threads.append({
            'color': color,
            'paths': unit_paths
        })

# Write YAML file
yaml_content = "threads:\n"
for i, thread in enumerate(threads):
    row = i // 6 + 1  # 1-indexed for display
    col = i % 6 + 1   # 1-indexed for display
    actual_row = i // 6  # 0-indexed for logic
    actual_col = i % 6   # 0-indexed for logic

    # Format comment similar to existing file
    if row == 1:
        col_desc = 'left' if col == 1 else 'middle' if col == 3 or col == 4 else 'right' if col == 6 else f'col-{col}'
        comment = f"  # Unit {col},{row} (top-{col_desc})\n"
    elif row == 8:
        col_desc = 'left' if col == 1 else 'middle' if col == 3 or col == 4 else 'right' if col == 6 else f'col-{col}'
        comment = f"  # Unit {col},{row} (bottom-{col_desc})\n"
    else:
        col_desc = 'left' if col == 1 else 'middle' if col == 3 or col == 4 else 'right' if col == 6 else f'col-{col}'
        row_names = {2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh'}
        row_desc = row_names.get(row, f'{row}th')
        comment = f"  # Unit {col},{row} ({row_desc} row, {col_desc})\n"

    yaml_content += comment
    yaml_content += f"  - color: {thread['color']}\n"
    yaml_content += "    paths:\n"

    x_offset = actual_col * 5
    y_offset = actual_row * 5

    # Add translation comment if needed
    if x_offset > 0 or y_offset > 0:
        trans_parts = []
        if x_offset > 0:
            trans_parts.append(f"+{x_offset} in x")
        if y_offset > 0:
            trans_parts.append(f"+{y_offset} in y")
        trans_comment = f" (translated {' and '.join(trans_parts)})"
        yaml_content += f"      # Threads{trans_comment}\n"

    # Output all 9 paths
    for path in thread['paths']:
        yaml_content += f"      - start: [{path['start'][0]}, {path['start'][1]}]\n"
        yaml_content += f"        end: [{path['end'][0]}, {path['end'][1]}]\n"

with open('threebyfour.yaml', 'w') as f:
    f.write(yaml_content)

print('Generated 6x8 grid with 48 units (each unit has 9 threads in a 5x5 grid)')
