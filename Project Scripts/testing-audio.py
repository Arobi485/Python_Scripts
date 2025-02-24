import sounddevice as sd
import numpy as np
import soundfile as sf
import os
import time
from scipy.io import wavfile

def capture_audio():
    duration = 1  # seconds
    sample_rate = 44100  # Hz
    channels = 1  # mono audio
    temp_file = "temp_recording.wav"
    
    while True:
        try:
            # Print input devices
            devices = sd.query_devices()
            print("\nAvailable Audio Devices:")
            for i, device in enumerate(devices):
                print(f"Device {i}: {device['name']} (inputs: {device['max_input_channels']})")
            
            # Record audio
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=channels,
                             dtype=np.float32,
                             blocking=True)
            sd.wait()
            
            # Print audio statistics
            print("\nAudio Statistics:")
            print(f"Number of non-zero values: {np.count_nonzero(recording)}")
            print(f"Mean value: {np.mean(recording)}")
            print(f"Max value: {np.max(recording)}")
            print(f"Min value: {np.min(recording)}")
            
            # Only proceed if we have meaningful audio
            if np.count_nonzero(recording) < 100:  # Adjust threshold as needed
                print("Not enough audio data detected, skipping...")
                continue
                
            # Normalize and save
            recording = recording / np.max(np.abs(recording))
            sf.write(temp_file, recording, sample_rate, subtype='FLOAT')
            
            # Optional: Print first few non-zero values and their positions
            nonzero_indices = np.nonzero(recording)[0][:10]
            print("\nFirst few non-zero values and their positions:")
            for idx in nonzero_indices:
                print(f"Position {idx}: {recording[idx]}")
            
            # Play back the recording (optional)
            print("\nPlaying back recording...")
            data, fs = sf.read(temp_file)
            sd.play(data, fs)
            sd.wait()
            
            os.remove(temp_file)
            
        except Exception as e:
            print(f"Error in audio capture: {str(e)}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            time.sleep(1)
        
        # Ask if user wants to continue
        user_input = input("\nPress Enter to record again or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

def main():
    print("Audio Capture and Analysis Tool")
    print("-------------------------------")
    print("This program will:")
    print("1. Show available audio devices")
    print("2. Record 1 second of audio")
    print("3. Display audio statistics")
    print("4. Play back the recording")
    print("5. Save and clean up temporary files")
    print("-------------------------------")
    
    try:
        capture_audio()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        print("Cleaning up...")
        if os.path.exists("temp_recording.wav"):
            os.remove("temp_recording.wav")
        print("Done!")

if __name__ == "__main__":
    main()