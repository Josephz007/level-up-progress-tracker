#imports
import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import calendar
import random
import plotly.graph_objects as go

#Constants
DATA_DIR = "data"
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")
REWARDS_FILE = os.path.join(DATA_DIR, "rewards.json")


### Load and Save Functions

def load_json_file(file_path):
    """
    Loads a JSON file from the specified path.
    Args:
        file_path (str): The path to the JSON file.
    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """
    Saves a dictionary to a JSON file.
    Args:
        file_path (str): The path to the JSON file.
        data: The data to save to the JSON file.
    Returns:
        None
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

### Session State Functions

def initialize_session_state():
    """
    Loads data from JSON files into session state.
    This now reloads on every rerun to ensure external changes (like from a cron job) are reflected.
    Args:
        None
    Returns:
        None
    """
    # Always reload data from disk to catch external changes
    st.session_state.tasks = load_json_file(TASKS_FILE)
    st.session_state.progress = load_json_file(PROGRESS_FILE)
    st.session_state.rewards = load_json_file(REWARDS_FILE)

    # Initialize UI-specific state (like checkbox values) only once per session
    if 'task_checks' not in st.session_state:
        st.session_state.task_checks = {}
        for ttype in ['daily', 'weekly', 'monthly', 'one_time']:
            for task in st.session_state.tasks[ttype]:
                st.session_state.task_checks[f"{ttype}_{task['name']}"] = False

### XP Calculation Functions

