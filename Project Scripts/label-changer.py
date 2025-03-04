import os

def fix_first_characters(folder_path):
    try:
        # Get all text files in the folder
        files = os.listdir(folder_path)
        txt_files = [f for f in files if f.endswith('.txt')]
        
        for file_name in txt_files:
            file_path = os.path.join(folder_path, file_name)
            modified = False
            
            # Read the file
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Check each line
            for i in range(len(lines)):
                if lines[i] and lines[i][0] != "0":
                    # Keep the rest of the line, just change first character
                    lines[i] = "0" + lines[i][1:]
                    modified = True
            
            # Write back only if changes were made
            if modified:
                with open(file_path, 'w') as file:
                    file.writelines(lines)
                print(f"Updated lines in {file_name}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Specify your folder path here
folder_path = "E:\Repos\Python_Scripts\emergency_vehicle_images\images\\police"
fix_first_characters(folder_path)