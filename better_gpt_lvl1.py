import pyaudio
from gtts import gTTS
import wave
import os
import threading
import pygame
import openai
import json


# Initialize Pygame
pygame.init()

one_time = True

# Screen settings
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Audio Recorder and Value Identification")

# Fonts
font = pygame.font.Font(None, 32)

# Input box settings
input_box = pygame.Rect(100, 150, 600, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

active = False
text = ''
question = "Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?"
values_identified = ''
ai_message_count = 0
follow_up_count = 0

# OpenAI API key
openai.api_key = 'sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp'

# Parameters for recording
FORMAT = pyaudio.paInt16
RATE = 44100
CHUNK = 1024

# Global variables
audio = pyaudio.PyAudio()
stream = None
recording_thread = None
frames = []

def save_conversation(conversation, filename="conversation_history.json"):
    with open(filename, "w") as file:
        json.dump(conversation, file)

def load_conversation(filename="conversation_history.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return []

conversation_history = load_conversation()

def get_next_filename(prefix="recording", extension=".wav"):
    """Get the next available filename in the sequence."""
    i = 1
    while os.path.exists(f"{prefix}{i}{extension}"):
        i += 1
    return f"{prefix}{i}{extension}"

def record_audio(stream, frames):
    """Record audio in chunks and save to frames."""
    while getattr(recording_thread, "do_run", True):
        data = stream.read(CHUNK)
        frames.append(data)

def start_recording():
    """Start audio recording in a separate thread."""
    global recording_thread, stream, frames

    frames = []

    try:
        stream = audio.open(format=FORMAT,
                            channels=2,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
    except OSError as e:
        print(f"Stereo not supported: {e}, falling back to mono.")
        stream = audio.open(format=FORMAT,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

    recording_thread = threading.Thread(target=record_audio, args=(stream, frames))
    recording_thread.do_run = True
    recording_thread.start()

    print("Recording...")

def stop_recording():
    """Stop audio recording and save to file."""
    global recording_thread, stream, text

    if recording_thread:
        recording_thread.do_run = False
        recording_thread.join()

    if stream and stream.is_active():
        stream.stop_stream()
        stream.close()

    output_filename = get_next_filename()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(stream._channels)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved to {output_filename}")

    text = audio_to_text(output_filename)
    if text:
        print(f"Transcription: {text}")
        handle_ai_response(text)

def audio_to_text(audio_file):
    """Convert audio to text using Whisper API."""
    with open(audio_file, "rb") as audio:
        response = openai.Audio.transcribe("whisper-1", audio)
        text = response["text"]
        return text

def handle_ai_response(user_response):
    global question, ai_message_count, values_identified, follow_up_count  # Declare global variables

    if ai_message_count >= 3 + follow_up_count:
        return

    messages = [
        {"role": "system", "content": "You are a conversational agent to help user(high school student) for self reflection and self determination, understanding the inner feelings of the user, values they prioritize when they make decisions."},
        {"role": "assistant", "content": "The conversation should flow naturally. Start with the following question in the first message: 'Imagine you have unlimited resources for one cause or initiative. What would you choose to do, and why?' Remember, the user should answer to the question 'Imagine you have unlimited resources for one cause or initiative. What would you choose to do, and why?', the follow-up questions, all should help to answer to this question. After the first user response, say, 'I understand.' Comment on their answer, analyze it, and determine if the given information is sufficient to identify their top 3 values. If more information is needed, ask only one follow-up, open-ended question message. If the information is sufficient, thank the user and mention their top 3 values in a maximum of 15 words. The conversation should stop after 4 messages from chatgpt side, and the 4th one being thank you and top 3 value mentioning."},
    ]

    if ai_message_count == 0:
        messages.append({"role": "user", "content": user_response})
    elif ai_message_count > 0:
        messages.append({"role": "assistant", "content": "I understand. Could you provide more details or another example?"})
        messages.append({"role": "user", "content": user_response})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )

    ai_message = response.choices[0].message['content'].strip()
    print(ai_message)  # Print to terminal
    play_text_to_speech(ai_message)

    ai_message_count += 1

    # Save conversation
    conversation_history.append({"user": user_response, "assistant": ai_message})
    save_conversation(conversation_history)

    if ai_message_count >=  + follow_up_count:
        values_identified = ai_message  # Assuming the last response mentions top 3 values
        print("Conversation ended.")
    elif "I don't know" in user_response or "I'm not sure" in user_response:
        follow_up_count += 1
        print("Asking a follow-up question due to unclear response.")

def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
    """Draw text on the screen."""
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2
    font_height = font.size("Tg")[1]

    while text:
        i = 1
        if y + font_height > rect.bottom:
            break

        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing
        text = text[i:]

    return text

def play_text_to_speech(text_to_speak, language='en'):
    """Convert text to speech and play it."""
    speech = gTTS(text=text_to_speak, lang=language, slow=False)
    speech.save("output.mp3")
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

# Load and resize images
record_img = pygame.image.load("record.png")
stop_img = pygame.image.load("stop.png")

record_img = pygame.transform.scale(record_img, (64, 64))
stop_img = pygame.transform.scale(stop_img, (64, 64))

# Button states
recording = False
button_rect = record_img.get_rect(center=(750, 350))

def main():
    global active, color, text, one_time, running, recording

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
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        if one_time:
            play_text_to_speech(question)
            one_time = False    

        screen.fill((30, 30, 30))
        draw_text(screen, question, pygame.Color('white'), pygame.Rect(100, 50, 600, 80), font)
        draw_text(screen, text, color, pygame.Rect(100, 150, 600, 300), font)
        width = max(600, font.size(text)[0] + 10)
        input_box.w = width
        pygame.draw.rect(screen, color, input_box, 2)

        # Display identified values (if applicable)
        if values_identified:
            draw_text(screen, f"Identified values: {values_identified}", pygame.Color('white'), pygame.Rect(100, 400, 600, 200), font)

        if recording:
            screen.blit(stop_img, button_rect)
        else:
            screen.blit(record_img, button_rect)

        pygame.display.flip()

    pygame.quit()

    if stream and stream.is_active():
        stream.stop_stream()
        stream.close()
    audio.terminate()

if __name__ == "__main__":
    main()
