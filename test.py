import asyncio
import os
from camera import process_frames  # Ensure camera.py is in the same directory or adjust the import path accordingly

async def main():

    async for x, y, z in process_frames():
        print(f"X: {x}, Y: {y}, Z: {z}")

if __name__ == "__main__":
    asyncio.run(main())
