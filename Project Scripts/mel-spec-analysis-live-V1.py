import time
import librosa
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
import threading
import sounddevice as sd


#function
# takes in no data
# variables: audio_files - the output array where data is stored
#            VAR_path    - the location of the .wav data used to access the data within
# outputs: an array with .wav data inside
#          the labels used for data classification
# to add more data make new _path folder with data and then loop through to access
def load_audio_data():
  #data array
  audio_files = []
  #label array
  labels = []
  #paths to each of the .wav repos (changed this to work with any path as long as the emergency vehicle sounds are one folder up from code)
  current_dir = os.getcwd()
  parent_dir = os.path.dirname(current_dir)
  
  ambulance_path = os.path.join(parent_dir, "Python_Scripts\\emergency_vehicle_sounds\\sounds\\ambulance")
  firetruck_path = os.path.join(parent_dir, "Python_Scripts\\emergency_vehicle_sounds\\sounds\\firetruck")
  traffic_path = os.path.join(parent_dir, "Python_Scripts\\emergency_vehicle_sounds\\sounds\\traffic")
  
  #goes through path for each of the sound types and reads the data
  #emergency vehicle labels
  print("Reading files : ambulance")
  for file in read_wav_files(ambulance_path):
    audio_files.append(file)
    labels.append("Emergency Vehicle")
  print("Reading files : firetruck")
  for file in read_wav_files(firetruck_path):
    audio_files.append(file)
    labels.append("Emergency Vehicle")

  #regular traffic labels
  print("Reading files : traffic")
  for file in read_wav_files(traffic_path):
    audio_files.append(file)
    labels.append("Regular Traffic")

  return audio_files, labels

#Function
# takes in the path of the folder to read
# variables: temp_audio_files - a temporary array to store the data before returning
# outputs: an array full of .wav data
# shouldn't need changing more now it is finished
def read_wav_files(path):
    temp_audio_files = []
    #go through each file in specific sound file
    for filename in os.listdir(path):
       #check if file type is .wav
       if filename[-4:] == ".wav":
          #read data
          data = extract_mel_features(path + "\\" + filename, None)
          #save to audio_files
          temp_audio_files.append(data)
    return(temp_audio_files)

#Function
# takes in audio_input to be processed
# Variables: target_length - the target length, will poll the live input feed at this rate (1hz currently)
# outputs: a single "mel_db" - the extracted data from the file provided
def extract_mel_features(audio_input, sample_rate = None):
  #target length of the audio clip
  target_length = 1000

  # Handle both file paths and raw audio
  if isinstance(audio_input, str):  # If it's a file path
      sound_data, sample_rate = librosa.load(audio_input)
  else:  # If it's raw audio data
      sound_data = audio_input
        
  mel_spec = librosa.feature.melspectrogram(y=sound_data, sr=sample_rate, n_mels=128, fmax=8000)
  mel_db = librosa.power_to_db(mel_spec, ref=np.max)

  current_length = mel_spec.shape[1]
  #if the length is too long reduce it to the ideal length
  if current_length > target_length:
    return mel_spec[:, :target_length]
  #if it is too short pad it out with zeros so that it can still be used
  elif current_length < target_length:
    padding = np.zeros((mel_spec.shape[0], target_length - current_length))
    return np.hstack((mel_spec, padding))

  return mel_db

#Function
# takes in raw audio and sample rate
# outputs the predicted class
def process_audio(raw_audio_data, sample_rate):

  # Normalizing volume
  raw_audio_data = raw_audio_data / np.max(np.abs(raw_audio_data))

  # Extract Mel-spectrogram features
  mel_features = extract_mel_features(raw_audio_data, sample_rate)

  # Flatten the features for the classifier
  mel_features_flattened = mel_features.flatten()
  
  # Make array 2D
  mel_features_flattened = mel_features_flattened.reshape(1, -1)

  # Predict the vehicle type
  predicted_class = model.predict(mel_features_flattened)
  
  # Prediction confidence
  prediction_proba = model.predict_proba(mel_features_flattened)
  confidence = np.max(prediction_proba) * 100
  print(f"Confidence: {confidence:.2f}%")
  
  return predicted_class

def capture_audio():
  duration = 1  # seconds
  sample_rate = 44100  # Hz
  channels = 1  # mono audio
  
  while True:
    try:
      recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
      recording = recording.flatten()
      
      sd.wait()
      
      print(f"Predicted vehicle type is : {process_audio(recording, sample_rate)}")
    
    except Exception as e:
      print(f"Error in audio capture: {str(e)}")
  
  
# Main execution flow
if __name__ == "__main__":
  #loading in the audio files
  print("Reading audio files")
  audio_files, labels = load_audio_data()
  
  #splitting up the testing and training set so that I can verify model
  print("Setting up train/test split")
  X_train, X_test, y_train, y_test = train_test_split(audio_files, labels, test_size=0.2, random_state=42)
  
  #converting from array to a numpy array so i can change the format of the test array
  X_train = np.array(X_train)
  X_test = np.array(X_test)

  #"flattening" the array so that the model can use it from a 3D array to a 2D one
  X_train = X_train.reshape(X_train.shape[0], -1)  
  X_test = X_test.reshape(X_test.shape[0], -1)     

  #training the classifier
  print("Training model")
  model = RandomForestClassifier()
  model.fit(X_train, y_train)

  #get the prediction of the model
  print("Calculate accuracy")
  y_pred = model.predict(X_test)

  #calculate the accuracy of the model and display as a %
  accuracy = accuracy_score(y_test, y_pred)
  print("")
  print(f"Accuracy: {accuracy * 100:.2f}%")

  audio_thread = threading.Thread(target=capture_audio)
  audio_thread.daemon = True
  audio_thread.start()
  
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print("Keyboard input detected, halting...")
  
  
