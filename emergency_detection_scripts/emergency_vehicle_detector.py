#needs to,  create instances of both of the detector AI
#           combine these outputs to generate a total accuracy
#           runs these both on seperate threads as to not back up the system
#           possible run the Yolo model on images instead of a video stream?
#           get the mel-analysis to actually work on short recorded clips
#           or just handle the saving side of that here then just pass the path?
#           DO THIS /\

#external
import threading

#internal
from mel_spec_analysis_class import mel_spec_analysis
from yoloV5_detection_class import emergency_vehicle_yoloV5

class emergency_vehicle_detection_class:
    def __init__(self):
        # starting up yoloV5 model
        self.yolo = emergency_vehicle_yoloV5()

        # starting up mel-spec model, will retrain if no model found
        self.msa = mel_spec_analysis()

    def check_mel(self):
        self.msa.check_file("emergency_detection_scripts\\test_files\\sound_1.wav")
        
    def check_yolo(self):
        # confidence check for yolo
        confidence_check = 0.9

        # checking test files
        yolo_output = []

        yolo_output = self.yolo.run_detection("emergency_detection_scripts\\test_files\\test1.png")

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
    
    # start detection threads
    detection.start_detection()
    
    # wait for both detections to complete
    detection.wait_for_completion()
