# test_connection.py
from ppadb.client import Client as AdbClient

def test_adb_connection():
    try:
        # Initialize ADB client
        client = AdbClient(host="127.0.0.1", port=5037)
        
        # Get devices
        devices = client.devices()
        
        if not devices:
            print("No devices connected")
            return False
            
        device = devices[0]
        print(f"Connected to {device.serial}")
        
        # Test command
        result = device.shell('echo "Test successful"')
        print(f"Command result: {result}")
        
        return True
        
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_adb_connection()