from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

def run_detection():
    # Load your trained weights
    weights_path = input("Enter path to your .pt weights file: ")
    
    # Custom class names - update these to match your classes
    class_names = ['ambulance', 'firetruck', 'police', 'traffic']
    
    # Load the model with your custom weights
    try:
        model = YOLO(weights_path)
        print("Loaded custom weights successfully")
        print(f"Model classes: {model.names}")
    except Exception as e:
        print(f"Error loading weights: {e}")
        return
    
    # Ask for input type
    input_type = input("Do you want to process a video (v) or image (i)? ").lower()
    
    if input_type == 'v':
        # Process video
        video_path = input("Enter path to video file: ")
        output_path = input("Enter path for output video (e.g., output.mp4): ")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video.")
            return
            
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Create video writer
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        
        frame_count = 0
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
                
            # Run detection
            results = model.predict(frame, conf=0.25)  # Adjust confidence threshold as needed
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Get class and confidence
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Add label
                    label = f'{class_names[cls]} {conf:.2f}'
                    cv2.putText(frame, label, (x1, y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Write frame
            out.write(frame)
            
            # Display progress
            frame_count += 1
            if frame_count % 30 == 0:  # Show progress every 30 frames
                print(f"Processed {frame_count} frames")
            
            # Display frame
            cv2.imshow('Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Video processing complete. Output saved to: {output_path}")
        
    elif input_type == 'i':
        # Process image
        image_path = input("Enter path to image file: ")
        output_path = input("Enter path for output image: ")
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print("Error: Could not read image.")
            return
        
        # Run detection
        results = model.predict(image, conf=0.25)  # Adjust confidence threshold as needed
        
        # Process results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get class and confidence
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                # Draw box
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add label
                label = f'{class_names[cls]} {conf:.2f}'
                cv2.putText(image, label, (x1, y1-10), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save output
        cv2.imwrite(output_path, image)
        print(f"Image processing complete. Output saved to: {output_path}")
        
        # Display image
        cv2.imshow('Detection', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    else:
        print("Invalid input type selected")

if __name__ == "__main__":
    print("Emergency Vehicle Detection using Custom Weights")
    print("==============================================")
    run_detection()