from netmiko import ConnectHandler

def user_input(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ["y", "yes"]:
            return True
        if answer in ["n", "no"]:
            return False
        print("Please enter Yes or No")

def apply_changes(device):
    expected_changes = {}

    try:
        print("Connecting to SSH")
        connection = ConnectHandler(**device)

        config_commands = []

        print("\nSelect the configuration changes to apply:\n")

        if user_input("Change hostname? (yes/no): "):
            new_hostname = input("Enter new hostname: ").strip()
            if new_hostname:
                config_commands.append(f"hostname {new_hostname}")
                expected_changes["hostname"] = new_hostname

        if user_input("Change MOTD Banner? (yes/no): "):
            new_banner = input("Enter MOTD Banner text: ").strip()
            if new_banner:
                config_commands.append(f"banner motd #{new_banner}#")
                expected_changes["banner"] = new_banner

        if user_input("Change Gig1 description? (yes/no): "):
            new_desc = input("Enter new description: ").strip()
            if new_desc:
                config_commands.append("interface GigabitEthernet1")
                config_commands.append(f"description {new_desc}")
                expected_changes["interface"] = "GigabitEthernet1"
                expected_changes["description"] = new_desc

        if not config_commands:
            print("No config changes accepted.")
        else:
            print("\nApplying Selected Changes\n")
            output = connection.send_config_set(config_commands)
            print(output)

            print("\nSaving Configs")
#           save_output = connection.save_config()
#           print(save_output)
        connection.disconnect()
        print("\nDone.")

        return expected_changes

    except Exception as e:
        print(f"Error: {e}")
        return None
