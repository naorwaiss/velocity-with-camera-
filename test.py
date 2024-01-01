
# check only the camera fonctionalaty

import asyncio
from camera import process_frames  # Make sure this is the correct path to your file

async def print_coordinates():
    queue = asyncio.Queue()
    frame_processor_task = asyncio.create_task(process_frames(queue))  # Start processing frames in a separate task

    try:
        while True:
            x, y, z = await queue.get()  # Get x, y, z values from the queue
            print(f"Coordinates: X={x}, Y={y}, Z={z}")  # Print the coordinates
    except asyncio.CancelledError:
        pass  # Handle cancellation of the task
    finally:
        frame_processor_task.cancel()  # Ensure the frame processing task is cancelled when done

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(print_coordinates())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
