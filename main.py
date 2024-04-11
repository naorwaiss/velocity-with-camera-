import asyncio
from camera import process_frames, pixel_to_meters,butter_lowpass_filter
from mavsdk import System
from mavsdk.offboard import OffboardError, VelocityBodyYawspeed
import time
from drone_mothion_function import offboard, takeoff_velocity, odomety, takeoff_presedoure,movment_camera
from notebook import crate_notepad, save_to_note_pads



async def check_camera_work(drone, camera_data_queue, timeout_duration):
    # this function not work - need to fix it

    try:
        # Wait for an indication that the camera is ready
        await asyncio.wait_for(camera_data_queue.get(), timeout=timeout_duration)
        print("Camera processing started")
        return True
    except asyncio.TimeoutError:
        print("Camera did not start within the specified time, initiating landing.")
        await drone.action.land()
        return False




async def save_data(drone,Vx,Vy,delta_t,Vx_current,Vy_current):
            await save_to_note_pads(delta_t, 'delta_t.txt')
            await save_to_note_pads(Vx,'Vx.txt')
            await save_to_note_pads(Vy, 'Vy.txt')
            await save_to_note_pads(Vx_current,'Vx_current.txt')
            await save_to_note_pads(Vy_current, 'Vy_current.txt')




async def main():
    # this is the main branch of the drone code -
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    await drone.action.hold()
    await takeoff_velocity(drone)  # Doing takeoff to 5-4 meters without GPS
    await asyncio.sleep(5)


    camera_data_queue = asyncio.Queue()
    camera_task = asyncio.create_task(process_frames(camera_data_queue))
    print("Start camera processing")

    camera_started = await check_camera_work(drone, camera_data_queue, 10)
    if not camera_started:
        #await drone.action.land()??
        return

    try:
        last_time = time.time()

        await crate_notepad() #need to check if the textfile is open ??
        filtered_x_prev=filtered_y_prev =0
        Error_x_prev= Error_y_prev=0
        while True:

            #time check - elapsed is the time between the loops - this is importent for the PID
            current_time = time.time()
            elapsed = current_time - last_time
            last_time = current_time

            x, y, z = await camera_data_queue.get()
            x_n, y_n = await pixel_to_meters(x, y, 87, 58, 640, 480, z)
            #filtered_x = await butter_lowpass_filter(filtered_x_prev, x_n)
            #filtered_y = await butter_lowpass_filter(filtered_y_prev, y_n)




            #start the camera movment
            await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
            await offboard(drone)
            Vx,Vy,z,Vx_current,Vy_current,Error_x_prev,Error_y_prev = await movment_camera(drone,x_n,y_n,x,y,z,Error_x_prev,Error_y_prev,elapsed)
            await save_data(drone,Vx,Vy,elapsed,Vx_current,Vy_current)



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