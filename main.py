import subprocess
import os

# Define the path to the script
script_path = os.path.join('.', 'src', 'GUI', 'login.py')

# Start the script
try:
    subprocess.run(['python', script_path], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error occurred while running the script: {e}")