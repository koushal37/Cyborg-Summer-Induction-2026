from math import dist
from unittest import result

import cv2
import numpy as np
import glob

def localize_bot():
    """
    Task 2A: Camera Calibration and ArUco Pose Estimation
    """
    # Initialize the output dictionary with exact keys required by the evaluator
    result = {
        "camera_matrix_trace": 0.0,
        "markers": {}
    }

    # ==========================================
    # STEP 1: Camera Calibration
    # ==========================================
    # TODO: Define the real-world 3D coordinates for the checkerboard corners (9x6 grid, 2.5cm square size)
    
    # TODO: Use glob to read all images from the 'calibration_images' folder
    
    # TODO: Loop through the images, convert to grayscale, and use cv2.findChessboardCorners()
    
    # TODO: Use cv2.calibrateCamera() to calculate the camera matrix (mtx) and distortion coefficients (dist)
    
    # TODO: Calculate the trace of the camera matrix (sum of the main diagonal elements)
    # result["camera_matrix_trace"] = round(trace_value, 2)
    CHECKERBOARD = (9, 6)
    square_size = 2.5 
    
    objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2) * square_size

    objpoints = [] 
    imgpoints = [] 
    
    # Load and explicitly sort the image paths for deterministic output
    images = sorted(glob.glob('calibration_images/*.jpg') + glob.glob('calibration_images/*.png'))
    
    # Criteria for sub-pixel accuracy (REQUIRED for evaluator exact-match)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    gray_shape = None
    for fname in images:
        img = cv2.imread(fname)
        if img is None:
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_shape = gray.shape[::-1]
        
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)

        if ret == True:
            # Refine corner detection for mathematically perfect camera calibration
            corners_refined = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            objpoints.append(objp)
            imgpoints.append(corners_refined)

    if len(objpoints) > 0:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray_shape, None, None)
        trace_value = float(np.trace(mtx))
        result["camera_matrix_trace"] = round(trace_value, 2) 
    else:
        print("Error: No checkerboard corners detected in calibration images.")
        return result

    # ==========================================
    # STEP 2: Image Undistortion
    # ==========================================
    # TODO: Read the target image 'test_images/test_arena.png'
    
    # TODO: Use cv2.undistort() with your calculated mtx and dist to fix the image
    img_path = 'test_images/test_arena.png'
    raw_image = cv2.imread(img_path)
    
    
    if raw_image is None: raw_image = cv2.imread('test_arena.png')
    if raw_image is None: raw_image = cv2.imread('test_arena.jpg')

    if raw_image is not None:
        
        fixed_image = cv2.undistort(raw_image, mtx, dist)
    else:
        print("Error: Target test image could not be loaded.")
        return result

    # ==========================================
    # STEP 3: ArUco Detection & Pose Estimation
    # ==========================================
    # TODO: Initialize the ArUco detector for DICT_4X4_50
    
    # TODO: Detect markers in the UNDISTORTED image
    
    # TODO: For each detected marker, use cv2.solvePnP() to estimate its pose
    # Hint: You need the real-world 3D coordinates of the marker corners (Marker size is 5.0 cm)
    
    # TODO: Extract the z-distance and x-offset from the translation vector (tvec)
    
    try:
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        corners, ids, rejected = detector.detectMarkers(fixed_image)
    except AttributeError:
        try:
            dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters_create()
        except AttributeError:
            dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, rejected = cv2.aruco.detectMarkers(fixed_image, dictionary, parameters=parameters)
    
    if ids is not None:
        marker_size = 5.0  # 5.0 cm
        
        # Standard OpenCV Coordinate System for ArUco
        marker_3d_edges = np.array([
            [-marker_size / 2.0,  marker_size / 2.0, 0], # Top-Left
            [ marker_size / 2.0,  marker_size / 2.0, 0], # Top-Right
            [ marker_size / 2.0, -marker_size / 2.0, 0], # Bottom-Right
            [-marker_size / 2.0, -marker_size / 2.0, 0]  # Bottom-Left
        ], dtype=np.float32)

        for i in range(len(ids)):
            m_id = int(ids[i][0])
            marker_corners_2d = corners[i][0]
            
            success, rvec, tvec = cv2.solvePnP(marker_3d_edges, marker_corners_2d, mtx, dist)
            
            if success:
                x_offset = float(tvec[0][0])  
                distance_z = float(tvec[2][0])  
                
                result["markers"][f"id_{m_id}"] = {
                    "distance_z": round(distance_z, 1),
                    "x_offset": round(x_offset, 1)
                }
    # ==========================================
    # SORT MARKERS BY ARUCO ID
    # ==========================================
    result["markers"] = dict(

        sorted(

            result["markers"].items(),

            key=lambda item: int(
                item[0].split("_")[1]
            ),
            reverse=True
        )

    )

    # ==========================================
    # RETURN FINAL OUTPUT
    # ==========================================

    return result

if __name__ == "__main__":
    # Test your function
    output = localize_bot()
    print("Task 2A Output:")
    print(output)