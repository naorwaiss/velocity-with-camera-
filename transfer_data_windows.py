import subprocess
import os

def transfer_files(hostname, username, password, local_files, remote_directory):
    try:
        # Transfer each file using winscp.com
        for local_file in local_files:
            print(f"Transferring {local_file} to {remote_directory}")
            subprocess.run([
                'winscp.com',
                '/command',
                f'open scp://{username}:{password}@{hostname}/ -hostkey="*"',
                f'put "{local_file}" "{os.path.join(remote_directory, os.path.basename(local_file))}"',
                'exit'
            ], check=True)
            print(f"Transfer successful for {local_file}")

        print("File transfer completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

# Replace these values with your own
linux_hostname = '192.168.1.121'
linux_username = 'naor'
linux_password = 'your_linux_password'  # Replace with the actual password of your Linux machine

linux_local_files_to_transfer = [
    '/home/naor/fhsbs/velocity-with-camera-/delta_t.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vx.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vy.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vx_current.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vy_current.txt',
]

windows_remote_directory = r'C:\Users\naorw\OneDrive\שולחן העבודה\proj'

# Perform the file transfer
transfer_files(linux_hostname, linux_username, linux_password, linux_local_files_to_transfer, windows_remote_directory)
