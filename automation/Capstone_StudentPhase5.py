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


# ============================================================
# PHASE 3 - VALIDATE THE CHANGES
# ============================================================
print("\n==============================")
print("PHASE 3 - VALIDATE THE CHANGES")
print("==============================\n")
time.sleep(1)

try:
    print("Checking the hostname in the running config...")
    time.sleep(1)

    # This asks the router to show only the hostname line.
    hostname_output = connection.send_command("show running-config | include ^hostname")

    # This checks whether the hostname we wanted is actually present.
    # The result will be either True or False.
    hostname_ok = f"hostname {new_hostname}" in hostname_output

    print("Checking the GigabitEthernet1 description...")
    time.sleep(1)

    # This asks the router to show the config for GigabitEthernet1.
    desc_output = connection.send_command("show running-config interface GigabitEthernet1")

    # This checks whether the description we wanted is present.
    description_ok = f"description {new_description}" in desc_output

    print("\nValidation Results:")
    print("-------------------")
    print(f"Hostname: {'Pass' if hostname_ok else 'Fail'}")
    print(f"Interface Description: {'Pass' if description_ok else 'Fail'}\n")
    time.sleep(2)

except Exception as e:
    print(f"Error during Phase 3: {e}")


# ============================================================
# PHASE 4 - READ THE ORIGINAL VALUES FROM THE BACKUP
# ============================================================
print("\n========================================")
print("PHASE 4 - READ THE ORIGINAL VALUES BACK")
print("========================================\n")
time.sleep(1)

try:
    print("Opening the backup file...")
    time.sleep(1)

    # Read the saved config file back into Python as one big text block.
    with open(backup_file, "r") as f:
        backup_text = f.read()

    print("Backup file loaded.\n")
    time.sleep(1)

    print("Finding the original hostname in the backup...")
    time.sleep(1)

    # re.search() looks for a pattern in text.
    #
    # ^hostname means:
    # find a line that starts with "hostname"
    #
    # \s+ means:
    # one or more spaces
    #
    # (.+) means:
    # save the rest of the line
    hostname_match = re.search(r"^hostname\s+(.+)$", backup_text, re.MULTILINE)

    if hostname_match:
        original_hostname = hostname_match.group(1).strip()
    else:
        original_hostname = None

    print(f"Original hostname: {original_hostname}")
    time.sleep(1)

    print("Finding the original interface description in the backup...")
    time.sleep(1)

    # splitlines() takes one large block of text
    # and breaks it into separate lines.
    #
    # Example:
    # "line1\nline2\nline3"
    # becomes:
    # ["line1", "line2", "line3"]
    lines = backup_text.splitlines()

    original_description = None
    in_interface = False

    for line in lines:
        # strip() removes spaces from the beginning and end of the line.
        stripped = line.strip()

        # Check whether we are at the correct interface section.
        if stripped == "interface GigabitEthernet1":
            in_interface = True
            continue

        if in_interface:
            # If we hit another interface or !, the section is over.
            if stripped.startswith("interface ") or stripped == "!":
                break

            # startswith() checks whether the line begins
            # with certain text.
            if stripped.startswith("description "):
                original_description = stripped.replace("description ", "", 1)
                break

    print(f"Original interface description: {original_description}\n")
    time.sleep(2)

except Exception as e:
    print(f"Error during Phase 4: {e}")


# ============================================================
# PHASE 5 - ROLLBACK IF VALIDATION FAILED
# ============================================================
print("\n======================================")
print("PHASE 5 - ROLLBACK IF VALIDATION FAILED")
print("======================================\n")
time.sleep(1)

try:
    # If both checks passed, leave the config as-is.
    if hostname_ok and description_ok:
        print("Both changes passed validation.")
        print("No rollback is needed.\n")
        time.sleep(1)

    else:
        print("Validation failed.")
        print("Even if one change worked, both changes will be rolled back.")
        time.sleep(2)

        rollback_commands = []

        # Put the original hostname back.
        if original_hostname:
            rollback_commands.append(f"hostname {original_hostname}")

        # Enter the interface section.
        rollback_commands.append("interface GigabitEthernet1")

        # If there was an old description, restore it.
        # If there was no old description, remove the current one.
        if original_description:
            rollback_commands.append(f"description {original_description}")
        else:
            rollback_commands.append("no description")

        print("\nSending rollback commands to the router...\n")
        time.sleep(1)

        rollback_output = connection.send_config_set(rollback_commands)

        print("Router response:\n")
        print(rollback_output)
        time.sleep(1)

        print("Checking rollback results...\n")
        time.sleep(1)

        # Re-check the hostname after rollback.
        hostname_output = connection.send_command("show running-config | include ^hostname")

        if original_hostname:
            hostname_rollback_ok = f"hostname {original_hostname}" in hostname_output
        else:
            hostname_rollback_ok = False

        # Re-check the interface description after rollback.
        desc_output = connection.send_command("show running-config interface GigabitEthernet1")

        if original_description:
            description_rollback_ok = f"description {original_description}" in desc_output
        else:
            description_rollback_ok = "description " not in desc_output

        print("Rollback Results:")
        print("-----------------")
        print(f"Hostname Rollback: {'Passed' if hostname_rollback_ok else 'Failed'}")
        print(f"Interface Description Rollback: {'Passed' if description_rollback_ok else 'Failed'}\n")
        time.sleep(2)

except Exception as e:
    print(f"Error during Phase 5: {e}")
connection.disconnect()