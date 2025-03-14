#external imports
from joblib import load
import os

#internal imports
from extract_mel_features import extract_mel
from training_mel_spec import Train_Mel_Spec

#2 seperate models that combine their outputs at the end

class Mel_Spec_Analysis:
  def __init__(self):
    if not os.path.exists("mel_spec_model.joblib"):
          tms = Train_Mel_Spec()

          print("Error locating model file for mel-spec analysis, generating now")
          tms.train_model()
    
    self.model = load("mel_spec_model.joblib")

  def check_file(self, audio_location):
    # Extract Mel-spectrogram features
    mel_features = extract_mel.extract_mel_features(extract_mel, audio_location)

    # Flatten the features for the classifier
    mel_features_flattened = mel_features.flatten()

    # Predict the vehicle type
    predicted_class = self.model.predict([mel_features_flattened])

    print(f"Predicted vehicle type for {os.path.basename(audio_location)}: {predicted_class}")

