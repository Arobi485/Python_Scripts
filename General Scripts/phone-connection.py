# fast_phone_connection.py
from ppadb.client import Client as AdbClient
import threading
import queue
import time
import json
import struct
import logging
from typing import Optional, Dict, Any

class FastPhoneConnection:
    def __init__(self, buffer_size: int = 4096):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.device: Optional[Any] = None
        self.running = False
        self.buffer_size = buffer_size
        self.data_queue = queue.Queue()
        self.logging = logging.getLogger(__name__)
        
        # Performance metrics
        self.transfer_rates = []
        self.latencies = []
        
    def connect(self) -> bool:
        """Establish connection with the device"""
        try:
            devices = self.client.devices()
            if not devices:
                raise Exception("No devices connected")
            self.device = devices[0]
            
            # Set USB transfer mode to max speed
            self.device.shell('setprop sys.usb.config mtp,adb')
            return True
            
        except Exception as e:
            self.logging.error(f"Connection error: {e}")
            return False

    def start_high_speed_transfer(self):
        """Initialize high-speed data transfer"""
        self.running = True
        
        # Start separate threads for reading and processing
        self.read_thread = threading.Thread(target=self._read_data_loop)
        self.process_thread = threading.Thread(target=self._process_data_loop)
        
        self.read_thread.start()
        self.process_thread.start()

    def _read_data_loop(self):
        """High-performance data reading loop"""
        try:
            # Create a direct pipe for faster data transfer
            pipe = self.device.create_connection(timeout=1000)
            
            while self.running:
                start_time = time.perf_counter()
                
                # Read raw bytes
                data = pipe.read(self.buffer_size)
                
                if data:
                    # Calculate transfer rate
                    elapsed = time.perf_counter() - start_time
                    rate = len(data) / elapsed
                    self.transfer_rates.append(rate)
                    
                    # Put data in queue for processing
                    self.data_queue.put((data, start_time))
                
        except Exception as e:
            self.logging.error(f"Read error: {e}")
            self.running = False

    def _process_data_loop(self):
        """Process received data efficiently"""
        while self.running:
            try:
                if not self.data_queue.empty():
                    data, start_time = self.data_queue.get()
                    
                    # Process the data
                    processed_data = self._fast_process_data(data)
                    
                    # Calculate latency
                    latency = time.perf_counter() - start_time
                    self.latencies.append(latency)
                    
                    # Handle the processed data
                    self._handle_processed_data(processed_data)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.logging.error(f"Processing error: {e}")

    def _fast_process_data(self, data: bytes) -> Dict:
        """Process data with minimal overhead"""
        try:
            # Use struct for faster parsing of binary data
            # This is an example assuming specific data format
            # Modify according to your actual data structure
            format_string = 'fff'  # Example: 3 float values
            unpacked = struct.unpack(format_string, data[:12])
            
            return {
                'x': unpacked[0],
                'y': unpacked[1],
                'z': unpacked[2],
                'timestamp': time.time()
            }
            
        except struct.error:
            return self._fallback_process_data(data)

    def _fallback_process_data(self, data: bytes) -> Dict:
        """Fallback data processing method"""
        try:
            return json.loads(data.decode('utf-8'))
        except json.JSONDecodeError:
            return {'raw_data': data}

    def _handle_processed_data(self, data: Dict):
        """Handle the processed data"""
        # Example: Print transfer statistics
        avg_rate = sum(self.transfer_rates[-100:]) / min(len(self.transfer_rates), 100)
        avg_latency = sum(self.latencies[-100:]) / min(len(self.latencies), 100)
        
        print(f"Data: {data}")
        print(f"Avg Transfer Rate: {avg_rate:.2f} bytes/s")
        print(f"Avg Latency: {avg_latency*1000:.2f} ms")

    def stop(self):
        """Stop the data transfer"""
        self.running = False
        if hasattr(self, 'read_thread'):
            self.read_thread.join()
        if hasattr(self, 'process_thread'):
            self.process_thread.join()

# Example usage with performance monitoring
def main():
    # Initialize connection
    phone = FastPhoneConnection(buffer_size=8192)  # Larger buffer for better performance
    
    if not phone.connect():
        print("Failed to connect to device")
        return

    try:
        # Start high-speed transfer
        phone.start_high_speed_transfer()
        
        # Run for specified duration
        time.sleep(60)
        
    finally:
        phone.stop()
        
        # Print performance statistics
        avg_rate = sum(phone.transfer_rates) / len(phone.transfer_rates)
        avg_latency = sum(phone.latencies) / len(phone.latencies)
        
        print(f"\nPerformance Statistics:")
        print(f"Average Transfer Rate: {avg_rate:.2f} bytes/s")
        print(f"Average Latency: {avg_latency*1000:.2f} ms")
        print(f"Total Data Transferred: {sum(phone.transfer_rates):.2f} bytes")

if __name__ == "__main__":
    main()