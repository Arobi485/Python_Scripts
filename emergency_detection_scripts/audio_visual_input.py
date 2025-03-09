import cv2
import pyaudio
import wave
import numpy as np
import threading
import time
import os
from datetime import datetime
import noisereduce as nr
from scipy import signal

class AudioVisualRecorder:
    def __init__(self):        
        # start cv2 camera
        self.camera = cv2.VideoCapture(0)

        # start pyaudio
        self.p = pyaudio.PyAudio()
        
        self.is_recording = False

    def capture_audio(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 2
        rate = 44100

        stream = self.p.open(format=format,
                channels=channels,
                rate=rate,
                input=True,  
                frames_per_buffer=chunk,)

        while self.is_recording:
            
            frames = []

            for i in range(0, int(rate / chunk)):
                data = stream.read(chunk)
                frames.append(data)

            wf = wave.open("audio.wav", 'wb')  
            wf.setnchannels(channels)
            wf.setsampwidth(self.p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close() 

        stream.stop_stream()
        stream.close()

    def capture_images(self):
        while self.is_recording:
            ret, frame = self.camera.read()
            if ret:
                cv2.imwrite("image.png", frame)
            time.sleep(1)

    def start_recording(self):
        self.is_recording = True
        
        audio_thread = threading.Thread(target=self.capture_audio)
        audio_thread.start()
        
        image_thread = threading.Thread(target=self.capture_images)
        image_thread.start()
        
        return audio_thread, image_thread

    def stop_recording(self):
        self.is_recording = False

    def cleanup(self):
        self.camera.release()
        self.p.terminate()
