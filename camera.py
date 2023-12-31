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

    # Open a video window
    cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Video Stream", 640, 480)

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
                # Calculate x, y, z coordinates from the center of the largest red object
                M = cv2.moments(largest_obstacle)
                if M["m00"] != 0:
                    center_x = int(M["m10"] / M["m00"])
                    center_y = int(M["m01"] / M["m00"])
                    depth_value = depth_frame.get_distance(center_x, center_y)

                    # Mark the center of all pixels belonging to the red object
                    cv2.drawContours(color_image, [largest_obstacle], -1, (0, 0, 255), 2)
                    cv2.circle(color_image, (center_x, center_y), 5, (0, 255, 0), -1)

                    # Put the x, y, z coordinates into the queue
                    await queue.put((center_x, center_y, depth_value))

            cv2.imshow("Video Stream", color_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            await asyncio.sleep(0.01)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pipeline.stop()
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
