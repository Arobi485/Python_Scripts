import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from joblib import dump
import os

from extract_mel_features import extract_mel

class trainMelSpec:
    def __init__(self):
        pass

    #function
    # takes in no data
    # variables: audio_files - the output array where data is stored
    #            VAR_path    - the location of the .wav data used to access the data within
    # outputs: an array with .wav data inside
    #          the labels used for data classification
    # to add more data make new _path folder with data and then loop through to access
    def load_audio_data(self):
        #data array
        audio_files = []
        #label array
        labels = []
        #paths to each of the .wav repos (changed this to work with any path as long as the emergency vehicle sounds are one folder up from code)
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        
        ambulance_path = "emergency_vehicle_sounds\\sounds\\ambulance"
        firetruck_path = "emergency_vehicle_sounds\\sounds\\firetruck"
        traffic_path = "emergency_vehicle_sounds\\sounds\\traffic"

        #goes through path for each of the sound types and reads the data
        #emergency vehicle labels
        print("Reading files : ambulance")
        for file in self.read_wav_files(ambulance_path):
            audio_files.append(file)
            labels.append("Emergency Vehicle")

        print("Reading files : firetruck")
        for file in self.read_wav_files(firetruck_path):
            audio_files.append(file)
            labels.append("Emergency Vehicle")

        #regular traffic labels
        print("Reading files : traffic")
        for file in self.read_wav_files(traffic_path):
            audio_files.append(file)
            labels.append("Regular Traffic")

        return audio_files, labels

    #Function
    # takes in the path of the folder to read
    # variables: temp_audio_files - a temporary array to store the data before returning
    # outputs: an array full of .wav data
    # shouldn't need changing more now it is finished
    def read_wav_files(self,path):

        temp_audio_files = []

        #go through each file in specific sound file
        for filename in os.listdir(path):
            #check if file type is .wav
            if filename[-4:] == ".wav":
                #read data
                extractor = extract_mel()
                data = extractor.extract_mel_features(path + "\\" + filename)
                #save to audio_files
                temp_audio_files.append(data)
        return(temp_audio_files)

    #temp function for test purposes
    def process_audio(self, audio_file):

        # Extract Mel-spectrogram features
        mel_features = self.extract_mel_features(audio_file)

        # Flatten the features for the classifier
        mel_features_flattened = mel_features.flatten()

        # Predict the vehicle type
        predicted_class = self.model.predict([mel_features_flattened])
        return predicted_class  

    def train_model(self):
        #loading in the audio files
        print("Reading audio files")
        audio_files, labels = self.load_audio_data()
        
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

        #output model
        filename = "mel_spec_model.joblib"
        dump(model, filename)