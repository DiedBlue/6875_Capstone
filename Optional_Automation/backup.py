from netmiko import ConnectHandler
from datetime import datetime
import os

# Please make sure all information is correct

def backup_config(device):
    backup_dir = "backup_configs"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    try:
        # The next few lines uses netmiko's connect handler module to connect to the
        # router, take some time to review how it works!

        print("SSH into Device")
        connection = ConnectHandler(**device)

        print("Processing Running Configuration")
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

        return filename

    except Exception as e:
        print(f"Backup Error: {e}")
        return None
