import moviepy as mp
import speech_recognition as sr
from transformers import pipeline
import os

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file"""
    try:
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path)
        video.close()
        return True
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        return False

def speech_to_text(audio_path):
    """Convert speech to text using Google Speech Recognition"""
    recognizer = sr.Recognizer()
    text = ""
    
    try:
        # Convert audio to WAV format if needed
        audio = sr.AudioFile(audio_path)
        
        with audio as source:
            audio_data = recognizer.record(source)
            
        # Using Google Speech Recognition
        text = recognizer.recognize_google(audio_data)
        return text
    
    except Exception as e:
        print(f"Error in speech recognition: {str(e)}")
        return None

def generate_summary(text):
    """Generate summary using transformers"""
    try:
        # Initialize summarization pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Split text into chunks if it's too long (BART has a max input length)
        max_chunk_length = 1024
        chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        return " ".join(summaries)
    
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return None

def analyze_video(video_path):
    """Main function to analyze video content"""
    try:
        # Create temporary audio file
        audio_path = "temp_audio.wav"
        
        # Step 1: Extract audio
        print("Extracting audio from video...")
        if not extract_audio_from_video(video_path, audio_path):
            return
        
        # Step 2: Convert speech to text
        print("Converting speech to text...")
        text = speech_to_text(audio_path)
        if not text:
            return
        
        # Step 3: Generate summary
        print("Generating summary...")
        summary = generate_summary(text)
        if not summary:
            return
        
        # Clean up temporary files
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "full_transcript": text,
            "summary": summary
        }
    
    except Exception as e:
        print(f"Error in video analysis: {str(e)}")
        return None

def main():
    # Specify the path to your video file
    video_path = "CO3404 Lecture-20250123_115935-Meeting Recording.mp4"
    
    print("Starting video analysis...")
    result = analyze_video(video_path)
    
    if result:
        print("\nVideo Analysis Results:")
        print("\nFull Transcript:")
        print(result["full_transcript"])
        print("\nSummary:")
        print(result["summary"])
    else:
        print("Video analysis failed.")

if __name__ == "__main__":
    main()