def calculate_level(xp):
    """
    Calculates the level based on the experience points (XP).
    Args:
        xp (int): The experience points.
    Returns:
        int: The calculated level.
    """
    return (xp // 100) + 1

def calculate_xp_to_next_level(xp):
    """
    Calculates the experience points needed to reach the next level.
    Args:
        xp (int): The experience points.
    Returns:
        int: The experience points needed to reach the next level.
    """
    current_level = calculate_level(xp)
    return current_level * 100 - xp

### Time Left Functions

def get_time_left(category):
    """
    Gets the time left for a task based on its category.
    Args:
        category (str): The category of the task.
    Returns:
        tuple: A tuple containing the time left as a string and a boolean indicating if the grace period is active.
    """
    now = datetime.now()
    grace = timedelta(hours=1)
    grace_on = False
    if category == "daily":
        end_of_day = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        hours_left = (end_of_day - now).total_seconds() / 3600
        # Grace period: after midnight but before 1am
        if now.time() < (datetime.min + grace).time():
            grace_on = True
        timer_str = f"⏰ {int(hours_left)}h {int((hours_left%1)*60)}m left today"
    elif category == "weekly":
        days_left = 6 - now.weekday()
        # Grace period: before 1am on Monday
        week_start = now - timedelta(days=now.weekday())
        week_start_1am = datetime.combine(week_start.date(), datetime.min.time()) + grace
        if now < week_start_1am:
            grace_on = True
        timer_str = f"⏰ {days_left+1} day{'s' if days_left else ''} left this week"
    elif category == "monthly":
        last_day = calendar.monthrange(now.year, now.month)[1]
        days_left = last_day - now.day
        # Grace period: before 1am on the 1st
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_1am = month_start + grace
        if now < month_start_1am:
            grace_on = True
        timer_str = f"⏰ {days_left+1} day{'s' if days_left else ''} left this month"
    else:
        return None, False
    return timer_str, grace_on

def get_period_key(category):
    """
    Gets the period key based on the category of the task. This is needed because tasks can be done on different days, weeks, or months due to the grace period.
    Args:
        category (str): The category of the task.
    Returns:
        str: The period key, which is essentially the date or week or month, for example 2025-06-22, 2025-W25, 2025-06.
    """
    now = datetime.now()
    grace = timedelta(hours=1)
    
    if category == "daily":
        # If before 1am, use previous day as period key
        if now.time() < (datetime.min + grace).time():
            period_date = now.date() - timedelta(days=1)
        else:
            period_date = now.date()
        return period_date.strftime("%Y-%m-%d")
    elif category == "weekly":
        # If before 1am on Monday, use previous week
        week_start = now - timedelta(days=now.weekday())
        week_start_1am = datetime.combine(week_start.date(), datetime.min.time()) + grace
        if now < week_start_1am:
            prev_week = now - timedelta(weeks=1)
            return f"{prev_week.isocalendar()[0]}-W{prev_week.isocalendar()[1]}"
        else:
            return f"{now.isocalendar()[0]}-W{now.isocalendar()[1]}"
    elif category == "monthly":
        # If before 1am on the 1st, use previous month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_start_1am = month_start + grace
        if now < month_start_1am:
            prev_month = (now.replace(day=1) - timedelta(days=1))
            return prev_month.strftime("%Y-%m")
        else:
            return now.strftime("%Y-%m")
    elif category == "one-time":
        return "one-time"
    return None

### Task Completion Functions

def get_task_completion_count(progress, category, task_name):
    """
    Gets the completion count of a task for the current period.
    Args:
        progress (dict): The progress dictionary.
        category (str): The category of the task.
        task_name (str): The name of the task.
    Returns:
        int: The completion count of the task for the current period.
    """
    period_key = get_period_key(category)
    if category == "one-time":
        # One-time tasks are either done (1) or not (0).
        return 1 if progress.get('completed_tasks', {}).get(category, {}).get(task_name) else 0
    #returns 0 if the task is not completed for the current period
    return progress.get('completed_tasks', {}).get(category, {}).get(task_name, {}).get(period_key, 0) 

def mark_tasks_completed(progress, category, tasks_to_increment):
    """
    Increments the completion count for a list of tasks for the current period.
    Args:
        progress (dict): The progress dictionary.
        category (str): The category of the tasks.
        tasks_to_increment (list): The list of task names to increment.
    Returns:
        None
    """
    period_key = get_period_key(category)
    if category not in progress['completed_tasks']:
        progress['completed_tasks'][category] = {} #initialize the category if it doesn't exist
    
    for task_name in tasks_to_increment: #increment the completion count for each task
        if task_name not in progress['completed_tasks'][category]:
            progress['completed_tasks'][category][task_name] = {} #initialize the task if it doesn't exist
        
        current_count = progress['completed_tasks'][category][task_name].get(period_key, 0) #get the current count for the task
        progress['completed_tasks'][category][task_name][period_key] = current_count + 1 # increment the count for the task
        
    save_json_file(PROGRESS_FILE, progress) 

def assign_penalties(progress, unchecked_count):
    """
    Assigns penalties based on the unchecked count.
    Args:
        progress (dict): The progress dictionary.
        unchecked_count (int): The number of unchecked tasks.
    Returns:
        None
    """
    penalties = progress.get('penalties', []) #get the penalties from the progress dictionary
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
        penalty = random.choice(small_penalties)
        penalties.append({ 
            'due_date': tomorrow, 
            'description': penalty,
            'completed': False
        })
    elif unchecked_count >= 2:
        penalty = random.choice(big_penalties)
        penalties.append({
            'due_date': tomorrow,
            'description': penalty,
            'completed': False
        })
    progress['penalties'] = penalties
    save_json_file(PROGRESS_FILE, progress)

### UI Functions

def render_penalties_section():
    """
    Renders the penalties section.
    Args:
        None
    Returns:
        None
    """
    st.subheader("Penalties", divider="gray")
    progress = st.session_state.progress
    penalties = progress.get('penalties', [])
    
    active_penalties_with_indices = [
        (i, p) for i, p in enumerate(penalties) if not p.get('completed', False) #only show the penalties that are not completed, i is the index of the penalty and p is the penalty
    ]

    if not active_penalties_with_indices:
        st.write("No active penalties!")
    else:
        for original_index, penalty in active_penalties_with_indices:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.warning(f"Due: {penalty['due_date']} - {penalty['description']}")
            with col2:
                if st.button("Mark Completed", key=f"penalty_{original_index}"):
                    #Assign an ID if not present (for backward compatibility)
                    penalty.setdefault('id', f"pen-{datetime.now().timestamp()}-{original_index}")
                    penalty['completed'] = True
                    
                    # Add to detailed_logs to track the penalty
                    if 'detailed_logs' not in progress:
                        progress['detailed_logs'] = []
                    
                    progress['detailed_logs'].append({
                        "name": penalty['description'],
                        "xp": 0,
                        "category": ["Penalty"],
                        "type": "penalty",
                        "date": date.today().isoformat(),
                        "penalty_id": penalty['id']
                    })
                    
                    save_json_file(PROGRESS_FILE, progress)
                    st.success("Penalty marked as completed and logged in history!")
                    st.rerun()

def render_task_section(task_type, tasks):
    """
    Renders the task section.
    Args:
        task_type (str): The type of task.
        tasks (list): The list of tasks.
    Returns:
        None
    """
    timer, grace_on = get_time_left(task_type)
    header = f"{task_type.capitalize()} Tasks"
    if timer: #if the task type is daily, weekly, or monthly, show the timer
        st.subheader(f"{header}  ", divider="gray")
        grace_note = "Grace period active" if grace_on else "Grace period off"
        st.caption(f"{timer}  |  {grace_note}")
    else:
        st.subheader(header, divider="gray") #if the task type is one-time, don't show the timer
    checked = [] #list of currently checked tasks
    progress = st.session_state.progress
    period_key = get_period_key(task_type)
    for task in tasks: #render the tasks
        col1, col2 = st.columns([3, 1]) #split the screen into two columns
        with col1:
            key = f"{task_type}_{task['name']}"
            frequency = task.get('frequency', 1)
            completion_count = get_task_completion_count(progress, task_type, task['name'])
            
            is_maxed_out = completion_count >= frequency 
            
            label = f"{task['name']} ({task['xp']} XP)" #name of the task and the XP it's worth
            if frequency > 1:
                label = f"({completion_count}/{frequency}) {label}"

            if is_maxed_out:
                st.checkbox(
                    f"{label} — Completed",
                    key=key,
                    value=True,
                    disabled=True,
                    help=task['description']
                )
            else: #if task is not maxed out, show the checkbox!!
                is_checked = st.checkbox(
                    label,
                    key=key,
                    value=st.session_state.task_checks.get(key, False),
                    help=task['description']
                )
                if is_checked: #if the checkbox is checked, add the task to the list of checked tasks
                    checked.append(task['name'])
        with col2:
            st.write(f"Category: {', '.join(task.get('category', task.get('tags', [])))}") #show the category of the task
     
    
    #Submit button for this category
    if checked:
        if st.button(f"Submit {task_type.capitalize()} Tasks", key=f"submit_{task_type}"): #if the submit button is clicked, mark the tasks as completed
            # Pass the list of checked task names to increment their counts
            mark_tasks_completed(progress, task_type, checked)
            # Award XP and log each completed task with details
            earned_xp = sum([t['xp'] for t in tasks if t['name'] in checked])
            completed_log = []
            today = date.today().isoformat()
            for task in tasks:
                if task['name'] in checked:
                    completed_log.append({
                        "name": task['name'],
                        "xp": task['xp'],
                        "category": task.get('category', task.get('tags', [])),
                        "type": task_type,
                        "date": today,
                        "period_key": period_key
                    })
            progress['current_xp'] += earned_xp
            progress['current_level'] = (progress['current_xp'] // 100) + 1
            progress['xp_to_next_level'] = progress['current_level'] * 100 - progress['current_xp']
            if 'detailed_logs' not in progress:
                progress['detailed_logs'] = []
            progress['detailed_logs'].extend(completed_log)
            save_json_file(PROGRESS_FILE, progress)
            
            # Reset checkboxes for this category
            for task_name in checked:
                st.session_state.task_checks[f"{task_type}_{task_name}"] = False #reset the checkbox for the task
            st.success(f"Submitted! You earned {earned_xp} XP for {task_type} tasks.")
            st.rerun()

def render_money_tracking():
    """
    Renders the money tracking section.
    Args:
        None
    Returns:
        None
    """
    st.subheader("💰 Money Tracking")
    money = st.session_state.rewards['money_tracking']
    #Ensure all values are float for calculations
    current_balance = float(money['current_balance'])
    total_earned = float(money['total_earned'])
    total_spent = float(money['total_spent'])
    #Display current balance and totals
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"${current_balance}")
    with col2:
        st.metric("Total Earned", f"${total_earned}")
    with col3:
        st.metric("Total Spent", f"${total_spent}")
    #Add spending form only if balance > 0
    with st.expander("Document Your Spending Here"):
        if current_balance > 0:
            with st.form("spending_form"):
                amount = st.number_input("Amount ($)", min_value=0.01, max_value=current_balance, step=0.01)
                description = st.text_input("What did you spend it on?")
                submitted = st.form_submit_button("Add Spending")
                if submitted and amount and description:
                    # Update money tracking
                    money['total_spent'] = float(money['total_spent']) + float(amount)
                    money['current_balance'] = float(money['current_balance']) - float(amount)
                    money['spending_history'].append({
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'amount': float(amount),
                        'description': description
                    })
                    save_json_file(REWARDS_FILE, st.session_state.rewards)
                    st.success("Spending recorded!")
                    st.rerun()
        else:
            st.info("No funds available to spend. Claim a reward to add money to your balance!")
    # Display spending history
    if money['spending_history']:
        st.subheader("Spending History")
        history_df = pd.DataFrame(money['spending_history'])
        st.dataframe(history_df)

def process_task_submission():
    """
    Processes the task submission.
    Args:
        None
    Returns:
        None
    """
    tasks = st.session_state.tasks
    checks = st.session_state.task_checks
    progress = st.session_state.progress
    today = date.today().isoformat()
    completed = {"daily": [], "weekly": [], "monthly": [], "one_time": []} #list of completed tasks
    earned_xp = 0
    for ttype in ["daily", "weekly", "monthly", "one_time"]: #for each task type, check if the task is completed
        for task in tasks[ttype]:
            key = f"{ttype}_{task['name']}"
            if checks.get(key, False):
                completed[ttype].append(task['name']) # Add the task to the list of completed tasks
                earned_xp += int(task['xp'])
    # Update the progress
    progress['current_xp'] += earned_xp
    new_level = calculate_level(progress['current_xp']) #calculate the new level
    leveled_up = new_level > progress['current_level'] #check if the user leveled up
    progress['current_level'] = new_level #Update the current level
    progress['xp_to_next_level'] = calculate_xp_to_next_level(progress['current_xp']) #calculate the XP needed to reach the next level
    
    # Log the day
    progress['daily_logs'].append({
        "date": today,
        "completed": completed,
        "earned_xp": earned_xp,
        "level": progress['current_level']
    })
    save_json_file(PROGRESS_FILE, progress)
    # Reset checkboxes
    for key in checks:
        checks[key] = False
    return earned_xp, completed, leveled_up, new_level

def reset_progress_and_rewards():
    """
    Resets the progress and rewards. Used when the user wants to reset their progress and rewards.
    Args:
        None
    Returns:
        None
    """
    # Load initial states from files or hardcode them
    initial_progress = {
        "current_level": 1,
        "current_xp": 0,
        "xp_to_next_level": 100,
        "daily_logs": [],
        "detailed_logs": [],
        "penalties": [],
        "completed_tasks": {
            "daily": {},
            "weekly": {},
            "monthly": {},
            "one_time": []
        }
    }
    initial_rewards = {
        "rewards": [
            {"level": lvl, "description": "$50 to spend on yourself", "claimed": False}
            for lvl in range(5, 55, 5)
        ],
        "money_tracking": {
            "total_earned": 0,
            "total_spent": 0,
            "current_balance": 0,
            "spending_history": []
        }
    }
    save_json_file(PROGRESS_FILE, initial_progress)
    save_json_file(REWARDS_FILE, initial_rewards)
    st.session_state.progress = initial_progress
    st.session_state.rewards = initial_rewards
    if 'task_checks' in st.session_state:
        for key in st.session_state.task_checks:
            st.session_state.task_checks[key] = False
    st.success("Progress and rewards have been reset!")
    st.rerun()

def get_xp_per_category():
    """
    Gets the XP earned per category from the detailed_logs.
    Args:
        None
    Returns:
        dict: A dictionary with the category as the key and the XP earned as the value.
    """
    # Aggregate XP earned per category from detailed_logs
    progress = st.session_state.progress
    if 'detailed_logs' not in progress:
        return {}
    xp_by_cat = {}
    for entry in progress['detailed_logs']: #for each entry in the detailed_logs, add the XP earned to the category
        for cat in entry.get('category', []): #for each category in the entry, add the XP earned to the category
            xp_by_cat[cat] = xp_by_cat.get(cat, 0) + entry.get('xp', 0) #add the XP earned to the category
    return xp_by_cat

def render_radar_chart():
    """
    Renders the xp radar chart. 
    Args:
        None
    Returns:
        None
    """
    xp_by_cat = get_xp_per_category()
    # Get all possible categories from tasks
    tasks = st.session_state.tasks
    all_cats = set()
    for ttype in tasks: #for each task type, add the categories to the set
        for task in tasks[ttype]:
            cats = task.get('category', task.get('tags', []))
            for cat in cats:
                all_cats.add(cat)
    all_cats = sorted(list(all_cats))
    
    categories = all_cats
    values = [xp_by_cat.get(cat, 0) for cat in categories]
    msg = None
    if not any(v > 0 for v in values):
        msg = "No XP earned yet. Complete tasks to see your stats!"

    # Close the loop for radar
    categories += categories[:1] #close the loop by adding the first category to the end
    values += values[:1] #close the loop by adding the first value to the end
    fig = go.Figure(
        data=[go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='purple', fillcolor='rgba(128,0,128,0.3)')]
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1000]  #Set the max value to 1000 XP (future update: allow the user to set the max value)
            )
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)
    if msg:
        st.info(msg)

