#!/usr/bin/env python3
"""
Desktop Launcher for Level Up - Life Progress Tracker
This script launches the Streamlit app and opens it in your default browser.
"""

import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def launch_app():
    """Launch the Streamlit app and open in browser"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Navigate to the main project directory (parent of the .app bundle)
    project_dir = script_dir.parent.parent.parent
    
    # Change to the project directory where app.py is located
    os.chdir(project_dir)
    
    print("🚀 Launching Level Up - Life Progress Tracker...")
    print("📁 Working directory:", project_dir)
    
    try:
        # Start Streamlit process
        print("⚙️ Starting Streamlit server...")
        
        # Try to use conda environment if available, otherwise fall back to system Python
        python_executable = sys.executable
        
        # Check if we're in a conda environment
        if 'CONDA_PREFIX' in os.environ:
            conda_python = os.path.join(os.environ['CONDA_PREFIX'], 'bin', 'python')
            if os.path.exists(conda_python):
                python_executable = conda_python
                print(f"🐍 Using conda Python: {python_executable}")
        
        streamlit_process = subprocess.Popen([
            python_executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
        
        # Wait a moment for the server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Open in default browser
        print("🌐 Opening in browser...")
        webbrowser.open("http://localhost:8501")
        
        print("✅ App launched successfully!")
        print("📱 Your Level Up Tracker is now running in your browser")
        print("🔄 The app will automatically reload when you make changes")
        print("❌ Press Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            streamlit_process.terminate()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        print("💡 Make sure you have Streamlit installed: pip install streamlit")
        return False
    
    return True

if __name__ == "__main__":
    launch_app() 