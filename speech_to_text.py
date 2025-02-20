import speech_recognition as sr

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to convert audio to text
def audio_to_text(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)  # Record the audio file

        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

# Example usage
if __name__ == "__main__":
    audio_file = "recording4.wav"  # Replace with your audio file path
    text = audio_to_text(audio_file)
    if text:
        print(f"Transcription: {text}")
