import os
import hashlib
import json
import time

# ==== CONFIG ====
DRIVE_PATH = "E:/YourPendrive"  # <- Change this to your pendrive path
SNAPSHOT_FILE = "snapshot.json"

# ==== FUNCTIONS ====

def fast_metadata(file_path):
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "mtime": stat.st_mtime
        }
    except:
        return None

def compute_hash(file_path, algo='sha256', max_bytes=1024 * 1024):  # Only first 1MB
    h = hashlib.new(algo)
    with open(file_path, 'rb') as f:
        h.update(f.read(max_bytes))
    return h.hexdigest()

def scan_drive(directory):
    file_info = {}
    for root, dirs, files in os.walk(directory):
        for name in files:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, directory)
            meta = fast_metadata(full_path)
            if meta:
                meta["hash"] = compute_hash(full_path)  # partial hash for speed
                file_info[rel_path] = meta
    return file_info

def save_snapshot(data):
    with open(SNAPSHOT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, 'r') as f:
        return json.load(f)

def compare_snapshots(old, new):
    modified = []
    deleted = []
    new_files = []

    for path, old_data in old.items():
        if path not in new:
            deleted.append(path)
        else:
            if old_data != new[path]:
                modified.append(path)

    for path in new:
        if path not in old:
            new_files.append(path)

    return modified, deleted, new_files

# ==== MAIN ====

def main():
    print("Scanning pendrive...")
    current = scan_drive(DRIVE_PATH)
    old = load_snapshot()

    if not old:
        print("No snapshot found. Saving first-time snapshot...")
        save_snapshot(current)
        print("Baseline saved.")
        return

    modified, deleted, new_files = compare_snapshots(old, current)

    print("\n==== Comparison Results ====")
    print(f"🔁 Modified files: {len(modified)}")
    for f in modified: print(" -", f)

    print(f"❌ Deleted files: {len(deleted)}")
    for f in deleted: print(" -", f)

    print(f"🆕 New files: {len(new_files)}")
    for f in new_files: print(" -", f)

    choice = input("\nUpdate snapshot with current state? (y/n): ").strip().lower()
    if choice == 'y':
        save_snapshot(current)
        print("Snapshot updated.")

if __name__ == "__main__":
    main()
