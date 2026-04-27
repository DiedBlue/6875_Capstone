from netmiko import ConnectHandler
from datetime import datetime
import os

# These will be the details of the device from the topology
device = {
    "device_type": "cisco_ios",
    "host": "192.168.56.101",
    "username": "cisco",
    "password": "cisco123!",
}

# Please make sure all information is correct

backup_dir = "backup_configs"

try:
    # The next few lines uses netmiko's connect handler module to connect to the
    # router, take some time to review how it works!

    print("SSH into Device")
    connection = ConnectHandler(**device)

    print("Processing Runnin COnfiguration")
    config = connection.send_command("show running-config")

    # The next line uses the datetime module to name files based on the 
    # date/time the file was created. Review reflection questions for why!

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{backup_dir}/{device['host']}_backup_{timestamp}.cfg"

    print(f"Saving backup to {filename}")
    with open(filename, "w") as f:
        f.write(config)
    
    print("Backup completed, check file")
    connection.disconnect()

except Exception as e:
    print(f"Error: {e}")