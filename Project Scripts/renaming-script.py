import os
from pathlib import Path

def rename_images(folder_path, start_number):
    # Common image file extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    
    try:
        # Convert folder path to Path object
        folder = Path(folder_path)
        
        # Verify the folder exists
        if not folder.is_dir():
            raise NotADirectoryError("The specified path is not a valid directory")
        
        # Get all files in the directory that are images
        image_files = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
        
        # Counter for renaming
        counter = start_number
        
        # Rename each image
        for image in image_files:
            # Get the file extension
            extension = image.suffix
            
            # Create new filename
            new_name = folder / f"image_{counter}{extension}"
            
            # If the new filename already exists, increment counter until we find a free name
            while new_name.exists():
                counter += 1
                new_name = folder / f"image_{counter}{extension}"
            
            # Rename the file
            image.rename(new_name)
            print(f"Renamed {image.name} to {new_name.name}")
            
            counter += 1
            
        print(f"\nSuccessfully renamed {len(image_files)} images")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Get folder path from user
    folder_path = "E:\\Repos\\Python_Scripts\\emergency_vehicle_images\\images\\traffic"

    start_number = 235
    
    # Run the renaming function
    rename_images(folder_path, start_number)