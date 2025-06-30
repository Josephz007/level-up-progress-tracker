# Level Up - Life RPG Tracker

A desktop application that gamifies your daily tasks and goals, inspired by Solo Leveling. Track your progress, earn XP, and level up in real life!

## Features

- **Dynamic Task Tracking**: Manage daily, weekly, monthly, and one-time tasks, each with its own submission button.
- **Time-Aware System**:
    - Each task category has a countdown timer (hours for daily, days for weekly/monthly).
    - A 1-hour grace period allows you to submit tasks even after the deadline.
- **XP and Leveling System**: Gain XP for completing tasks and watch your level grow.
- **Robust Penalty System**:
    - Penalties are automatically assigned for uncompleted daily tasks by a scheduled background job.
    - 1 missed task = 1 small penalty; 2+ missed tasks = 1 big penalty.
    - View and complete active penalties in the UI.
    - **Completed penalties are now logged in your Task History.** If you delete a completed penalty from the history, it will reappear as an active penalty to be completed again.
- **Detailed Money & Rewards**:
    - Earn a $50 reward for every 5 levels gained.
    - Track your total earnings, spending, and current balance.
    - Log purchases with a dedicated spending form and view your spending history.
- **Advanced Statistics**:
    - A dynamic radar chart visualizes the total XP you've earned in each category (e.g., Health, Learning, Social).
- **Task History & Admin Controls**:
    - **Scrollable, paginated task history**: View all completed tasks and penalties, 3 at a time, with navigation controls.
    - Delete any entry from your history to revert its effects (XP and completion status for tasks, or restore a penalty if deleted).
    - Securely reset all progress with a PIN-based confirmation.
    - ~~Undo your last task submission with a single click.~~ (Now replaced by granular task/penalty deletion in history.)

## Setup & Automation

### Running the App

1.  **Install Python 3.8+**
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```
4.  **(Optional) Create a desktop shortcut**:
    *   Open the app in Chrome.
    *   Go to **Menu > More Tools > Create Shortcut**.
    *   Name it "Level Up Tracker" and check "Open as window".

### Setting Up Automated Penalties (Cron Job on macOS/Linux)

To ensure penalties are assigned automatically every day, set up the included `auto_reset.py` script to run as a cron job.

1.  **Find your Python path**:
    ```bash
    which python
    ```
2.  **Open your crontab**:
    ```bash
    crontab -e
    ```
3.  **Add the job**: Add the following line, replacing `/path/to/your/python` with the output from step 1 and updating the script path if necessary. This example runs the job daily at 1:00 AM.
    ```
    0 1 * * * /path/to/your/python /Users/josephzhai/Documents/PersonalProj/Solo_Leveling/auto_reset.py
    ```
4.  **Save and exit** the editor.

## Project Structure

-   `app.py`: The main Streamlit application file.
-   `auto_reset.py`: The automation script for assigning daily penalties (now assigns unique IDs to penalties for tracking/restoration).
-   `data/`: Directory for JSON data files (`tasks.json`, `progress.json`, `rewards.json`).
-   `requirements.txt`: Project dependencies.
-   `Planning.txt`: The original project blueprint. 