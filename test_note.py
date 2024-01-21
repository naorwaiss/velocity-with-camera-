import aiofiles
import asyncio
import pandas as pd
import random
import os


#this function is make my some first information about how to save file - this  be goot to learn how the drone behave
#need to connact the script to the main script --- need to think how to do his

async def create_notepad(file_path, content):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(content)


async def append_to_notepad(file_path, content):
    async with aiofiles.open(file_path, 'a') as file:
        await file.write(content)


async def save_velocity_data(file_path, time, vx, vy, vz):
    data = pd.DataFrame({'Time': time, 'Vx': vx, 'Vy': vy, 'Vz': vz})
    table_string = data.to_string(index=False) + '\n\n'

    # Remove the existing file, if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Create a new notepad
    await create_notepad(file_path, table_string)


# Example usage with random values
async def main():
    notepad_path = 'velocity_data.txt'
    time_values = []
    Vx_values = []
    Vy_values = []
    Vz_values = []

    for iteration in range(1, 6):  # Simulating 5 iterations
        # Simulating random velocity values
        time_values.append(iteration)
        Vx_values.append(random.uniform(1, 10))
        Vy_values.append(random.uniform(1, 10))
        Vz_values.append(random.uniform(1, 10))

        # Save velocity data at each iteration
        await save_velocity_data(notepad_path, time_values, Vx_values, Vy_values, Vz_values)

    print(f"Velocity data saved at: {notepad_path}")


# Run the asyncio event loop
asyncio.run(main())
