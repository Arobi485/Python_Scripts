from ultralytics import YOLO
import cv2
import os

class emergencyVehicleYoloV5:
    def __init__(self):
        if not os.path.exists("emergency_detection_scripts\\emergency_vehicles_trained_model\\weights\\best.pt"):
            print("Error locating weights file for YOLOv5 model, recommended to run training")
            return

    def run_detection(self, image_location):
        #confidence threshhold so that it doesnt flag everything it sees
        confidence_threshhold = 0.7

        # loading in the trained weights from local location
        weights_path = "emergency_detection_scripts\\emergency_vehicles_trained_model\\weights\\best.pt"
        
        # only classs is emergency vehicle
        class_names = ['emergency vehicle']
        
        # loading in the YOLO v5 model with my trained weights to locate emergency vehicles
        try:
            model = YOLO(weights_path)
            #print("Loaded custom weights successfully")
            #print(f"Model classes: {model.names}")
        except Exception as e:
            print(f"Error loading weights: {e}")
            return      
        
        # Read image
        image = cv2.imread(image_location)
        if image is None:
            print("Error: Could not read image.")
            return
        
        # Run detection
        results = model.predict(image, confidence_threshhold, verbose = False)  # Adjust confidence threshold as needed
        
        # result output
        output_confidences = []

        # process results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # get confidence
                output_confidences.append(float(box.conf[0]))
        
        # Save output
        return (output_confidences)