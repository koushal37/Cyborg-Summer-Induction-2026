# script.py
import cv2
import numpy as np


def analyze_arena(input_image):

    # ==========================================
    # LOAD IMAGE
    # ==========================================

    image = cv2.imread(input_image)

    if image is None:

        print("Error loading image.")
        return {}

    # ==========================================
    # INITIALIZE OUTPUT
    # ==========================================

    result = {

        "arena_size": None,
        "start": None,
        "goal": None,
        "special_cells": {}

    }

    # ==========================================
    # ARENA CONFIGURATION
    # ==========================================

    MARGIN = 40
    CELL_SIZE = 80

    height, width = image.shape[:2]

    # Detect arena size
    arena_pixels = width - (2 * MARGIN)

    grid_size = arena_pixels // CELL_SIZE

    result["arena_size"] = int(grid_size)

    # ==========================================
    # CONVERT IMAGE TO HSV
    # ==========================================

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # ==========================================
    # HSV COLOR RANGES
    # ==========================================

    color_ranges = {

        "DANGER": [
            ((0, 120, 120), (10, 255, 255)),
            ((160, 120, 120), (180, 255, 255))
        ],

        "SAFE": [
            ((35, 80, 80), (85, 255, 255))
        ],

        "REFUEL": [
            ((90, 80, 80), (130, 255, 255))
        ],

        "SLOW": [
            ((10, 120, 120), (25, 255, 255))
        ]

    }

    # ==========================================
    # START / GOAL COLOR RANGES
    # ==========================================

    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([35, 255, 255])

    cyan_lower = np.array([80, 100, 100])
    cyan_upper = np.array([100, 255, 255])

    # ==========================================
    # LOOP THROUGH GRID CELLS
    # ==========================================

    for row in range(grid_size):

        for col in range(grid_size):

            # ==========================================
            # CELL BOUNDARIES
            # ==========================================

            x1 = MARGIN + col * CELL_SIZE
            y1 = MARGIN + row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # Extract cell
            cell = hsv[y1:y2, x1:x2]

            # ==========================================
            # CENTER REGION
            # ==========================================

            center = cell[25:55, 25:55]

            # Mean HSV value
            mean_hsv = np.mean(center, axis=(0, 1))

            # ==========================================
            # GRID COORDINATES
            # ==========================================

            arena_row = grid_size - row
            arena_col = chr(ord('A') + col)

            coordinate = f"{arena_col}{arena_row}"

            # ==========================================
            # DETECT START CELL
            # ==========================================

            yellow_mask = cv2.inRange(
                center,
                yellow_lower,
                yellow_upper
            )

            yellow_pixels = cv2.countNonZero(yellow_mask)

            if yellow_pixels > 50:
                result["start"] = coordinate

            # ==========================================
            # DETECT GOAL CELL
            # ==========================================

            cyan_mask = cv2.inRange(
                center,
                cyan_lower,
                cyan_upper
            )

            cyan_pixels = cv2.countNonZero(cyan_mask)

            if cyan_pixels > 50:
                result["goal"] = coordinate

            # ==========================================
            # DETECT SPECIAL CELLS
            # ==========================================

            for zone_name, ranges in color_ranges.items():

                detected = False

                for lower, upper in ranges:

                    lower = np.array(lower)
                    upper = np.array(upper)

                    if np.all(mean_hsv >= lower) and np.all(mean_hsv <= upper):

                        result["special_cells"][coordinate] = zone_name

                        detected = True
                        break

                if detected:
                    break

    # ==========================================
    # SORT SPECIAL CELLS
    # ==========================================

    sorted_cells = dict(

        sorted(

            result["special_cells"].items(),

            key=lambda item: (

                item[0][0],          # Column letter
                int(item[0][1:])     # Row number

            )
        )
    )

    result["special_cells"] = sorted_cells

    # ==========================================
    # RETURN FINAL OUTPUT
    # ==========================================

    return result