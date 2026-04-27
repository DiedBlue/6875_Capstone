from netmiko import ConnectHandler
import re
import time

# ============================================================
# ROUTER LOGIN INFORMATION
# ============================================================
# This dictionary stores the login information for the router.
# Netmiko uses these values to open an SSH connection.
device = {
    "device_type": "cisco_ios",
    "host": "192.168.56.101",
    "username": "cisco",
    "password": "cisco123!",
}

# This is the file where we will save the router backup.
backup_file = "router_backup.cfg"


# ============================================================
# PHASE 1 - CONNECT AND BACK UP THE CONFIG
# ============================================================
print("\n==================================================")
print("PHASE 1 - CONNECT TO THE ROUTER AND CREATE A BACKUP")
print("==================================================\n")
time.sleep(1)

try:
    print("Connecting to the router with Netmiko...")
    time.sleep(1)

    # ConnectHandler() opens an SSH session to the router.
    # The **device part means:
    # use all the values from the device dictionary as settings.
    connection = ConnectHandler(**device)

    print("Connected.\n")
    time.sleep(1)

    print("Turning off paging so the output does not pause...")
    time.sleep(1)

    # send_command() sends a normal command to the router
    # and stores the router output as text.
    connection.send_command("terminal length 0")

    print("Requesting the running configuration...")
    time.sleep(1)

    running_config = connection.send_command("show running-config")

    print("Configuration received.")
    time.sleep(1)

    print(f"Saving backup to {backup_file} ...")
    time.sleep(1)

    # This opens a file on the Linux machine and writes
    # the running config into it.
    with open(backup_file, "w") as f:
        f.write(running_config)

    print("Backup complete.\n")
    time.sleep(1)

except Exception as e:
    print(f"Error during Phase 1: {e}")


# ============================================================
# PHASE 2 - APPLY CONFIGURATION CHANGES
# ============================================================
print("\n===================================")
print("PHASE 2 - APPLY CONFIGURATION CHANGES")
print("===================================\n")
time.sleep(1)

try:
    print("We will now change two settings on the router:")
    print("1. The hostname")
    print("2. The GigabitEthernet1 description\n")
    time.sleep(2)

    # Ask the student for a new hostname.
    # In this lab environment, using a space in the hostname
    # should cause the hostname change to fail.
    new_hostname = input("Enter a new hostname: ").strip()

    # Ask the student for a new interface description.
    new_description = input("Enter a new GigabitEthernet1 description: ").strip()

    print("\nBuilding configuration commands...")
    time.sleep(1)

    # This list stores the commands we want to send.
    config_commands = [
        f"hostname {new_hostname}",
        "interface GigabitEthernet1",
        f"description {new_description}"
    ]

    print("Sending the commands to the router...\n")
    time.sleep(1)

    # send_config_set() is used for configuration commands.
    # Netmiko automatically enters config mode,
    # sends the commands, and exits config mode.
    config_output = connection.send_config_set(config_commands)

    print("Router response:\n")
    print(config_output)
    time.sleep(1)

    print("Configuration changes sent.\n")
    time.sleep(1)

except Exception as e:
    print(f"Error during Phase 2: {e}")
connection.disconnect()
