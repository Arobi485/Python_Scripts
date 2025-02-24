import subprocess
import time
from ppadb.client import Client as AdbClient

class ADBConnection:
    def __init__(self):
        self.client = None
        self.device = None
    
    def start_adb_server(self):
        """Start ADB server and verify it's running"""
        try:
            # Kill any existing ADB server
            subprocess.run(['adb', 'kill-server'], 
                         check=True, 
                         capture_output=True)
            time.sleep(1)
            
            # Start ADB server
            subprocess.run(['adb', 'start-server'], 
                         check=True, 
                         capture_output=True)
            time.sleep(2)
            
            # Verify server is running
            result = subprocess.run(['adb', 'devices'], 
                                  check=True, 
                                  capture_output=True, 
                                  text=True)
            print("ADB Server started successfully")
            print(result.stdout)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error with ADB command: {e}")
            return False
        except FileNotFoundError:
            print("ADB not found. Please install Android SDK Platform Tools")
            return False
    
    def connect_to_device(self):
        """Connect to device using ppadb"""
        try:
            self.client = AdbClient(host="127.0.0.1", port=5037)
            devices = self.client.devices()
            
            if not devices:
                print("No devices found. Please check USB connection and USB debugging")
                return False
            
            self.device = devices[0]
            print(f"Connected to device: {self.device.serial}")
            return True
            
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return False
    
    def test_connection(self):
        """Test the connection by running a simple command"""
        if not self.device:
            print("No device connected")
            return False
        
        try:
            result = self.device.shell('echo "Testing ADB connection"')
            print(f"Test result: {result}")
            return True
        except Exception as e:
            print(f"Test failed: {e}")
            return False

def main():
    # Create connection handler
    adb = ADBConnection()
    
    print("Setting up ADB connection...")
    print("\n1. Starting ADB server...")
    if not adb.start_adb_server():
        print("Failed to start ADB server")
        return
    
    print("\n2. Connecting to device...")
    print("Please ensure:")
    print("- USB debugging is enabled on your phone")
    print("- Phone is connected via USB")
    print("- You accept the USB debugging prompt on your phone")
    input("Press Enter when ready...")
    
    if not adb.connect_to_device():
        print("Failed to connect to device")
        return
    
    print("\n3. Testing connection...")
    if adb.test_connection():
        print("\nConnection established successfully!")
    else:
        print("\nConnection test failed")

if __name__ == "__main__":
    main()