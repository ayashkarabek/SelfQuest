import pyaudio
import wave
import os
import threading
import tkinter as tk
from tkinter import messagebox
import openai

# Parameters for recording
FORMAT = pyaudio.paInt16  # Format of sampling 16 bits per sample
RATE = 44100              # Sampling rate (samples per second)
CHUNK = 1024              # Number of frames per buffer

# Global variables
audio = pyaudio.PyAudio()
stream = None
recording_thread = None
frames = []

# Set your OpenAI API key
openai.api_key = "sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp"

# Function to get the next filename in the sequence
def get_next_filename(prefix="recording", extension=".wav"):
    i = 1
    while os.path.exists(f"{prefix}{i}{extension}"):
        i += 1
    return f"{prefix}{i}{extension}"

# Function to record audio
def record_audio(stream, frames):
    while getattr(recording_thread, "do_run", True):
        data = stream.read(CHUNK)
        frames.append(data)

def start_recording():
    global recording_thread, stream, frames

    frames = []

    # Try to open stream with 2 channels (stereo)
    try:
        stream = audio.open(format=FORMAT,
                            channels=2,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    except OSError as e:
        # If stereo is not supported, fallback to mono
        print(f"Stereo not supported: {e}, falling back to mono.")
        stream = audio.open(format=FORMAT,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

    # Start recording in a separate thread
    recording_thread = threading.Thread(target=record_audio, args=(stream, frames))
    recording_thread.do_run = True
    recording_thread.start()

    # Change button image to stop.png
    start_button.config(image=stop_img, command=stop_recording)

    print("Recording...")

def stop_recording():
    global recording_thread, stream

    if recording_thread:
        recording_thread.do_run = False  # Signal the recording thread to stop
        recording_thread.join()          # Wait for the thread to finish

    if stream and stream.is_active():
        stream.stop_stream()
        stream.close()

    # Change button image back to record.png
    start_button.config(image=record_img, command=start_recording)

    # Get the next available filename
    output_filename = get_next_filename()

    # Save the recorded audio to a WAV file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(stream._channels)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")
    messagebox.showinfo("Recording", f"Recording saved to {output_filename}")

    # Convert audio to text
    text = audio_to_text(output_filename)
    if text:
        print(f"Transcription: {text}")

# Function to convert audio to text using Whisper API
def audio_to_text(audio_file):
    with open(audio_file, "rb") as audio:
        response = openai.Audio.transcribe("whisper-1", audio)
        text = response["text"]
        return text

# Create the GUI
root = tk.Tk()
root.title("Audio Recorder and Speech-to-Text Converter")

# Load images
record_img = tk.PhotoImage(file="record.png")
stop_img = tk.PhotoImage(file="stop.png")

# Create buttons with images
start_button = tk.Button(root, image=record_img, command=start_recording)
start_button.pack(pady=10)

root.mainloop()
