import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)




async def offboard(drone):
    """

    :param drone: drone is the connact string
    :return: the real/ fake drone need to change the mode to off board mode
    before this function need to gave the drone some -  "set"
    """
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
    """

    :param drone: the connection string
    :return: this function takeoff the drone at velocity value
    """
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

async def odomety(drone):
    """

    :param drone: connection stroing
    :return: this function gave a single output for the drone belocity at budy
    * this function is simple example how to chanfe the for loop to single output - it take me too long time
    this function is one of the importent function
    """
    #need to think if need to vhange this value to somthing that i knew??
    async for odometry in drone.telemetry.odometry():
        return odometry.velocity_body.x_m_s,odometry.velocity_body.y_m_s,odometry.velocity_body.z_m_s








async def movment_camera(drone,filtered_x, filtered_y,x,y,z):
    #doing some calculation:
    Vx = (await convert(filtered_x,z))*(await sighn(x))
    Vy = (await convert(filtered_y,z)) * (await sighn(y))

    Vx_current,Vy_current,Vz_current = await odomety(drone)

    velocity_command = VelocityBodyYawspeed(Vy, Vx, 0.0, 0.0)
    await drone.offboard.set_velocity_body(velocity_command)



    # check the movment direction with the x,y and Vx, Vy
    #print(f" speed: Vx={Vx}, Vy={Vy}, z={z}")

    return Vx,Vy,z, Vx_current,Vy_current,Vz_current




async def PID(V_desierd,V_current,delta_t,Error_prev):
    """

    :param V_desierd: v that go to the drone
    :param V_current: velocity right now
    :param delta_t: the time
    :param Error_prev: the prev error for the D
    :return: error and velocity after PID
    """
    #this function need to move data to the movment cameara and then to the main
    kp = 0.1
    kd = 0.01       #dont know what the value need to be...

    Error = V_desierd-V_current
    Deff = (Error-Error_prev)/delta_t

    V_PID = kp*Error + kd*Deff

    return V_PID,Error









    return V_PID













async def camera_motion_simple(drone, x, y, z):
    # simple camera motion that i noot like to delet becuse it show me where i began

    factor = 0.01

    x_factor = x * factor
    y_factor = y * factor

    velocity_command = VelocityBodyYawspeed(y_factor, x_factor, 0.0, 0.0)

    if x_factor > 0.1 or y_factor > 0.1:
        await drone.offboard.set_velocity_body(velocity_command)
    else:
        await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
        #at this point the drone need to change the z velocity
