import paramiko
import os

def transfer_files(hostname, username, password, local_files, remote_directory):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Initialize sftp outside the try block
    sftp = None

    try:
        # Connect to the Linux machine
        ssh.connect(hostname, username=username, password=password)

        # Create an SFTP session
        sftp = ssh.open_sftp()

        # Transfer each file
        for local_file in local_files:
            # Use forward slash (/) as path separator for Linux paths
            local_file_linux = local_file.replace('\\', '/')
            print(f"Transferring {local_file_linux} to {remote_directory}")
            sftp.put(local_file_linux, os.path.join(remote_directory, os.path.basename(local_file_linux)))

        print("File transfer completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the SFTP session and the SSH connection
        if sftp is not None:
            sftp.close()
        ssh.close()

# Replace these values with your own
linux_hostname = '192.168.1.121'
linux_username = 'naor'
linux_password = '1'

# List of local files to transfer with absolute paths on Linux
linux_local_files_to_transfer = [
    '/home/naor/fhsbs/velocity-with-camera-/delta_t.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vx.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vy.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vx_current.txt',
    '/home/naor/fhsbs/velocity-with-camera-/Vy_current.txt',
]

# Remote directory on the Windows machine
windows_remote_directory = r'C:\Users\naorw\OneDrive\שולחן העבודה\proj'

# Perform the file transfer
transfer_files(linux_hostname, linux_username, linux_password, linux_local_files_to_transfer, windows_remote_directory)
