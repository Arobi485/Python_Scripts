import sounddevice as sd
import numpy as np
from scipy.fftpack import fft
import tkinter as tk
from tkinter import ttk
import threading
import time
import math

# Standard guitar tuning frequencies (in Hz)
GUITAR_NOTES = {
    'E2': 82.41,    # Low E (6th string)
    'A2': 110.00,   # A (5th string)
    'D3': 146.83,   # D (4th string)
    'G3': 196.00,   # G (3rd string)
    'B3': 246.94,   # B (2nd string)
    'E4': 329.63    # High E (1st string)
}

AMPLITUDE_THRESHOLD = 0.1

class GuitarTuner(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Guitar Tuner")
        self.geometry("600x400")
        self.configure(bg='#2c3e50')

        # Initialize variables
        self.running = True
        self.current_frequency = tk.StringVar(value="0 Hz")
        self.current_note = tk.StringVar(value="--")
        self.tuning_status = tk.StringVar(value="Waiting for input...")
        self.cents_deviation = 0

        self.setup_gui()
        
        # Start the audio processing thread
        self.audio_thread = threading.Thread(target=self.audio_processing_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Update GUI every 50ms
        self.update_gui()

    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Style configuration
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 24, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 16))
        style.configure('Status.TLabel', font=('Helvetica', 18, 'bold'))

        # Title
        title_label = ttk.Label(main_frame, text="Guitar Tuner", style='Title.TLabel')
        title_label.pack(pady=10)

        # Frequency display
        freq_frame = ttk.Frame(main_frame)
        freq_frame.pack(pady=10)
        ttk.Label(freq_frame, text="Frequency:", style='Info.TLabel').pack(side=tk.LEFT)
        ttk.Label(freq_frame, textvariable=self.current_frequency, style='Info.TLabel').pack(side=tk.LEFT, padx=10)

        # Note display
        note_frame = ttk.Frame(main_frame)
        note_frame.pack(pady=10)
        ttk.Label(note_frame, text="Note:", style='Info.TLabel').pack(side=tk.LEFT)
        ttk.Label(note_frame, textvariable=self.current_note, style='Info.TLabel').pack(side=tk.LEFT, padx=10)

        # Canvas for tuning meter
        self.canvas = tk.Canvas(main_frame, width=500, height=100, bg='white')
        self.canvas.pack(pady=20)

        # Status display
        ttk.Label(main_frame, textvariable=self.tuning_status, style='Status.TLabel').pack(pady=10)

        # String buttons
        strings_frame = ttk.Frame(main_frame)
        strings_frame.pack(pady=20)
        for note, freq in GUITAR_NOTES.items():
            btn = ttk.Button(strings_frame, text=f"{note} ({freq:.1f} Hz)")
            btn.pack(side=tk.LEFT, padx=5)

    def draw_tuning_meter(self):
        self.canvas.delete("all")
        
        # Draw the meter background
        width = 500
        height = 100
        center_x = width // 2
        center_y = height - 20

        # Draw scale lines
        for i in range(-50, 51, 10):
            x = center_x + (i * 4)
            line_height = 15 if i == 0 else (10 if i % 10 == 0 else 5)
            self.canvas.create_line(x, center_y, x, center_y - line_height, fill='black')
            if i % 10 == 0:
                self.canvas.create_text(x, center_y + 10, text=str(i))

        # Draw the needle
        needle_length = 60
        angle = math.radians(min(max(self.cents_deviation, -50), 50) * 1.5)
        end_x = center_x + needle_length * math.sin(angle)
        end_y = center_y - needle_length * math.cos(angle)
        
        # Color based on how close to in tune
        if abs(self.cents_deviation) < 5:
            color = 'green'
        elif abs(self.cents_deviation) < 15:
            color = 'orange'
        else:
            color = 'red'
            
        self.canvas.create_line(center_x, center_y, end_x, end_y, 
                              fill=color, width=3)

    def detect_frequency(self, audio_data, sample_rate):
        if np.max(np.abs(audio_data)) < AMPLITUDE_THRESHOLD:
            return 0
        
        window = np.hanning(len(audio_data))
        audio_data = audio_data * window
        
        fft_data = fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)
        
        magnitude = np.abs(fft_data)
        
        positive_mask = (freqs > 60) & (freqs < 1000)
        magnitude = magnitude[positive_mask]
        freqs = freqs[positive_mask]
        
        if len(freqs) == 0 or np.max(magnitude) < 100:
            return 0
            
        peak_freq = freqs[np.argmax(magnitude)]
        return abs(peak_freq)

    def find_closest_note(self, frequency):
        return min(GUITAR_NOTES.items(), key=lambda x: abs(x[1] - frequency))

    def audio_processing_loop(self):
        SAMPLE_RATE = 44100
        DURATION = 1

        while self.running:
            audio_data = sd.rec(int(SAMPLE_RATE * DURATION), 
                              samplerate=SAMPLE_RATE,
                              channels=1)
            sd.wait()
            
            frequency = self.detect_frequency(audio_data[:, 0], SAMPLE_RATE)
            
            if frequency > 0:
                note, expected_freq = self.find_closest_note(frequency)
                self.cents_deviation = 1200 * np.log2(frequency / expected_freq)
                
                self.current_frequency.set(f"{frequency:.1f} Hz")
                self.current_note.set(note)
                
                if abs(self.cents_deviation) < 5:
                    self.tuning_status.set("In tune! ✓")
                else:
                    if self.cents_deviation > 0:
                        self.tuning_status.set("Too high - tune down ↓")
                    else:
                        self.tuning_status.set("Too low - tune up ↑")
            else:
                self.tuning_status.set("Waiting for input...")

    def update_gui(self):
        self.draw_tuning_meter()
        self.after(50, self.update_gui)

    def on_closing(self):
        self.running = False
        time.sleep(0.2)  # Give time for the audio thread to close
        self.destroy()

if __name__ == "__main__":
    app = GuitarTuner()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()