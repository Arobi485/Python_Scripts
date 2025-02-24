import psutil
import time
import subprocess
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='minecraft_watchdog.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s')

# Configuration
MINECRAFT_PROCESS_NAME = "java.exe"  # Process name for Minecraft server
RESTART_BATCH_FILE = "startserver.bat"  # Your restart batch file
CHECK_INTERVAL = 30  # Seconds between checks

def is_minecraft_running():
    """Check if Minecraft server process is running"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == MINECRAFT_PROCESS_NAME:
                # You might want to add additional checks here
                # For example, check if the process is using specific ports
                # or check the command line arguments
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def restart_minecraft():
    """Restart the Minecraft server using the batch file"""
    try:
        logging.info("Attempting to restart Minecraft server...")
        subprocess.run([RESTART_BATCH_FILE], shell=True)
        logging.info("Restart command executed successfully")
    except Exception as e:
        logging.error(f"Error restarting server: {str(e)}")

def main():
    logging.info("Minecraft server watchdog started")
    
    while True:
        if not is_minecraft_running():
            logging.warning("Minecraft server process not found!")
            restart_minecraft()
            # Wait a bit longer after restart attempt
            time.sleep(60)
        else:
            logging.info("Minecraft server is running")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Watchdog stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")