import paramiko
import os


def transfer_files(hostname, username, password, local_files, remote_directory):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the Linux machine
        ssh.connect(hostname, username=username, password=password)

        # Create an SFTP session
        sftp = ssh.open_sftp()

        # Transfer each file
        for local_file in local_files:
            local_path = os.path.abspath(local_file)
            remote_path = os.path.join(remote_directory, os.path.basename(local_file))

            print(f"Transferring {local_path} to {remote_path}")
            sftp.put(local_path, remote_path)

        print("File transfer completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the SFTP session and the SSH connection
        if sftp:
            sftp.close()
        ssh.close()


# Replace these values with your own
linux_hostname = '192.168.1.121'
linux_username = 'naor'
linux_password = '1'

# List of local files to transfer
local_files_to_transfer = ['delta_t.txt', 'Vx.txt', 'Vy.txt', 'Vx_current.txt', 'Vy_current.txt']

# Remote directory on the Windows machine
windows_remote_directory = 'C:/Path/To/Your/Windows/Directory/'

# Perform the file transfer
transfer_files(linux_hostname, linux_username, linux_password, local_files_to_transfer, windows_remote_directory)
