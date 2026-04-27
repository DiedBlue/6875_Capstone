from backup import backup_config
from changes import apply_changes
from verify import verify_changes
from rollback import rollback_config

device = {
    "device_type": "cisco_ios",
    "host": "192.168.56.101",
    "username": "cisco",
    "password": "cisco123!",
}

def run_rollback(device, backup_file, expected_changes):
    print("\nRolling back to most recent backup")
    rollback_results = rollback_config(device, backup_file, expected_changes)

    if rollback_results is None:
        print("Rollback failed")
        return

    print("\nRollback Results:")

    if "hostname" in rollback_results:
        status = "Passed" if rollback_results["hostname"]["passed"] else "Failed"
        value = rollback_results["hostname"]["value"]
        print(f"Hostname Rollback: {status} - Rolled back to {value}")

    if "description" in rollback_results:
        status = "Passed" if rollback_results["description"]["passed"] else "Failed"
        value = rollback_results["description"]["value"]
        print(f"Description Rollback: {status} - Rolled back to {value}")

    if "banner" in rollback_results:
        status = "Passed" if rollback_results["banner"]["passed"] else "Failed"
        value = rollback_results["banner"]["value"]
        print(f"Banner Rollback: Rolled back to {value}")


def main():
    print("Starting Automated Configuration Playbook\n")

    # Step 1: Backup current config
    backup_file = backup_config(device)
    if backup_file is None:
        print("Backup failed, exiting script")
        return

    print(f"\nBackup Successful: {backup_file}")

    # Step 2: Apply changes
    expected_changes = apply_changes(device)
    if expected_changes is None:
        print("Configuration step failed, exiting script")
        return

    if not expected_changes:
        print("No valid changes were selected, exiting script")
        return

    print(f"\nExpected changes: {expected_changes}")

    # Step 3: Verify changes
    results = verify_changes(device, expected_changes)
    if results is None:
        print("Verification failed")
        print("Verification could not complete. Treating as failed validation.")
        run_rollback(device, backup_file, expected_changes)
        return

    print("\nVerification Results:")
    all_passed = True

    if "hostname" in results:
        status = "Pass" if results["hostname"] else "Fail"
        print(f"Hostname: {status}")
        if not results["hostname"]:
            all_passed = False

    if "banner" in results:
        status = "Pass" if results["banner"] else "Fail"
        print(f"Banner: {status}")
        if not results["banner"]:
            all_passed = False

    if "description" in results:
        status = "Pass" if results["description"] else "Fail"
        print(f"Description: {status}")
        if not results["description"]:
            all_passed = False

    if all_passed:
        print("\nChanges Successful")
    else:
        run_rollback(device, backup_file, expected_changes)


if __name__ == "__main__":
    main()