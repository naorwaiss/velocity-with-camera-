import time
import asyncio
import math
import numpy as np
from filterpy.kalman import KalmanFilter
from camera import process_frames  # Make sure this is the correct path to your camera module
from camera import pixel_to_meters
from notebook import crate_notepad, save_to_note_pads


async def save_data( Vx, Vy, delta_t):
    await save_to_note_pads(delta_t, 'delta_t.txt')
    await save_to_note_pads(Vx, 'Vx.txt')
    await save_to_note_pads(Vx, 'Vy.txt')



def initialize_kalman_filter():
    # Create a new Kalman Filter instance - need to learn it little bit more deep becuse this is right now like black box
    kf = KalmanFilter(dim_x=2, dim_z=2)  # Assuming 2D coordinates (x, y)

    # Configure the Kalman filter parameters
    kf.F = np.array([[1, 0], [0, 1]])  # State transition matrix
    kf.H = np.array([[1, 0], [0, 1]])  # Measurement function
    kf.R = np.eye(2) * 0.1             # Measurement uncertainty
    kf.Q = np.eye(2) * 0.1             # Process noise
    kf.P = np.eye(2) * 1               # Initial estimation uncertainty

    return kf

def update_kalman_filter(kf, x_n, y_n):
    kf.predict()  # Predict the next state
    kf.update([x_n, y_n])  # Update with the new measurements

    filtered_x, filtered_y =kf.x[0], kf.x[1]
    return filtered_x, filtered_y

async def pixel_to_meters(x_pixel, y_pixel, fov_horizontal, fov_vertical, image_width, image_height, distance_to_object):
    # Calculate the angle per pixel for both horizontal and vertical FOVs
    angle_per_pixel_x = fov_horizontal / image_width
    angle_per_pixel_y = fov_vertical / image_height

    # Calculate the angle offset from the center
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
    #this function is a test function -- only for the example



    kf = initialize_kalman_filter()
    queue = asyncio.Queue()
    frame_processor_task = asyncio.create_task(process_frames(queue))
    filtered_x_prev = filtered_y_prev = 0
    try:
        last_time = time.time()
        await crate_notepad()  # need to check if the textfile is open ??
        while True:
            current_time = time.time()
            elapsed = current_time - last_time
            last_time = current_time

            x, y, z = await queue.get()
            x_n, y_n = await pixel_to_meters(x, y, 87, 58, 640, 480, z)
            filtered_x, filtered_y = update_kalman_filter(kf, x_n, y_n)
            print (filtered_x,filtered_y,elapsed)
            await save_data(x_n,y_n,elapsed)


    except asyncio.CancelledError:
        pass
    finally:
        frame_processor_task.cancel()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(print_coordinates())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
