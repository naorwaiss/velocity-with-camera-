import aiofiles
import asyncio
import random
import os

# Function to create a new notepad (file) with the specified content
async def create_notepad(file_path, content):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(content)

# Function to append content to an existing notepad (file)
async def append_to_notepad(file_path, content):
    async with aiofiles.open(file_path, 'a') as file:
        await file.write(content)

# Function to save velocity data to a notepad, either by creating a new notepad or appending to an existing one
async def save_velocity_data(file_path, velocity_data):
    # Format the velocity data to have 4 decimal places
    formatted_data = [format_number(V) for V in velocity_data]

    # Convert the list of velocity data to a string with newline separators
    table_string = '\n'.join(map(str, formatted_data)) + '\n'

    # If the file exists, append to it; otherwise, create a new notepad
    if os.path.exists(file_path):
        await append_to_notepad(file_path, table_string)
    else:
        await create_notepad(file_path, table_string)

# Function to save velocity data to a notepad (file) with a list of velocity values


# Function to format a number with 4 decimal places
def format_number(num):
    return "{:.4f}".format(num)



async def crate_notepad():
    notepad_path1 = 'delta_t.txt'
    notepad_path2= 'Vy.txt'
    notepad_path3 = 'Vx.txt'

    await create_notepad(notepad_path1, '')
    await create_notepad(notepad_path2, '')
    await create_notepad(notepad_path3, '')


async def save_to_note_pads(V, file_path):
    await save_velocity_data(file_path, [V])



# Example usage with random values
async def main():
    notepad_path = 'velocity_x_data.txt'

    # Open the file at the beginning of the loop (create an empty notepad initially)
    await create_notepad(notepad_path, '')

    i = 0
    while i < 10:
        V = random.uniform(1, 10)

        # Write to the notepad in each iteration
        await save_to_note_pads(V, notepad_path)

        i += 1

    print(f"Velocity data saved at: {notepad_path}")

# Run the asyncio event loop
asyncio.run(main())
