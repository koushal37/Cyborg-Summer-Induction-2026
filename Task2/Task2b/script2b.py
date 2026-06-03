import cv2
import numpy as np

def map_arena():
    """
    Task 2B: Perspective Transformation and Coordinate Mapping
    """
    # Initialize the output dictionary
    result = {
        "corner_points_detected": [],
        "robot_pixel_coord": [],
        "robot_real_world_coord": []
    }

    # ==========================================
    # STEP 1: Corner Detection (Color Tracking)
    # ==========================================
    # TODO: Read the target image 'test_images/angled_arena.png'
    
    # TODO: Convert the image to HSV color space
    
    # TODO: Create HSV masks to isolate the Red, Green, Blue, and Yellow corners
    
    # TODO: Find contours for each mask and calculate the centroid (cx, cy) using moments (M["m10"] / M["m00"])
    
    # TODO: Store the coordinates in the exact order: [Top-Left(Red), Top-Right(Green), Bottom-Right(Blue), Bottom-Left(Yellow)]
    # result["corner_points_detected"] = [[cx_r, cy_r], [cx_g, cy_g], [cx_b, cy_b], [cx_y, cy_y]]


    image = cv2.imread('angled_arena.png')
    if image is None: image = cv2.imread('test_images/angled_arena.png')

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask_r = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255])) + cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
    mask_g = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
    mask_b = cv2.inRange(hsv, np.array([100, 150, 50]), np.array([140, 255, 255]))
    mask_y = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([30, 255, 255]))

    corners = []
    for mask in [mask_r, mask_g, mask_b, mask_y]:
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            M = cv2.moments(max(cnts, key=cv2.contourArea))
            if M["m00"] != 0: corners.append([int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])])
            else: corners.append([0,0])
        else: corners.append([0,0])

    result["corner_points_detected"] = corners

    # ==========================================
    # STEP 2: Perspective Transformation
    # ==========================================
    # TODO: Define your source points as a float32 numpy array (the 4 centroids calculated above)
    
    # TODO: Define your destination points as a flat 500x500 pixel square
    # Example: [[0,0], [500,0], [500,500], [0,500]]
    
    # TODO: Use cv2.getPerspectiveTransform() to calculate the 3x3 Homography Matrix
    
    # TODO: Apply cv2.warpPerspective() to flatten the angled arena into a 500x500 top-down view
    

    pts_src = np.float32(result["corner_points_detected"])
    pts_dst = np.float32([[0, 0], [500, 0], [500, 500], [0, 500]])

    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
    flat_image = cv2.warpPerspective(image, matrix, (500, 500))
    cv2.imwrite("birdsview.png", flat_image)

    # ==========================================
    # STEP 3: Robot Detection on Warped Arena
    # ==========================================
    # TODO: On the NEW warped 500x500 image, initialize an ArUco detector (DICT_4X4_50)
    
    # TODO: Detect the marker representing the robot (ID 1)
    
    # TODO: Calculate the center pixel coordinates (cx, cy) of the detected marker
    # result["robot_pixel_coord"] = [cx, cy]

    try:
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        marker_corners, ids, _ = detector.detectMarkers(flat_image)
    except AttributeError:
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters_create()
        marker_corners, ids, _ = cv2.aruco.detectMarkers(flat_image, dictionary, parameters=parameters)

    cx, cy = 0, 0
    if ids is not None:
        for i in range(len(ids)):
            if ids[i][0] == 1:
                mc = marker_corners[i][0]
                cx = int(np.mean(mc[:, 0]))
                cy = int(np.mean(mc[:, 1]))
                result["robot_pixel_coord"] = [cx, cy]
                break

    # ==========================================
    # STEP 4: Real-World Coordinate Conversion
    # ==========================================
    # Context: The 500x500 pixel warped image represents a physical arena of 200cm x 200cm.
    # The top-left corner is the origin [0.0, 0.0] cm.
    
    # TODO: Use linear scaling to convert the robot's pixel coordinates to real-world centimeters.
    # result["robot_real_world_coord"] = [x_cm, y_cm]
    if result["robot_pixel_coord"]:
        scale_factor = 200.0 / 500.0
        x_cm = float(cx * scale_factor)
        y_cm = float(cy * scale_factor)
        result["robot_real_world_coord"] = [round(x_cm, 1), round(y_cm, 1)]

    return result

if __name__ == "__main__":
    # Test your function
    output = map_arena()
    print("Task 2B Output:")
    print(output)