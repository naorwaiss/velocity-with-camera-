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




async def factor(value):
    #the factor to make the drone run after the item --- the drone need to be little faster then the object
    if (0<value<50):
        factor = 0
        return factor
    elif (51<value<120):
        factor = 1.2
        return factor
    else:
        factor = 1.4
        return factor


async def sighn(value):
    # gave the sighn of the velocity - to the drone
    PN = 0
    if value >= 0 :
        PN = 1
        return PN
    else:
        PN = -1
        return PN




async def camera_motion_PID(x,y,filtered_x, filtered_y,filtered_x_prev, filtered_y_prev,z,eleps,drone):

    #this function not ready - need to add few things
    Vx = abs((filtered_x - filtered_x_prev) / eleps)
    Vy = abs((filtered_y - filtered_y_prev) / eleps)
    if (z==0):
        Vx=Vy=0
        return Vx,Vy

    elif (Vx >3 or Vy >3):
        print("high velo - prolem- stop the drone movment at this iteration ")
        #stop the movemt to the drone
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(0.1)
    else:
        #doing some calculation
        Vx = Vx * (await factor(x))*(await sighn(x))
        Vy = Vy * (await factor(y))*(await sighn(y))

        #need to find out if the direction - and change the factor as well

        velocity_command = VelocityBodyYawspeed(Vy, Vx, 0.0, 0.0)
        await drone.offboard.set_velocity_body(velocity_command)
        #await asyncio.sleep(0.2) this things is needed?
    return


