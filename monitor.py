import os
import time
import shutil
from process import process_file

WATCH_FOLDER = 'input_files'
PROCESSED_FOLDER = 'processed_files'

def monitor_folder():
    print("Monitoring folder for new files...")
    already_seen = set(os.listdir(WATCH_FOLDER))

    while True:
        current_files = set(os.listdir(WATCH_FOLDER))
        new_files = current_files - already_seen

        for file in new_files:
            if file.endswith(".txt"):
                filepath = os.path.join(WATCH_FOLDER, file)
                print(f"New file detected: {file}")
                process_file(filepath)
                shutil.move(filepath, os.path.join(PROCESSED_FOLDER, file))

        already_seen = current_files
        time.sleep(5)  # check every 5 seconds

if __name__ == "__main__":
    monitor_folder()
