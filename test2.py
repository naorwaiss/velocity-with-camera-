import asyncio
from camera import process_frames  # Adjusted to put data into a queue
from mavsdk import System

# ... Other function definitions ...

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    print("Waiting for drone to connect...")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    # Set up a queue for camera data
    camera_data_queue = asyncio.Queue()

    # Start process_frames as a background task
    camera_task = asyncio.create_task(process_frames(camera_data_queue))

    try:
        while True:
            # Get camera data from the queue
            x, y, z = await camera_data_queue.get()
            print(f"Received camera data: x={x}, y={y}, z={z}")

            # Process camera data (e.g., move drone based on x, y, z)
            # ...

    except asyncio.CancelledError:
        # This block will execute when camera_task is cancelled
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        camera_task.cancel()  # Cancel the background task on exit

if __name__ == "__main__":
    asyncio.run(main())
