import cv2
import numpy as np

def get_centroid(mask):
    """Helper function to extract the (x,y) center of a binary mask."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Get largest contour in case of noise
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return [cx, cy]
    return [0, 0]

def map_arena():
    result = {
        "corner_points_detected": [],
        "robot_pixel_coord": [],
        "robot_real_world_coord": []
    }

    # ==========================================
    # STEP 1: Corner Detection (Color Tracking)
    # ==========================================
    img = cv2.imread('test_images/angled_arena.png')
    if img is None:
        return result

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Note: Red hues wrap around 0 and 180 in OpenCV, so it requires two masks
    mask_red1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    mask_red2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
    mask_red = mask_red1 | mask_red2
    
    mask_green = cv2.inRange(hsv, np.array([40, 100, 100]), np.array([80, 255, 255]))
    mask_blue = cv2.inRange(hsv, np.array([100, 100, 100]), np.array([140, 255, 255]))
    mask_yellow = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([35, 255, 255]))

    # Extract centroids
    tl = get_centroid(mask_red)     # Top-Left
    tr = get_centroid(mask_green)   # Top-Right
    br = get_centroid(mask_blue)    # Bottom-Right
    bl = get_centroid(mask_yellow)  # Bottom-Left

    result["corner_points_detected"] = [tl, tr, br, bl]

    # ==========================================
    # STEP 2: Perspective Transformation
    # ==========================================
    pts_src = np.float32([tl, tr, br, bl])
    
    # Map the angled corners to a perfect 500x500 square
    pts_dst = np.float32([[0, 0], [500, 0], [500, 500], [0, 500]])

    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
    warped = cv2.warpPerspective(img, matrix, (500, 500))

    # ==========================================
    # STEP 3 & 4: Robot Detection & Real-World Mapping
    # ==========================================
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    corners, ids, _ = detector.detectMarkers(warped)
    
    if ids is not None:
        for i in range(len(ids)):
            if ids[i][0] == 1: # We are looking for Robot ID 1
                # Find the center of the marker by averaging its 4 corners
                c = corners[i][0]
                cx = int(np.mean(c[:, 0]))
                cy = int(np.mean(c[:, 1]))
                result["robot_pixel_coord"] = [cx, cy]

                # Scale pixels to cm. 500 pixels = 200 cm. (Scale factor: 200/500 = 0.4)
                x_cm = round(cx * 0.4, 1)
                y_cm = round(cy * 0.4, 1)
                result["robot_real_world_coord"] = [float(x_cm), float(y_cm)]
                break

    return result

if __name__ == "__main__":
    print(map_arena())