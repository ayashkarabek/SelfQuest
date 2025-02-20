# this is the working button with changed images and correct dimentions
import pyaudio
import wave
import os
import threading
import pygame
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

    print("Recording...")

def stop_recording():
    global recording_thread, stream

    if recording_thread:
        recording_thread.do_run = False  # Signal the recording thread to stop
        recording_thread.join()          # Wait for the thread to finish

    if stream and stream.is_active():
        stream.stop_stream()
        stream.close()

    # Get the next available filename
    output_filename = get_next_filename()

    # Save the recorded audio to a WAV file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(stream._channels)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")

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

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Audio Recorder and Speech-to-Text Converter")

# Load and resize images
record_img = pygame.image.load("record.png")
stop_img = pygame.image.load("stop.png")

record_img = pygame.transform.scale(record_img, (64, 64))
stop_img = pygame.transform.scale(stop_img, (64, 64))

# Button states
recording = False
button_rect = record_img.get_rect(center=(750, 350))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                if not recording:
                    start_recording()
                    recording = True
                else:
                    stop_recording()
                    recording = False

    # Clear screen
    screen.fill((255, 255, 255))

    # Draw button
    if recording:
        screen.blit(stop_img, button_rect)
    else:
        screen.blit(record_img, button_rect)

    pygame.display.flip()

pygame.quit()

# Close the audio stream
if stream and stream.is_active():
    stream.stop_stream()
    stream.close()
audio.terminate()
