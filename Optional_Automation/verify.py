from netmiko import ConnectHandler
from genie.testbed import load


def verify_changes(device, expected_changes):
    results = {}

    try:
        print("\nConnecting to SSH for Verification")
        connection = ConnectHandler(**device)
        connection.send_command("terminal length 0")

        # Load Genie testbed object for parsing only
        testbed = load("testbed.yaml")
        genie_device = testbed.devices["csr1000v"]

        # Hostname verification
        if "hostname" in expected_changes:
            raw_hostname = connection.send_command("show running-config | include ^hostname")
            expected_line = f"hostname {expected_changes['hostname']}"
            results["hostname"] = expected_line in raw_hostname

        # Banner verification
        if "banner" in expected_changes:
            raw_banner = connection.send_command("show running-config | section banner")
            results["banner"] = expected_changes["banner"] in raw_banner

        # Interface description verification using Genie parser
        if "interface" in expected_changes and "description" in expected_changes:
            interface_name = expected_changes["interface"]

            raw_interfaces = connection.send_command(f"show interfaces {interface_name}")

            parsed = genie_device.parse(
                f"show interfaces {interface_name}",
                output=raw_interfaces
            )

            actual_desc = None
            if interface_name in parsed:
                actual_desc = parsed[interface_name].get("description")

            results["description"] = actual_desc == expected_changes["description"]

        connection.disconnect()
        return results

    except Exception as e:
        print(f"Verification Error: {e}")
        return None