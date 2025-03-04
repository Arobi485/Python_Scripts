import os
import subprocess
import sys
from pathlib import Path
import yaml

def verify_dataset(dataset_path):
    """Verify dataset structure and content"""
    dataset_path = Path(dataset_path)
    
    # Check directory structure
    required_dirs = [
        dataset_path / 'images' / 'train',
        dataset_path / 'images' / 'val',
        dataset_path / 'labels' / 'train',
        dataset_path / 'labels' / 'val'
    ]
    
    print("\nVerifying dataset structure...")
    for dir_path in required_dirs:
        if dir_path.exists():
            num_files = len(list(dir_path.glob('*')))
            print(f"✓ {dir_path} exists with {num_files} files")
        else:
            print(f"✗ Missing directory: {dir_path}")
            return False
    
    # Verify data.yaml
    yaml_path = dataset_path / 'data.yaml'
    if not yaml_path.exists():
        print(f"✗ Missing data.yaml file")
        return False
    
    # Read and verify data.yaml content
    with open(yaml_path) as f:
        try:
            data = yaml.safe_load(f)
            print("\ndata.yaml contents:")
            print(f"Train path: {data.get('train', 'Not specified')}")
            print(f"Val path: {data.get('val', 'Not specified')}")
            print(f"Number of classes: {data.get('nc', 'Not specified')}")
            print(f"Class names: {data.get('names', 'Not specified')}")
        except yaml.YAMLError as e:
            print(f"✗ Error reading data.yaml: {e}")
            return False
    
    return True

def install_requirements():
    print("\nInstalling required packages...")
    packages = [
        'ultralytics',
        'torch',
        'torchvision',
        'opencv-python',
        'pyyaml'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ Installed {package}")
        except Exception as e:
            print(f"✗ Error installing {package}: {e}")
            return False
    return True

def train_model(dataset_path, project_dir):
    print("\nStarting model training...")
    
    try:
        from ultralytics import YOLO
        
        # Create project directory
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        print("Initializing YOLO model...")
        model = YOLO('yolov5s.pt')
        
        # Print model information
        print(f"\nInitial model classes: {model.names}")
        
        # Load data.yaml
        with open(Path(dataset_path) / 'data.yaml') as f:
            data = yaml.safe_load(f)
        
        print(f"\nTraining with {len(data['names'])} custom classes: {data['names']}")
        
        # Train model with verbose output
        print("\nStarting training...")
        results = model.train(
            data=str(Path(dataset_path) / 'data.yaml'),
            epochs=200,
            imgsz=800,
            batch=16,
            project=str(project_dir),
            name='emergency_vehicles',
            exist_ok=True,
            verbose=True  # Add verbose output
        )
        
        print("\nTraining completed!")
        
        # Verify weights file was created
        weights_path = project_dir / 'emergency_vehicles' / 'weights' / 'best.pt'
        if weights_path.exists():
            print(f"✓ Weights file created at: {weights_path}")
            
            # Verify the trained model
            trained_model = YOLO(str(weights_path))
            print(f"\nTrained model classes: {trained_model.names}")
        else:
            print("✗ Weights file not found!")
        
    except Exception as e:
        print(f"✗ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    print("Emergency Vehicle Detection - Model Training Script")
    print("================================================")
    
    # Get dataset path
    while True:
        dataset_path = input("\nEnter the path to your YOLO dataset (containing data.yaml): ").strip()
        if verify_dataset(dataset_path):
            break
        print("\nPlease fix dataset issues and try again.")
    
    # Set project directory
    project_dir = Path('emergency_vehicle_detection')
    print(f"\nProject will be saved in: {project_dir.absolute()}")
    
    # Confirm with user
    print("\nTraining Configuration:")
    print("- Epochs: 100")
    print("- Batch size: 24")
    print("- Image size: 800")
    print("- Model: YOLOv5s")
    print(f"- Output directory: {project_dir.absolute()}")
    
    proceed = input("\nProceed with training? (y/n): ").lower()
    if proceed != 'y':
        print("Training cancelled.")
        return
    
    # Train model
    if train_model(dataset_path, project_dir):
        print("\n✓ Training completed successfully!")
        print(f"Check weights at: {project_dir / 'emergency_vehicles' / 'weights' / 'best.pt'}")
    else:
        print("\n✗ Training failed!")

if __name__ == "__main__":
    main()