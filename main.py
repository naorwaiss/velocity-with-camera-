import asyncio
from camera import process_frames,pixel_to_meters  # Import the process_frames function from the main script
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import time
from drone_mothion_function import (offboard,takeoff_velocity,camera_motion_simple,takeoff_presedoure)

async def check_camera_work(drone, camera_task, timeout_duration):
    try:
        # Wait for the camera to start with the provided timeout
        await asyncio.wait_for(camera_task, timeout=timeout_duration)
        print("Camera processing started")
        return True  # Camera started successfully
    except asyncio.TimeoutError:
        print("Camera did not start within the specified time, initiating landing.")
        # Camera did not start, land the drone
        await drone.action.land()
        return False


async def main():
    global x, y, z
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    await drone.action.hold()
    await takeoff_velocity(drone)  # Doing takeoff to 5-4 meters without GPS

    # Set up a queue for camera data
    camera_data_queue = asyncio.Queue()
    # Start process_frames as a background task
    camera_task = asyncio.create_task(process_frames(camera_data_queue))
    print("Start camera processing")

    # Check if the camera starts within a specified time (e.g., 10 seconds)
    camera_started = await check_camera_work(drone, camera_task, 10)
    if not camera_started:
        return  # Exit the main function as the drone is landing

    try:
        last_time = time.time()  # Record the initial time

        while True:
            current_time = time.time()
            elapsed = current_time - last_time  # Calculate elapsed time since last iteration
            last_time = current_time  # Update last_time for the next iteration

            # Get camera data from the queue
            x, y, z = await camera_data_queue.get()
            print(x, y, z)
            await camera_motion_simple(drone, x, y, z)

    except asyncio.CancelledError:
        # This block will execute when camera_task is cancelled
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
        await drone.action.hold()
        await asyncio.sleep(5)
        await drone.action.land()
    finally:
        camera_task.cancel()  # Cancel the background task on exit
        await drone.action.land()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Script manually interrupted")
    except Exception as e:
        print(f"Unhandled error: {e}")