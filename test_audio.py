import pygame
import pyaudio
import wave
import speech_recognition as sr
from gtts import gTTS
import os
import requests
import threading

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 400, 400
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Audio Recorder')

# Load the images
record_img = pygame.image.load('record.png')
stop_img = pygame.image.load('stop.png')

# Set up the button
button_rect = pygame.Rect(WIDTH / 2 - 50, HEIGHT / 2 - 25, 100, 50)
button_color = RED
button_image = record_img

# Set up the audio recorder
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav" #file save first in local device, 

# Set up the speech recognition
r = sr.Recognizer()

# Set up the ChatGPT API
chatgpt_api_key = "sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp"

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def get_response():
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand your audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    response = requests.post(
        f"https://api.chatgpt.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {chatgpt_api_key}"},
        json={"prompt": text}
    ).json()
    if 'choices' in response:
        return response["choices"][0]["text"]
    else:
        return "No response from ChatGPT"

# Game loop
recording = False
response = ""
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                if not recording:
                    # Start recording
                    recording = True
                    button_color = WHITE
                    button_image = stop_img
                    threading.Thread(target=record_audio).start()
                else:
                    # Stop recording
                    recording = False
                    button_color = RED
                    button_image = record_img
                    response = get_response()
                    tts = gTTS(text=response, lang='en')
                    tts.save("response.mp3")
                    os.system("mp3gains -r response.mp3")

    # Draw the button
    screen.fill(WHITE)
    pygame.draw.rect(screen, button_color, button_rect)
    screen.blit(button_image, (WIDTH / 2 - 25, HEIGHT / 2 - 25))
    font = pygame.font.Font(None, 36)
    text = font.render(response, True, (0, 0, 0))
    screen.blit(text, (10, 10))
    pygame.display.update()