import asyncio
from camera import process_frames,pixel_to_meters  # Import the process_frames function from the main script
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)














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






async def takeoff_velocity(drone):
    #only move at the z at the start of the drone
    print("-- Arming")
    await drone.action.arm()

    print("start takeoff at velocity")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await offboard(drone) #change to offboard

    print("-- only climb")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -1.0, 0))
    await asyncio.sleep(5)

    print ("stop the takeoff")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0))





async def camera_motion(drone, x, y, z):
    print(f"Received camera data: x={x}, y={y}, z={z}")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await offboard(drone)
    factor = 0.01

    x_factor = x * factor
    y_factor = y * factor

    velocity_command = VelocityBodyYawspeed(y_factor, x_factor, 0.0, 0.0)

    if x_factor > 0.1 or y_factor > 0.1:
        await drone.offboard.set_velocity_body(velocity_command)
    else:
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        #at this point the drone need to change the z velocity



async def main():
    global x,y,z
    drone = System()
    await drone.connect(system_address="udp://:14540")
    #await drone.connect(system_address="serial:///dev/ttyTHS1")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    await drone.action.hold()

    #target_altitude = int(input("what is the drone first altitude:"))
    # await takeoff_presedoure(drone, target_altitude)
    # await takeoff_presedoure(drone, 3)
    await takeoff_velocity(drone)





    # Set up a queue for camera data
    camera_data_queue = asyncio.Queue()
    # Start process_frames as a background task
    camera_task = asyncio.create_task(process_frames(camera_data_queue))
    print(" start camera procesing ")
    try:
        while True:
            # Get camera data from the queue
            x, y, z = await camera_data_queue.get()
            print (x,y,z)
            await camera_motion(drone,x,y,z)



    except asyncio.CancelledError:
        # This block will execute when camera_task is cancelled
        pass
    except Exception as e:
        print(f"An error occurred: {e}")
        await drone.action.hold()
        await asyncio.sleep(5)
        await drone.action.land()
    finally:
        camera_task.cancel()  # Cancel the background task on exit4
        await drone.action.land()






if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Script manually interrupted")
    except Exception as e:
        print(f"Unhandled error: {e}")