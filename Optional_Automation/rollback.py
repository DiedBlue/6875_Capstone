from netmiko import ConnectHandler
import re


def get_backup_config(backup_file):
    try:
        with open(backup_file, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading backup file: {e}")
        return None


def get_hostname_from_backup(config_text):
    match = re.search(r"^hostname\s+(.+)$", config_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def get_interface_description_from_backup(config_text, interface_name="GigabitEthernet1"):
    lines = config_text.splitlines()
    in_interface = False

    for line in lines:
        stripped = line.strip()

        if stripped == f"interface {interface_name}":
            in_interface = True
            continue

        if in_interface:
            if stripped.startswith("interface ") or stripped == "!":
                break
            if stripped.startswith("description "):
                return stripped.replace("description ", "", 1)

    return None


def get_banner_from_backup(config_text):
    lines = config_text.splitlines()

    for i, line in enumerate(lines):
        if line.startswith("banner motd "):
            delimiter = line.replace("banner motd ", "", 1).strip()

            banner_lines = []
            for banner_line in lines[i + 1:]:
                if banner_line.strip() == delimiter:
                    return "\n".join(banner_lines)
                banner_lines.append(banner_line)

    return None


def build_banner_parts(banner_text):
    delimiter = "#"

    for candidate in ["#", "@", "%", "&", "^", "!"]:
        if candidate not in banner_text:
            delimiter = candidate
            break

    return delimiter, banner_text


def rollback_config(device, backup_file, expected_changes):
    config_text = get_backup_config(backup_file)
    if config_text is None:
        return None

    rollback_results = {}

    try:
        original_hostname = get_hostname_from_backup(config_text)
        original_banner = get_banner_from_backup(config_text)
        original_desc = get_interface_description_from_backup(
            config_text,
            "GigabitEthernet1"
        )

        print("\nConnecting to SSH for rollback")
        connection = ConnectHandler(**device)

        rollback_commands = []

        if "hostname" in expected_changes and original_hostname:
            rollback_commands.append(f"hostname {original_hostname}")

        if "banner" in expected_changes:
            rollback_commands.append("no banner motd")

        if "description" in expected_changes:
            rollback_commands.append("interface GigabitEthernet1")
            if original_desc:
                rollback_commands.append(f"description {original_desc}")
            else:
                rollback_commands.append("no description")

        if rollback_commands:
            print("\nApplying rollback, standby\n")
            output = connection.send_config_set(rollback_commands)
            print(output)

        if "banner" in expected_changes and original_banner:
            delimiter, banner_text = build_banner_parts(original_banner)

            connection.send_command_timing("configure terminal")
            connection.send_command_timing(f"banner motd {delimiter}")

            for line in banner_text.splitlines():
                connection.send_command_timing(line)

            connection.send_command_timing(delimiter)
            connection.send_command_timing("end")

        connection.send_command("terminal length 0")

        if "hostname" in expected_changes and original_hostname:
            hostname_output = connection.send_command("show running-config | include ^hostname")
            rollback_results["hostname"] = {
                "passed": f"hostname {original_hostname}" in hostname_output,
                "value": original_hostname
            }

        if "banner" in expected_changes:
            banner_output = connection.send_command("show running-config | section banner")

            if original_banner:
                original_lines = [line.strip() for line in original_banner.splitlines() if line.strip()]
                passed = all(line in banner_output for line in original_lines)
            else:
                passed = "banner motd" not in banner_output

            rollback_results["banner"] = {
                "passed": passed,
                "value": original_banner if original_banner else "No banner configured"
            }

        if "description" in expected_changes:
            desc_output = connection.send_command("show running-config interface GigabitEthernet1")
            if original_desc:
                passed = f"description {original_desc}" in desc_output
                value = original_desc
            else:
                passed = "description " not in desc_output
                value = "No description configured"

            rollback_results["description"] = {
                "passed": passed,
                "value": value
            }

        connection.disconnect()
        print("\nRollback completed.")
        return rollback_results

    except Exception as e:
        print(f"Rollback Error: {e}")
        return None