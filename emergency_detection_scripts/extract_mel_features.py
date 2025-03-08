import librosa
import numpy as np

class extract_mel:
    #Function
    # takes in an individual audio_file to be processed
    # Variables: target_length - the target length, will poll the live input feed at this rate (1hz currently)
    # outputs: a single "mel_db" - the extracted data from the file provided
    def extract_mel_features(self, audio_file):
        #target length of the audio clip
        target_length = 1000

        sound_data, sample_rate = librosa.load(audio_file)
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