def render_task_history():
    """
    Renders the task history with completion dates and delete buttons.
    Args:
        None
    Returns:
        None
    """
    progress = st.session_state.progress
    tasks = st.session_state.tasks
    
    if 'detailed_logs' not in progress or not progress['detailed_logs']:
        st.info("No task history yet. Complete some tasks to see your history!")
        return
    
    #Sort logs by completion date (newest first)
    sorted_logs = sorted(progress['detailed_logs'], key=lambda x: x.get('date', ''), reverse=True)
    
    # Initialize page state if not exists
    if 'task_history_page' not in st.session_state:
        st.session_state.task_history_page = 0
    
    # Calculate number of pages
    tasks_per_page = 3
    total_pages = (len(sorted_logs) + tasks_per_page - 1) // tasks_per_page
    if total_pages == 0: total_pages = 1 # Avoid page 1 of 0
    start_idx = st.session_state.task_history_page * tasks_per_page
    end_idx = min(start_idx + tasks_per_page, len(sorted_logs))
    current_tasks = sorted_logs[start_idx:end_idx]

    # Title and Navigation on the same line (flattened to avoid nesting error)
    col1, col2, col3, col4 = st.columns([5, 2, 3, 2])
    with col1:
        st.markdown("#### Task History")

    with col2:
        if st.button("← Prev", disabled=st.session_state.task_history_page == 0, use_container_width=True):
            st.session_state.task_history_page -= 1
            st.rerun()

    with col3:
        st.markdown(f"<p style='text-align: center; white-space: nowrap;'>Page {st.session_state.task_history_page + 1} of {total_pages}</p>", unsafe_allow_html=True)

    with col4:
        if st.button("Next →", disabled=st.session_state.task_history_page >= total_pages - 1, use_container_width=True):
            st.session_state.task_history_page += 1
            st.rerun()
    
    # Display current page of tasks
    for i, log in enumerate(current_tasks):
        task_name = log.get('name', 'Unknown Task')
        completion_date = log.get('date', 'Unknown Date')
        xp_earned = log.get('xp', 0)
        categories = log.get('category', [])
        
        # More compact layout
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1: #task name and completion date
            st.write(f"**{task_name}**")
            st.caption(f"{completion_date} • {', '.join(categories)}")
        
        with col2: #XP earned
            st.write(f"{xp_earned} XP")
        
        with col3: #delete button
            if st.button("🗑️", key=f"delete_task_{start_idx + i}", help="Delete this task and deduct XP"):
                # Find the actual index in the full detailed_logs and remove it
                actual_index = progress['detailed_logs'].index(log)
                log_entry = progress['detailed_logs'].pop(actual_index)

                task_type = log_entry.get('type')
                xp_earned = log_entry.get('xp', 0)
                log_name = log_entry.get('name', 'Unknown')

                if task_type == 'penalty':
                    penalty_id = log_entry.get('penalty_id')
                    if penalty_id:
                        # Find the penalty in the main list and mark as not completed
                        for p in progress.get('penalties', []):
                            if p.get('id') == penalty_id:
                                p['completed'] = False
                                break
                    st.success(f"Penalty '{log_name}' restored.")
                else: # It's a regular task
                    task_name = log_entry.get('name')
                    period_key = log_entry.get('period_key')

                    # Decrement the completion count if period_key is available
                    if task_type and task_name and period_key:
                        counts = progress.get('completed_tasks', {}).get(task_type, {}).get(task_name, {})
                        if counts and period_key in counts:
                            counts[period_key] -= 1
                            if counts[period_key] < 0:
                                counts[period_key] = 0
                    
                    # Deduct XP
                    progress['current_xp'] -= xp_earned
                    if progress['current_xp'] < 0:
                        progress['current_xp'] = 0
                    
                    # Recalculate level
                    progress['current_level'] = (progress['current_xp'] // 100) + 1
                    progress['xp_to_next_level'] = progress['current_level'] * 100 - progress['current_xp']
                    st.success(f"Task '{log_name}' deleted! {xp_earned} XP deducted.")
                
                save_json_file(PROGRESS_FILE, progress)
                st.rerun()
        
        #add a small divider between tasks
        st.markdown("---")
    
    # Show total count
    if sorted_logs:
        st.caption(f"Total: {len(sorted_logs)} tasks completed")

def main():
    """
    Main function to run the app.
    Args:
        None
    Returns:
        None
    """
    st.set_page_config(
        page_title="Level Up - Progress Tracker",
        page_icon="🎮",
        layout="wide"
    )
    initialize_session_state()
    # Sidebar: Reset Progress Button with PIN and Undo
    with st.sidebar:
        st.header("Settings")
        if 'show_pin_input' not in st.session_state:
            st.session_state.show_pin_input = False
        if 'reset_pin' not in st.session_state:
            st.session_state.reset_pin = ""
        if 'clear_pin' not in st.session_state:
            st.session_state.clear_pin = False
        if st.button("Delete All Progress (Reset)", type="secondary"):
            st.session_state.show_pin_input = True
        # Clear the PIN before rendering the widget if needed
        if st.session_state.clear_pin:
            st.session_state.reset_pin = ""
            st.session_state.clear_pin = False
        if st.session_state.show_pin_input:
            st.text_input("Enter PIN to confirm reset:", type="password", key="reset_pin", value=st.session_state.reset_pin, on_change=None)
            if st.button("Confirm Reset"):
                pin = st.session_state.reset_pin
                if pin == "1849487":
                    st.session_state.clear_pin = True
                    st.session_state.show_pin_input = False
                    reset_progress_and_rewards()
                else:
                    st.error("Incorrect PIN. Progress was not deleted.")
                    st.session_state.clear_pin = True
                    st.session_state.show_pin_input = False

    # Header
    st.title("Level Up: Progress Tracker")
    # Progress Bar
    current_xp = st.session_state.progress['current_xp']
    current_level = st.session_state.progress['current_level']
    xp_to_next = st.session_state.progress['xp_to_next_level']
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.progress(current_xp / (current_level * 100))
    with col2:
        st.metric("Level", current_level)
    with col3:
        st.metric("XP", f"{current_xp}/{current_level * 100}")
    # Task History and Radar Chart
    radar_col, history_col = st.columns(2)
    with radar_col:
        st.markdown("#### XP Earned by Category")
        render_radar_chart()
    with history_col:
        # Create a compact, scrollable task history
        with st.container():
            render_task_history()

    # Main Content
    col1, col2 = st.columns([2, 1])
    with col1:
        # Task Sections are now self-contained with their dividers
        render_task_section("daily", st.session_state.tasks['daily'])
        render_task_section("weekly", st.session_state.tasks['weekly'])
        render_task_section("monthly", st.session_state.tasks['monthly'])
        render_task_section("one-time", st.session_state.tasks['one_time'])
        render_penalties_section()
    with col2:
        # Money Tracking Section
        render_money_tracking()
        st.markdown("---")
        # Rewards Section
        st.subheader("Available Rewards")
        for reward in st.session_state.rewards['rewards']:
            reward_level = reward['level']
            desc = f"Level {reward_level}: {reward['description']}"
            if reward['claimed']:
                st.success(f"{desc} — Completed!")
            else:
                st.info(desc)
                # Progress bar toward this reward
                progress = min(st.session_state.progress['current_level'] / reward_level, 1.0)
                st.progress(progress, text=f"Progress: Level {st.session_state.progress['current_level']} / {reward_level}")
                if st.session_state.progress['current_level'] >= reward_level:
                    if st.button(f"Claim Reward", key=f"claim_{reward_level}"):
                        reward['claimed'] = True
                        # Update money tracking when claiming reward
                        st.session_state.rewards['money_tracking']['total_earned'] = float(st.session_state.rewards['money_tracking']['total_earned']) + 50
                        st.session_state.rewards['money_tracking']['current_balance'] = float(st.session_state.rewards['money_tracking']['current_balance']) + 50
                        save_json_file(REWARDS_FILE, st.session_state.rewards)
                        st.rerun()

if __name__ == "__main__": #run the main function
    main() 