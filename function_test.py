import time
import asyncio
from camera import process_frames  # Make sure this is the correct path to your camera module
import math


# for d435: fov_horizontal=87 and fov_vertical = 58 //
# this function not work yet



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






async def print_coordinates():
    queue = asyncio.Queue()
    frame_processor_task = asyncio.create_task(process_frames(queue))  # Start processing frames in a separate task

    try:
        last_time = time.time()  # Record the initial time

        while True:
            current_time = time.time()
            elapsed = current_time - last_time  # Calculate elapsed time since last iteration
            last_time = current_time  # Update last_time for the next iteration

            x, y, z = await queue.get()  # Get x, y, z values from the queue
            x_n,y_n = await pixel_to_meters(x,y,87,58,640,480,z)
            hertz = 1/elapsed
            print(f"Time elapsed: {hertz:.2f} hertz, Coordinates: X={x_n}, Y={y_n}, Z={z}")

            # Optional: Insert a fixed delay if required
            # await asyncio.sleep(some_delay)

    except asyncio.CancelledError:
        pass  # Handle cancellation of the task
    finally:
        frame_processor_task.cancel()  # Ensure the frame processing task is cancelled when done

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(print_coordinates())
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt
    finally:
        loop.close()  # Close the loop
