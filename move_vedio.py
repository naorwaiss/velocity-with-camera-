import paramiko
import os

def copy_file_from_jetson():
    # Jetson SSH details
    jetson_host = "192.168.0.102"
    jetson_username = "drone"
    jetson_password = "fhsbs2023"  # Replace with your actual password
    jetson_remote_path = "/home/drone/Desktop/output.avi"

    # Local computer SSH details
    local_host = "172.18.71.121"
    local_username = "naor"
    local_password = "1"  # Replace with your actual password
    local_path = "/home/naor/Desktop/"

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to Jetson
        ssh.connect(jetson_host, username=jetson_username, password=jetson_password)

        # SCP file from Jetson to local computer
        scp = ssh.open_sftp()
        scp.get(jetson_remote_path, os.path.expanduser(local_path + "output.avi"))
        scp.close()

        print("File copied successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close SSH connection
        ssh.close()

if __name__ == "__main__":
    copy_file_from_jetson()