import os
import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import asyncio

os.environ["DISPLAY"] = ":0.0"

async def process_frames():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline.start(config)

    try:
        while True:
            frames = await asyncio.to_thread(pipeline.wait_for_frames)
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)

            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            largest_area = 0
            largest_obstacle = None

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area:
                    largest_area = area
                    largest_obstacle = contour

            # Find the center of the image
            height, width, _ = color_image.shape
            center_of_image_x = width // 2
            center_of_image_y = height // 2

            if largest_obstacle is not None:
                x, y, w, h = cv2.boundingRect(largest_obstacle)
                center_x = x + w // 2
                center_y = y + h // 2

                # Adjusting to make the center of the image (0, 0)
                adjusted_center_x = center_x - center_of_image_x
                adjusted_center_y = center_y - center_of_image_y

                depth_value = depth_frame.get_distance(center_x, center_y)

                cv2.drawContours(color_image, [largest_obstacle], -1, (0, 255, 0), 3)  # Draw contour in green for visibility

                # Yield the adjusted center coordinates and depth
                yield adjusted_center_x, adjusted_center_y, depth_value
            else:
                # Yield (0, 0, 0) if no red object is detected
                yield 0, 0, 0

            # Display the video feed with contours
            cv2.imshow('RealSense Color Feed', color_image)

            await asyncio.sleep(0.01)
            key = cv2.waitKey(1)
            if key == 27:  # 'Esc' key to exit
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(process_frames())
