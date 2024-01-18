import asyncio
from camera import process_frames, pixel_to_meters, update_kalman_filter, initialize_kalman_filter
from mavsdk import System
from drone_mothion_function import offboard,takeoff_velocity

from drone_mothion_function import offboard, takeoff_velocity, camera_motion_simple, takeoff_presedoure,movment_camera


async def odomety(drone):
    #this function gave me the velocity at the single time - this function is work
    async for odometry in drone.telemetry.odometry():
        return odometry.velocity_body.x_m_s,odometry.velocity_body.y_m_s,odometry.velocity_body.z_m_s





async def main():
    # this is the main branch of the drone code
    drone = System()
    await drone.connect(system_address="udp://:14540")


    odometry = await odomety(drone)
    print(odometry)

    await drone.action.hold()
    await takeoff_velocity(drone)  # Doing takeoff to 5-4 meters without GPS

    odometry = await odomety(drone)
    print(odometry)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Script manually interrupted")
    except Exception as e:
        print(f"Unhandled error: {e}")
