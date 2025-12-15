import json
import sys
from datetime import date, timedelta
from pathlib import Path

# Log file will sit alongside this script
LOG_FILE = Path("fbbq_xfer_auth_log.json")

# Connector key for clarity in multi-connector setups later
FB_CONNECTOR_KEY = "fbbq_xfer"

CHECKLISTS = {
    FB_CONNECTOR_KEY: [
        "Go to Facebook for Developers: https://developers.facebook.com/apps",
        "Open the app used for the BigQuery Facebook transfer.",
        "Go to App settings > Basic and copy the App ID to get the Client Id"
        "Click 'Show' next to App Secret to get the Client Secret",
        "In BigQuery, go to Data Transfers and open the Facebook connector config.",
        "Update Cliend Id and Client Secret, then click Authorize.",
        "Trigger a manual run to confirm the transfer succeeds."
    ]
}


def load_log():
    if LOG_FILE.exists():
        with LOG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_log(data):
    with LOG_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def human_status(connector_key, record):
    history = record.get("history", [])
    if not history:
        return f"[{connector_key}] No rotations logged yet."

    last = history[-1]
    rotated = last["rotated_on"]
    expires = last["expires_on"]

    today = date.today()
    expires_date = date.fromisoformat(expires)
    days_left = (expires_date - today).days

    if days_left < 0:
        status = "EXPIRED ❌"
    elif days_left <= 7:
        status = "Expiring soon ⚠"
    else:
        status = "OK ✅"

    return (
        f"[{connector_key}] Last rotation: {rotated}, "
        f"expires: {expires} ({days_left} days left) -> {status}"
    )


def cmd_status(connector_key=None):
    data = load_log()

    if not data:
        print("No auth rotations logged yet.")
        return

    if connector_key:
        record = data.get(connector_key)
        if not record:
            print(f"No log found for connector key: {connector_key}")
            return
        print(human_status(connector_key, record))
    else:
        for key, record in data.items():
            print(human_status(key, record))


def cmd_rotate(connector_key):
    if connector_key not in CHECKLISTS:
        print(f"No checklist configured for connector key: {connector_key}")
        return

    checklist = CHECKLISTS[connector_key]

    print(f"Starting rotation ritual for: {connector_key}\n")
    print("Follow these steps:")
    for i, step in enumerate(checklist, start=1):
        print(f"{i}. {step}")

    confirm = input("\nType 'done' when you have completed all steps: ").strip().lower()
    if confirm != "done":
        print("Rotation cancelled. Nothing logged.")
        return

    today = date.today()
    expires_on = today + timedelta(days=90)

    notes = input("Optional notes (press Enter to skip): ").strip()

    data = load_log()
    record = data.get(connector_key, {"history": []})

    event = {
        "rotated_on": today.isoformat(),
        "expires_on": expires_on.isoformat(),
        "notes": notes
    }
    record["history"].append(event)
    data[connector_key] = record
    save_log(data)

    print("\nRotation logged.")
    print(human_status(connector_key, record))


def print_help():
    help_text = f"""
Usage:
  python fbbq_xfer_auth_checklist.py status
      Show status for all connectors.

  python fbbq_xfer_auth_checklist.py status {FB_CONNECTOR_KEY}
      Show status for the Facebook → BigQuery transfer.

  python fbbq_xfer_auth_checklist.py rotate {FB_CONNECTOR_KEY}
      Run the rotation checklist and log a new entry.

Configured connector keys:
  - {FB_CONNECTOR_KEY}
"""
    print(help_text.strip())


def main():
    if len(sys.argv) == 1:
        print_help()
        return

    cmd = sys.argv[1].lower()

    if cmd == "status":
        if len(sys.argv) == 3:
            cmd_status(sys.argv[2])
        else:
            cmd_status()

    elif cmd == "rotate":
        if len(sys.argv) != 3:
            print("Please provide a connector key. Example:")
            print(f"  python fbbq_xfer_auth_checklist.py rotate {FB_CONNECTOR_KEY}")
            return
        cmd_rotate(sys.argv[2])

    else:
        print_help()


if __name__ == "__main__":
    main()
