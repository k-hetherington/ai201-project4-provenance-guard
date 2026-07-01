import json
import os

LOG_FILE = "logs/audit.json"

# Location of the audit log file
def load_log():
    """Load the audit log from disk."""
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as file:
        return json.load(file)

# Read the current audit log from disk
def save_log(entries):
    """Save the audit log to disk."""
    with open(LOG_FILE, "w") as file:
        json.dump(entries, file, indent=4)

# Save updated audit log entries
def add_entry(entry):
    """Add a new entry to the audit log."""
    entries = load_log()
    entries.append(entry)
    save_log(entries)

# Add a new event to the audit log
def get_log():
    """Return all audit log entries."""
    return load_log()

# Return every audit log entry
def update_status(content_id, new_status):
    entries = load_log()

    for entry in entries:
        if (
            entry.get("event_type") == "submission"
            and entry.get("content_id") == content_id
        ):
            entry["status"] = new_status

    save_log(entries)