import sounddevice as sd
import numpy as np
from scipy.fftpack import fft
import time

# Standard guitar tuning frequencies (in Hz)
GUITAR_NOTES = {
    'E2': 82.41,    # Low E (6th string)
    'A2': 110.00,   # A (5th string)
    'D3': 146.83,   # D (4th string)
    'G3': 196.00,   # G (3rd string)
    'B3': 246.94,   # B (2nd string)
    'E4': 329.63    # High E (1st string)
}

# Added amplitude threshold
AMPLITUDE_THRESHOLD = 0.5  # Adjust this value between 0.0 and 1.0 to change sensitivity

def detect_frequency(audio_data, sample_rate):
    """Detect the fundamental frequency from audio data."""
    # Check if the audio level is above the threshold
    if np.max(np.abs(audio_data)) < AMPLITUDE_THRESHOLD:
        return 0
    
    # Apply Hanning window to reduce noise
    window = np.hanning(len(audio_data))
    audio_data = audio_data * window
    
    # Apply FFT
    fft_data = fft(audio_data)
    freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)
    
    # Get magnitude of FFT
    magnitude = np.abs(fft_data)
    
    # Only look at positive frequencies in the expected range for guitar (60Hz to 1000Hz)
    positive_mask = (freqs > 60) & (freqs < 1000)
    magnitude = magnitude[positive_mask]
    freqs = freqs[positive_mask]
    
    # Find peak frequency
    peak_freq = freqs[np.argmax(magnitude)]
    
    # If the magnitude is too low, return 0
    if np.max(magnitude) < 100:  # Adjust this threshold as needed
        return 0
    
    return abs(peak_freq)

def find_closest_note(frequency):
    """Find the closest guitar note to the detected frequency."""
    closest_note = min(GUITAR_NOTES.items(), 
                      key=lambda x: abs(x[1] - frequency))
    return closest_note

def tune_guitar():
    # Audio parameters
    SAMPLE_RATE = 44100
    DURATION = 3  # seconds
    
    print("Guitar Tuner")
    print("============")
    print("Standard tuning: E A D G B E")
    print("Press Ctrl+C to exit")
    print(f"Current amplitude threshold: {AMPLITUDE_THRESHOLD}")
    
    try:
        while True:
            print("\nPluck a string (or wait for silence)...")
            
            # Record audio
            audio_data = sd.rec(int(SAMPLE_RATE * DURATION), 
                              samplerate=SAMPLE_RATE,
                              channels=1)
            sd.wait()
            
            # Get maximum amplitude
            max_amplitude = np.max(np.abs(audio_data))
            
            # Only process if above threshold
            if max_amplitude > AMPLITUDE_THRESHOLD:
                # Detect frequency
                frequency = detect_frequency(audio_data[:, 0], SAMPLE_RATE)
                
                if frequency > 0:
                    # Find closest note
                    note, expected_freq = find_closest_note(frequency)
                    
                    # Calculate how far off the frequency is
                    cents = 1200 * np.log2(frequency / expected_freq)
                    
                    print(f"Signal strength: {max_amplitude:.3f}")
                    print(f"Detected frequency: {frequency:.1f} Hz")
                    print(f"Closest note: {note} ({expected_freq:.1f} Hz)")
                    
                    # Provide tuning guidance
                    if abs(cents) < 5:
                        print("✓ In tune!")
                    else:
                        if cents > 0:
                            print("↓ Too high - tune down")
                        else:
                            print("↑ Too low - tune up")
            else:
                print("Signal too weak, try plucking harder")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    # Install required packages if not already installed
    # pip install sounddevice numpy scipy
    
    tune_guitar()