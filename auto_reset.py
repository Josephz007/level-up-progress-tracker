#imports
import json
import os
import random
from datetime import date, timedelta, datetime

#The purpose of this script is to enforces accountability for daily tasks, even if the main app is not running.
#Assigns penalties for uncompleted daily tasks after the grace period (e.g., at 1:00 AM every day).
#This script is meant to be run automatically (in my case by a cron job at 1:00 AM), so penalties are assigned even if the Streamlit app is closed.
#set up cron job: 0 1 * * * /path/to/python /path/to/auto_reset.py



### Configuration
# Get the absolute path to the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# The 'data' folder is in the same directory as the script
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")


def load_json(file_path):
    """
    Loads a JSON file.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(file_path, data):
    """
    Saves data to a JSON file.
    Args:
        file_path (str): The path to the JSON file.
        data (dict): The data to save to the JSON file.
    Returns:
        None
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def assign_penalties(progress, unchecked_count):
    """
    Assigns penalties based on the number of uncompleted daily tasks.
    Args:
        progress (dict): The progress dictionary.
        unchecked_count (int): The number of uncompleted daily tasks.
    Returns:
        dict: The updated progress dictionary.
    """
    penalties = progress.get('penalties', [])
    today = date.today()
    tomorrow = (today + timedelta(days=1)).isoformat()
    
    small_penalties = [
        "Vacuum floor",
        "15 min stretching/meditating",
        "Take stairs instead of elevator for the day"
    ]
    big_penalties = [
        "1 mile run",
        "Cold shower"
    ]

    if unchecked_count == 1:
        penalty_desc = random.choice(small_penalties)
        penalties.append({
            'id': f"pen-{datetime.now().timestamp()}-{random.randint(1000,9999)}",
            'due_date': tomorrow,
            'description': penalty_desc,
            'completed': False
        })
    elif unchecked_count >= 2:
        penalty_desc = random.choice(big_penalties)
        penalties.append({
            'id': f"pen-{datetime.now().timestamp()}-{random.randint(1000,9999)}",
            'due_date': tomorrow,
            'description': penalty_desc,
            'completed': False
        })
    
    progress['penalties'] = penalties
    save_json(PROGRESS_FILE, progress)
    return progress

### Main Logic
def main():
    """
    Checks for uncompleted daily tasks from yesterday and assigns penalties.
    Args:
        None
    Returns:
        None
    """
    print(f"Running daily check for {date.today()}...")

    try:
        progress = load_json(PROGRESS_FILE)
        tasks = load_json(TASKS_FILE)
    except FileNotFoundError:
        print(f"Error: Could not find tasks.json or progress.json in {DATA_DIR}. Exiting.")
        return

    # Determine yesterday's period key for daily tasks
    yesterday = date.today() - timedelta(days=1)
    yesterday_key = yesterday.strftime("%Y-%m-%d")
    
    print(f"Checking for uncompleted daily tasks from {yesterday_key}...")

    # Get all daily tasks
    daily_tasks = tasks.get('daily', [])
    if not daily_tasks:
        print("No daily tasks found in tasks.json.")
        return

    # Get completed daily tasks from progress
    completed_daily = progress.get('completed_tasks', {}).get('daily', {})

    # Count how many daily tasks were NOT completed yesterday
    unchecked_count = 0
    for task in daily_tasks:
        task_name = task['name']
        # Check if the task was logged as completed for yesterday
        if task_name not in completed_daily or yesterday_key not in completed_daily.get(task_name, {}):
            unchecked_count += 1
            print(f"- Task '{task_name}' was not completed.")

    print(f"Found {unchecked_count} uncompleted daily task(s) from yesterday.")

    # Assign penalties if there were any unchecked tasks
    if unchecked_count > 0:
        progress = assign_penalties(progress, unchecked_count)
        print("Successfully updated progress.json with new penalties.")
    else:
        print("All daily tasks were completed. No penalties assigned.")

if __name__ == "__main__":
    main() 