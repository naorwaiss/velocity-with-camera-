import asyncio
import cv2
import numpy as np
import pyrealsense2.pyrealsense2 as rs
import os
import math
from filterpy.kalman import KalmanFilter
from scipy.signal import butter, lfilter


# this code is finish
# At the Jetson, if the code runs from the console -- need: import pyrealsense2 as rs

# os.environ["DISPLAY"] = ":0.0" #need add only at the jetson

async def pixel_to_meters(x_pixel, y_pixel, fov_horizontal, fov_vertical, image_width, image_height, distance_to_object):
    # for d435: fov_horizontal=87 and fov_vertical = 58
    # for l515: fov_horizontal = 70 and fov_vertical = 55
    # this function is work


    # Calculate the angle per pixel for both horizontal and vertical FOVs
    angle_per_pixel_x = fov_horizontal / image_width
    angle_per_pixel_y = fov_vertical / image_height

    # Calculate the angle offset from the center
    # Assuming x_pixel and y_pixel are already the distances from the center
    angle_offset_x = x_pixel * angle_per_pixel_x
    angle_offset_y = y_pixel * angle_per_pixel_y

    # Convert angle to radians
    angle_offset_x_radians = math.radians(angle_offset_x)
    angle_offset_y_radians = math.radians(angle_offset_y)

    # Use trigonometry to calculate the offset in meters
    x_meters = math.tan(angle_offset_x_radians) * distance_to_object
    y_meters = math.tan(angle_offset_y_radians) * distance_to_object

    return x_meters, y_meters


async def butter_lowpass_filter(prev_value, current_value, order=1):
    cutoff_frequency = 6  # Adjust this value based on your requirements

    nyquist = 0.5
    normal_cutoff = cutoff_frequency / nyquist

    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    # Apply the filter using lfilter
    # Pass the last known value as the initial condition for continuity
    filtered_value = lfilter(b, a, [current_value], zi=[prev_value])[0]

    # Extract the scalar value from the NumPy array and round to the nearest integer
    return filtered_value[0]



async def process_frames(queue):
    pipeline = rs.pipeline()
    config = rs.config()
    # Configure streams
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Set up the path for video saving

    desktop_path = '/home/naor/Desktop'   #change this line to the jetson
    #desktop_path = '/home/drone/Desktop'
    video_path = os.path.join(desktop_path, 'output.avi')

    # Open a video window - need to check if it work at the jeton
    cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Video Stream", 640, 480)

    # Set up the VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = await asyncio.to_thread(pipeline.wait_for_frames)
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

            # Calculate the center of the image
            height, width, _ = color_image.shape
            center_x, center_y = width // 2, height // 2

            # Draw a blue dot at the center
            cv2.circle(color_image, (center_x, center_y), 5, (255, 0, 0), -1)

            # Define the range of red color in HSV
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])

            # Threshold the HSV image to get only red colors
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)

            # Morphological operations to remove noise
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            largest_area = 0
            largest_obstacle = None

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area:
                    largest_area = area
                    largest_obstacle = contour

            # Check if a largest obstacle is found
            if largest_obstacle is not None:
                M = cv2.moments(largest_obstacle)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    depth_value = depth_frame.get_distance(center_x, center_y)

                    # Adjust coordinates to be relative to the center of the frame
                    adjusted_x = center_x - 320
                    adjusted_y = 240 - center_y

                    # Mark the center
                    cv2.drawContours(color_image, [largest_obstacle], -1, (0, 0, 255), 2)
                    cv2.circle(color_image, (center_x, center_y), 5, (0, 255, 0), -1)

                    # Put the adjusted coordinates into the queue
                    await queue.put((adjusted_x, adjusted_y, depth_value))
                else:
                    await queue.put((0, 0, 0))
            else:
                # No red contour found, output (0,0,0)
                await queue.put((0, 0, 0))

            # Show the image
            cv2.imshow("Video Stream", color_image)

            # Save the frame to the video file
            out.write(color_image)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Stop streaming
        pipeline.stop()
        # Release the VideoWriter object
        out.release()
        # Close all OpenCV windows
        cv2.destroyAllWindows()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    try:
        loop.run_until_complete(process_frames(queue))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
