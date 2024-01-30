import time
import asyncio
import math
from scipy.signal import butter, lfilter
from camera import process_frames  # Make sure this is the correct path to your camera module
from camera import pixel_to_meters
from notebook import crate_notepad, save_to_note_pads



async def save_data(Vx, Vy, delta_t):
    await save_to_note_pads(delta_t, 'delta_t.txt')
    await save_to_note_pads(Vx, 'Vx.txt')
    await save_to_note_pads(Vy, 'Vy.txt')



async def butter_lowpass_filter(prev_value, current_value, n_time, order=1):
    cutoff_frequency = 6  # Adjust this value based on your requirements

    # Ensure cutoff_frequency is within a reasonable range
    if cutoff_frequency <= 0:
        raise ValueError("Cutoff frequency must be greater than 0")

    normal_cutoff = cutoff_frequency / n_time

    # Print the calculated normal_cutoff for debugging
    print("Normal Cutoff:", normal_cutoff)

    # Check if normal_cutoff is within the valid range (0 < Wn < 1)
    if normal_cutoff <= 0 or normal_cutoff >= 1:
        raise ValueError("Digital filter critical frequencies must be 0 < Wn < 1")

    b, a = butter(order, normal_cutoff, btype='low', analog=False)

    # Apply the filter using lfilter
    # Pass the last known value as the initial condition for continuity
    filtered_value = lfilter(b, a, [current_value], zi=[prev_value])[0]

    # Extract the scalar value from the NumPy array and round to the nearest integer
    return filtered_value[0]

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
    frame_processor_task = asyncio.create_task(process_frames(queue))
    filtered_x_prev = filtered_y_prev = 0

    try:
        last_time = time.time()
        await crate_notepad()  # need to check if the textfile is open ??

        while True:
            current_time = time.time()
            elapsed = current_time - last_time


            if elapsed <= 0.0001:  # Adjust the threshold as needed
                # Handle the case where elapsed is too small
                continue


            last_time = current_time

            x, y, z = await queue.get()
            nyquist = 1/(2*elapsed)

            x_n, y_n = await pixel_to_meters(x, y, 87, 58, 640, 480, z)
            filtered_x = await butter_lowpass_filter(filtered_x_prev, x_n,nyquist)
            filtered_y = await butter_lowpass_filter(filtered_y_prev, y_n,nyquist)

            print(filtered_x,filtered_y)

            filtered_x_prev = filtered_x
            filtered_y_prev = filtered_y

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
