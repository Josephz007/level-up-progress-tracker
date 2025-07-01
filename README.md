# 🎮 Level Up - Life Progress Tracker

A gamified desktop application that transforms your daily tasks and goals into an RPG experience, inspired by Solo Leveling. Track your progress, earn XP, level up, and unlock rewards in real life!

![Level Up Tracker](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)

## ✨ Features

### 🎯 **Core Gameplay**
- **Dynamic Task Tracking**: Manage daily, weekly, monthly, and one-time tasks with separate submission buttons
- **XP & Leveling System**: Gain experience points for completing tasks and watch your level grow (100 XP per level)
- **Money & Rewards**: Earn $50 for every 5 levels and spend on custom rewards
- **Grace Period System**: 1-hour buffer after deadlines to complete tasks without penalties

### ⏰ **Smart Time Management**
- **Real-time Countdown Timers**: Visual timers for each task category
- **Grace Period Indicators**: Clear indication when grace period is active
- **Automated Penalty System**: Background cron job assigns penalties for missed daily tasks
- **Period-based Tracking**: Tasks reset automatically based on their category

### 🎨 **Advanced UI & Analytics**
- **Interactive Radar Chart**: Visualize XP earned per category with fixed 1000 XP scale
- **Task History Log**: Scrollable, paginated history with delete functionality
- **Money Tracking**: Complete spending history and balance management
- **Modern Design**: Clean, responsive interface with smooth animations

### 🔒 **Privacy & Data Management**
- **Personal Data Protection**: Progress and rewards data excluded from repository
- **Template System**: Easy setup with template files for new users
- **Secure Reset**: PIN-protected progress reset functionality
- **Granular Control**: Delete individual tasks/penalties from history

### 🖥️ **Desktop Integration**
- **Native Desktop App**: Double-click launcher for macOS (`Level Up.app`)
- **Automatic Conda Support**: Uses your active conda environment (e.g., `tf`) for Streamlit and dependencies
- **Automatic Browser Launch**: Opens app in default browser
- **Background Server**: Runs Streamlit server automatically
- **Custom App Icon**: Uses your provided `levelup_logo.png` as the app icon
- **Easy Installation**: Simple setup scripts for desktop integration

## 🚀 Quick Start

### **Option 1: Desktop App (Recommended)**
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Josephz007/level-up-progress-tracker.git
   cd level-up-progress-tracker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create desktop app**:
   (If not already present, follow your setup script or instructions to create `Level Up.app`)

4. **Launch**: Double-click `Level Up.app`! The app will automatically use your conda environment and open in your browser.

#### **Troubleshooting: App Icon Not Showing?**
If the app icon is blank or doesn't update:
- Try killing the Dock and Finder:
  ```bash
  killall Dock; killall Finder
  ```
- Move the app to a different folder and back
- Restart your Mac if needed

### **Option 2: Traditional Launch**
1. **Clone and install** (steps 1-2 above)
2. **Initialize data files**:
   ```bash
   cp data/progress_template.json data/progress.json
   cp data/rewards_template.json data/rewards.json
   ```
3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## 🖥️ Build the macOS Desktop App Bundle

To create the Level Up.app bundle on your Mac, just run:

```bash
bash create_desktop_app.sh
```

- This will build the app bundle from your code and icon.
- After running, you can double-click `Level Up.app` to launch the tracker like a native app!
- If you update your code or icon, just re-run the script to refresh the app bundle.

## 📁 Project Structure

```
level-up-progress-tracker/
├── app.py                          # Main Streamlit application
├── auto_reset.py                   # Automated penalty assignment script
├── system_flowchart.html           # Interactive system architecture diagram
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── Planning.txt                    # Original project blueprint
├── data/
│   ├── tasks.json                  # Task definitions (included)
│   ├── progress_template.json      # Template for personal progress
│   ├── rewards_template.json       # Template for personal rewards
│   ├── progress.json              # Your personal progress (not in repo)
│   └── rewards.json               # Your personal rewards (not in repo)
├── levelup_logo.png                # Custom app icon (user-provided)
└── Level Up.app/                   # Desktop application bundle
    ├── Contents/
    │   ├── Info.plist              # macOS app metadata
    │   ├── MacOS/
    │   │   └── launcher            # Bash launcher (activates conda, runs Python)
    │   └── Resources/
    │       ├── icon.png            # App icon (copied from levelup_logo.png)
    │       └── launch_desktop.py   # Python launcher script
```

## ⚙️ Advanced Setup

### **Automated Penalties (Cron Job)**

Set up automatic penalty assignment for missed daily tasks:

1. **Find your Python path**:
   ```bash
   which python
   ```

2. **Open crontab**:
   ```bash
   crontab -e
   ```

3. **Add the job** (runs daily at 1:00 AM):
   ```
   0 1 * * * /path/to/your/python /path/to/level-up-progress-tracker/auto_reset.py
   ```

### **Customization**

- **Add Tasks**: Edit `data/tasks.json` to customize your task list
- **Modify Rewards**: Update `data/rewards_template.json` for personal rewards
- **Adjust Penalties**: Modify penalty lists in `auto_reset.py`
- **Change XP Values**: Update XP amounts in `data/tasks.json`

## 🎮 How to use

### **Daily Routine**
1. **Open the app** (desktop icon or `streamlit run app.py`)
2. **Check your tasks** for the day/week/month
3. **Complete tasks** and click submit buttons
4. **Earn XP** and watch your level increase
5. **Claim rewards** when you reach level milestones
6. **Check penalties** if you missed daily tasks

### **Task Categories**
- **Daily**: Reset every day at 1:00 AM (with 1-hour grace period)
- **Weekly**: Reset every Monday at 1:00 AM
- **Monthly**: Reset on the 1st of each month at 1:00 AM
- **One-time**: Complete once and done

### **Penalty System**
- **1 missed daily task**: Small penalty (vacuum, stretching, etc.)
- **2+ missed daily tasks**: Big penalty (run, cold shower, etc.)
- **Automatic assignment**: Cron job runs daily at 1:00 AM
- **Complete penalties**: Mark as done in the app

## 🔧 System Architecture

The application uses a modular architecture with clear separation of concerns:

- **Data Layer**: JSON files for persistent storage
- **Business Logic**: Python functions for XP calculation, task tracking
- **UI Layer**: Streamlit components for user interaction
- **Automation**: Cron job for background penalty assignment
- **Desktop Integration**: Native app wrapper for easy access

See `system_flowchart.html` for a detailed interactive diagram of the system architecture.

## 🛡️ Privacy & Security

- **Personal Data**: Your progress and rewards are stored locally and excluded from the repository
- **Template System**: New users get clean template files to start fresh
- **No Cloud Storage**: All data stays on your computer
- **Secure Reset**: PIN-protected reset prevents accidental data loss



**Ready to level up your life? Start your journey today!** 🚀✨ 
