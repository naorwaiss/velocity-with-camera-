import asyncio
from camera import process_frames, pixel_to_meters, update_kalman_filter, initialize_kalman_filter
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityBodyYawspeed
import time
from drone_mothion_function import offboard, takeoff_velocity, camera_motion_simple, takeoff_presedoure,camera_motion_PID

async def check_camera_work(drone, camera_data_queue, timeout_duration):
    # this function not work

    try:
        # Wait for an indication that the camera is ready
        await asyncio.wait_for(camera_data_queue.get(), timeout=timeout_duration)
        print("Camera processing started")
        return True
    except asyncio.TimeoutError:
        print("Camera did not start within the specified time, initiating landing.")
        await drone.action.land()
        return False

async def camera_manipulation(x, y, z, kf):
    x_n, y_n = await pixel_to_meters(x, y, 87, 58, 640, 480, z)
    filtered_x, filtered_y = update_kalman_filter(kf, x_n, y_n)
    return filtered_x, filtered_y

async def main():
    # this is the main branch of the drone code
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    await drone.action.hold()
    await takeoff_velocity(drone)  # Doing takeoff to 5-4 meters without GPS

    filtered_x_prev= filtered_y_prev=0
    camera_data_queue = asyncio.Queue()
    camera_task = asyncio.create_task(process_frames(camera_data_queue))
    print("Start camera processing")

    camera_started = await check_camera_work(drone, camera_data_queue, 10)
    if not camera_started:
        return

    try:
        last_time = time.time()
        kf = initialize_kalman_filter()
        while True:
            current_time = time.time()
            elapsed = current_time - last_time
            last_time = current_time

            x, y, z = await camera_data_queue.get()
            filtered_x, filtered_y = await camera_manipulation(x, y, z, kf)




            #start the camera movment
            await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
            await offboard(drone)
            await camera_motion_PID(x,y,filtered_x,filtered_y,filtered_x_prev,filtered_y_prev,z,elapsed,drone)


            #stop the camera movment (need to wirte it )




            filtered_x_prev = filtered_x
            filtered_y_prev = filtered_y

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
        await drone.action.hold()
        await asyncio.sleep(5)
        await drone.action.land()
    finally:
        camera_task.cancel()
        await drone.action.land()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Script manually interrupted")
    except Exception as e:
        print(f"Unhandled error: {e}")
