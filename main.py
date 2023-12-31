import asyncio
from camera import process_frames  # Import the process_frames function from the main script
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import time


async def takeoff_presedoure(drone,target_altitude):

    """
    :param drone: the connect strings
    :return: takeoff the drone
    """

    #  need to add change to stabilize mode

    await drone.action.set_takeoff_altitude(target_altitude)
    await asyncio.sleep(1)
    print("-- Arming")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
    return


async def offboard(drone):

    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
                  {error._result.result}")

        print("stop offbord")
        await drone.offboard.stop()
        return

    return




async def camera_motion(drone, x, y, z, timeout=10):
    start_time = time.time()
    print(x)
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    while time.time() - start_time < timeout:
        if x > 5:
            await drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))
        elif x <5 :
            await drone.offboard.set_velocity_body(VelocityBodyYawspeed(-1.0, 0.0, 0.0, 0.0))

        else:
            print("Hold")
            await asyncio.sleep(0.5)  # Add a small delay to prevent flooding the console
    print("Exiting camera_motion")





async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    target_altitude = int(input("what is the drone first altitude:"))
    await takeoff_presedoure(drone,target_altitude)

    try:
        async for x, y, z in process_frames():
            print(f"Received coordinates: {x}, {y}, {z}")
            await camera_motion(drone, x, y, z, timeout=10)
            print("Completed a camera_motion cycle")
    except Exception as e:
        print(f"An error occurred: {e}")

    if __name__ == "__main__":
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            print("Script manually interrupted")
        except Exception as e:
            print(f"Unhandled error: {e}")
