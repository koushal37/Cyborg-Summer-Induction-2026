#!/usr/bin/env python3
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
    # WRITE YOUR LOGIC BELOW
    # ==========================================
   

    
    img_src = None
    for var_name in ['image_path', 'image', 'input_image', 'img', 'frame']:
        if var_name in locals() or var_name in globals():
            val = locals().get(var_name, globals().get(var_name))
            if isinstance(val, str):
                img_src = cv2.imread(val)
                break
            elif isinstance(val, np.ndarray):
                img_src = val.copy()
                break
            
    if img_src is not None:
        H, W = img_src.shape[:2]
        gray = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
        
      
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        cell_boxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            
            if 10 < w < W * 0.5 and 10 < h < H * 0.5:
                aspect_ratio = float(w) / h
                if 0.85 <= aspect_ratio <= 1.15:
                    cell_boxes.append((x, y, w, h))
                    
        if len(cell_boxes) > 0:
            
            grid_x1 = min([box[0] for box in cell_boxes])
            grid_y1 = min([box[1] for box in cell_boxes])
            grid_x2 = max([box[0] + box[2] for box in cell_boxes])
            grid_y2 = max([box[1] + box[3] for box in cell_boxes])
            grid_w = grid_x2 - grid_x1
            grid_h = grid_y2 - grid_y1
            
            
            widths = [box[2] for box in cell_boxes]
            median_w = np.median(widths)
            estimated_size = grid_w / median_w
            arena_size = min([6, 8, 10, 12], key=lambda x: abs(x - estimated_size))
        else:
            
            grid_x1, grid_y1, grid_w, grid_h = 0, 0, W, H
            arena_size = 10
            
        result["arena_size"] = arena_size
        cell_w = grid_w / arena_size
        cell_h = grid_h / arena_size

       
        hsv_image = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
        
        color_masks = {
            "DANGER": [(np.array([0, 40, 40]), np.array([10, 255, 255])),
                       (np.array([170, 40, 40]), np.array([180, 255, 255]))],
            "SLOW":   [(np.array([11, 40, 40]), np.array([25, 255, 255]))],
            "START":  [(np.array([26, 40, 40]), np.array([35, 255, 255]))],
            "SAFE":   [(np.array([36, 40, 40]), np.array([85, 255, 255]))],
            "GOAL":   [(np.array([86, 40, 40]), np.array([105, 255, 255]))],
            "REFUEL": [(np.array([106, 40, 40]), np.array([140, 255, 255]))]
        }

        result["special_cells"] = {}
        result["start"] = None
        result["goal"] = None

        
        for row_idx in range(arena_size):
            for col_idx in range(arena_size):
                
                
                x1 = int(grid_x1 + col_idx * cell_w)
                x2 = int(grid_x1 + (col_idx + 1) * cell_w)
                y1 = int(grid_y1 + row_idx * cell_h)
                y2 = int(grid_y1 + (row_idx + 1) * cell_h)
                
                cw = x2 - x1
                ch = y2 - y1
                
                
                roi_hsv = hsv_image[int(y1 + ch * 0.2):int(y2 - ch * 0.2), int(x1 + cw * 0.2):int(x2 - cw * 0.2)]
                
                if roi_hsv.size == 0:
                    continue
                    
                roi_area = roi_hsv.shape[0] * roi_hsv.shape[1]
                
                col_letter = chr(ord('A') + col_idx)
                row_number = str(arena_size - row_idx)
                coordinate = f"{col_letter}{row_number}"
                
                best_color = None
                max_count = 0
                
                
                for color_name, masks in color_masks.items():
                    count = 0
                    for lower, upper in masks:
                        mask = cv2.inRange(roi_hsv, lower, upper)
                        count += cv2.countNonZero(mask)
                    if count > max_count:
                        max_count = count
                        best_color = color_name
                
                
                if max_count > max(12, int(roi_area * 0.02)):
                    if best_color == "START":
                        result["start"] = coordinate
                    elif best_color == "GOAL":
                        result["goal"] = coordinate
                    else:
                        result["special_cells"][coordinate] = best_color
    '''
    Steps you may follow:

    1. Detect arena size
    2. Divide arena into grid cells
    3. Convert image to HSV 
    4. Detect START cell
    5. Detect GOAL cell
    6. Detect special colored cells
    7. Map cells to arena coordinates
    8. Store outputs in result dictionary

    Color Meaning
    Red : Danger Zone
    Green : Safe Zone
    Blue : Refuel Station
    Orange : Slow Terrain
    Yellow : Start Position
    Cyan : Goal Position
    '''
    # Example:

    # result["arena_size"] = 8
    # result["start"] = "A1"
    # result["goal"] = "H8"

    # result["special_cells"]["B2"] = "DANGER"
    # result["special_cells"]["D5"] = "SAFE"

    # ==========================================
    # SORT SPECIAL CELLS
    # ==========================================

    sorted_cells = dict(

        sorted(

            result["special_cells"].items(),

            key=lambda item: (

                item[0][0],
                int(item[0][1:])

            )
        )
    )

    result["special_cells"] = sorted_cells

    # ==========================================
    # RETURN FINAL OUTPUT
    # ==========================================

    return result