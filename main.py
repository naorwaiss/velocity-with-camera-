import asyncio
from camera import process_frames  # Import the process_frames function from the main script
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




async def camera_motion(drone):
    async for x, y, z in process_frames():
        await drone.offboard.set_velocity_body(
            VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        while True:
            # Move at x
            if x > 5:
                await drone.offboard.set_velocity_body(
                    VelocityBodyYawspeed(1.0, 0.0, 0.0, 0.0))

            else:
                print ("hold")





async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break




    first_atitude = int(input("enter the first altitude of the drone at [M]:"))
    await takeoff_presedoure(drone,first_atitude)

    await camera_motion(drone)



    #async for x, y, z in process_frames():
        #print(f"x_distance: {x}, y_distance: {y}, depth: {z:.2f} meters")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())



