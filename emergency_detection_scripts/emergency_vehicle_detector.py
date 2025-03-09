#needs to,  create instances of both of the detector AI
#           combine these outputs to generate a total accuracy
#           runs these both on seperate threads as to not back up the system
#           possible run the Yolo model on images instead of a video stream?
#           get the mel-analysis to actually work on short recorded clips
#           or just handle the saving side of that here then just pass the path?
#           DO THIS /\

#external
import threading
import time

#internal
from mel_spec_analysis_class import melSpecAnalysis
from yoloV5_detection_class import emergencyVehicleYoloV5
from audio_visual_input import AudioVisualRecorder

class emergency_vehicle_detection_class:
    def __init__(self):
        # starting up yoloV5 model
        self.yolo = emergencyVehicleYoloV5()

        # starting up mel-spec model, will retrain if no model found
        self.msa = melSpecAnalysis()

    def check_mel(self):
        self.msa.check_file("audio.wav")
        
    def check_yolo(self):
        # confidence check for yolo
        confidence_check = 0.9

        # checking test files
        yolo_output = []

        yolo_output = self.yolo.run_detection("image.png")

        if yolo_output != []:
            for value in yolo_output:
                if value >= confidence_check:
                    print(f"Emergency vehicle detected with confidence : {value}")
        else:
            print("no vehicle detected")

    def start_detection(self):
        # Create threads
        self.yolo_thread = threading.Thread(target=self.check_yolo)
        self.mel_thread = threading.Thread(target=self.check_mel)

        # Start both threads
        self.yolo_thread.start()
        self.mel_thread.start()

    def wait_for_completion(self):
        # Wait for both threads to complete
        if self.yolo_thread:
            self.yolo_thread.join()
        if self.mel_thread:
            self.mel_thread.join()

if __name__ == "__main__":
    detection = emergency_vehicle_detection_class()

    recorder = AudioVisualRecorder()
    
    print("Starting recording... Press Ctrl+C to stop")
    audio_thread, image_thread = recorder.start_recording()
    
    try:
        while True:
            time.sleep(0.25)
            # start detection threads
            detection.start_detection()
            detection.wait_for_completion()
    except KeyboardInterrupt:
        print("\nStopping recording...")
        recorder.stop_recording()
        audio_thread.join()
        image_thread.join()
        recorder.cleanup()
        print("Recording stopped")
