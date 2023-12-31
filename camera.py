import asyncio
import cv2
import numpy as np
import pyrealsense2.pyrealsense2 as rs

async def process_frames(queue):
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

            if largest_obstacle is not None:
                x, y, w, h = cv2.boundingRect(largest_obstacle)
                center_x = x + w // 2
                center_y = y + h // 2
                depth_value = depth_frame.get_distance(center_x, center_y)

                cv2.drawContours(color_image, [largest_obstacle], -1, (0, 0, 255), 2)

                # Put the x, y, z coordinates into the queue
                await queue.put((center_x, center_y, depth_value))

            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pipeline.stop()
