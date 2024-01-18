import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import math



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


async def takeoff_presedoure(drone,target_altitude):

    """
    :param drone: the connect strings
    :return: takeoff the drone need gps to do this procedour (i think)
    """

    #  need to add change to stabilize mode

    await drone.action.set_takeoff_altitude(target_altitude)
    await asyncio.sleep(1)
    print("-- Arming")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)
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





async def camera_motion_simple(drone, x, y, z):
    #this function is simple motion - this is function need to fix

    factor = 0.01

    x_factor = x * factor
    y_factor = y * factor

    velocity_command = VelocityBodyYawspeed(y_factor, x_factor, 0.0, 0.0)

    if x_factor > 0.1 or y_factor > 0.1:
        await drone.offboard.set_velocity_body(velocity_command)
    else:
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        #at this point the drone need to change the z velocity




async def M_value(z):

    M = (19/49)*z+(3/49)
    return M


async def convert(value,z):
    value = abs(value)
    V=0
    #convert to
    if value<=0.1:
        V=0
        return V
    elif (0.1<value<4):
        #the function
        V = (value-0.1)/(await M_value(z))
        return V
    else:
        V = 2
        return V

async def sighn(value):
        # gave the sighn of the velocity - to the drone
        PN = 0
        if value >= 0:
            PN = 1
            return PN
        else:
            PN = -1
            return PN



async def movment_camera(drone,filtered_x, filtered_y,x,y,z):
    #doing some calculation:
    Vx = (await convert(filtered_x,z))*(await sighn(x))
    Vy = (await convert(filtered_y,z)) * (await sighn(y))

    velocity_command = VelocityBodyYawspeed(Vy, Vx, 0.0, 0.0)
    await drone.offboard.set_velocity_body(velocity_command)

    # check the movment direction with the x,y and Vx, Vy
    print(f" speed: Vx={Vx}, Vy={Vy}, z={z}")


async def odomety(drone):
    #this function gave me the velocity at the single time - this function is work
    async for odometry in drone.telemetry.odometry():
        return odometry.velocity_body.x_m_s,odometry.velocity_body.y_m_s,odometry.velocity_body.z_m_s
