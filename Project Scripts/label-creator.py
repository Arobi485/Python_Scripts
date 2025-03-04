import os
from pathlib import Path

def create_empty_labels(folder_path):
    # Convert string path to Path object
    folder = Path(folder_path)
    
    # Verify folder exists
    if not folder.exists():
        print(f"Error: Folder {folder} does not exist!")
        return
    
    # Get all PNG files
    png_files = list(folder.glob('*.png'))
    
    # Counter for labeling
    counter = 235
    
    print(f"Found {len(png_files)} PNG files")
    
    # Create empty txt file for each PNG
    for png_file in png_files:
        # Create label filename
        label_file = folder / f"image_{counter}.txt"
        
        # Create empty file
        label_file.touch()
        
        print(f"Created {label_file.name} for {png_file.name}")
        counter += 1
    
    print(f"\nCreated {counter-1} empty label files")

# Get folder path from user
folder_path = "E:\\Repos\\Python_Scripts\\emergency_vehicle_images\\images\\traffic"

# Create the labels
create_empty_labels(folder_path)