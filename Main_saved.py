
from gtts import gTTS
import pygame
import pygame.freetype
import pyaudio
import wave
import os
import threading
import tkinter as tk
from tkinter import messagebox
import openai
    
# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 400))
# Load and resize images
record_img = pygame.image.load("record.png")
stop_img = pygame.image.load("stop.png")

record_img = pygame.transform.scale(record_img, (64, 64))
stop_img = pygame.transform.scale(stop_img, (64, 64))

# Button states
recording = False
button_rect = record_img.get_rect(center=(750, 350))


# Set title and icon
pygame.display.set_caption("Self-autonomy Self-determination")
icon = pygame.image.load('user.png')
pygame.display.set_icon(icon)

# Load and scale the background image
background_image = pygame.image.load('dm1.png').convert()
background_image = pygame.transform.scale(background_image, (800, 400))

# Load the player image and resize it to 64x64 pixels
player_Img = pygame.image.load('Group 49.png').convert_alpha()
player_Img = pygame.transform.smoothscale(player_Img, (64, 64))
PlayerX = 10
PlayerX_change = 0
PlayerY = 280

# Load images for record and stop buttons
record_img = pygame.image.load('record.png').convert_alpha()
record_img = pygame.transform.smoothscale(record_img, (64, 64))

stop_img = pygame.image.load('stop.png').convert_alpha()
stop_img = pygame.transform.smoothscale(stop_img, (64, 64))

# Define global variables
is_recording = False  # Initial state for recording

# Variables to track the state of each item circle
item1_clicked = False
item2_clicked = False
item3_clicked = False

# Current visible comment box
current_comment_box = None
current_comment_text = ""

mouth_closed = pygame.image.load('me1.png').convert_alpha()
mouth_closed = pygame.transform.smoothscale(mouth_closed, (20, 12))

mouth_open = pygame.image.load('me2.png').convert_alpha()
mouth_open = pygame.transform.smoothscale(mouth_open, (20, 12))

mouth_closedX = 32  # Reset player position
mouth_closedY = 306

"""
    def play_text_to_speech(text_to_speak, language='en'):
        # ElevenLabs API endpoint and API key
    api_url = "https://api.elevenlabs.io/v1/text-to-speech"
    api_key = "093cdeeaf989d95e59d62b1399db692f"

    # API request payload
    payload = {
        "text": text_to_speak,
        "voice": "YOUR_CHOSEN_VOICE_ID",
        "language": language
    }

    # API request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Make the API request
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)

        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()
    else:
        print("Error:", response.json())
"""

def play_text_to_speech(text_to_speak, language='en'):
    speech = gTTS(text=text_to_speak, lang=language, slow=False)
    speech.save("output.mp3")
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

# Function to draw a circle with border and text inside
def draw_circle_with_text(surface, text, coordX, coordY, clicked):
    # Define colors
    YELLOW = (255, 222, 89)
    BROWN = (181, 117, 8)
    WHITE = (255, 255, 255)
    CLICKED_FILL = (0, 191, 99)    # New clicked fill color (#00BF63)
    CLICKED_BORDER = (4, 133, 71)  # New clicked border color (#048547)
    circle_radius = 20  # 30x30 pixels circle
    border_width = 2
    font_size = 22

    center = (coordX, coordY)

    # Change color if clicked
    if clicked:
        fill_color = CLICKED_FILL
        border_color = CLICKED_BORDER
    else:
        fill_color = YELLOW
        border_color = BROWN

    # Draw filled circle inside with chosen color
    pygame.draw.circle(surface, fill_color, center, circle_radius)

    # Draw border with chosen color
    pygame.draw.circle(surface, border_color, center, circle_radius, border_width)

    # Font
    pygame.freetype.init()
    font = pygame.freetype.SysFont('Arial', font_size, bold=True)

    # Calculate text position to center it in the circle
    text_width, text_height = font.get_rect(text)[2:]
    text_position = (center[0] - text_width // 2, center[1] - text_height // 2)

    # Render text
    font.render_to(surface, text_position, text, WHITE)

    # Return text position and dimensions
    return text_position, text_width, text_height

# Function to draw a new screen based on circle index
def draw_new_screen(surface, circle_index):
    def draw_rounded_rect(surface, color, rect, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        
    global is_recording, item1_clicked, item2_clicked, item3_clicked, current_comment_box, current_comment_text
    if circle_index == 0:
        surface.fill((174, 207, 240))  # White background for circle 0
        background_image = pygame.image.load('level0.jpg').convert()
        background_image = pygame.transform.scale(background_image, (800, 400))
        screen.blit(background_image, (0, 0))
       
        # Update player image and position
        player_Img = pygame.image.load('Group 49.png').convert_alpha()
        player_Img = pygame.transform.smoothscale(player_Img, (128, 128))
        PlayerX = 10  # Reset player position
        PlayerY = 250
        screen.blit(player_Img, (PlayerX, PlayerY))
        
        mouth_closed = pygame.image.load('me1.png').convert_alpha()
        mouth_closed = pygame.transform.smoothscale(mouth_closed, (40, 18))
        mouth_closedX = 50  # Reset player position
        mouth_closedY = 304
        screen.blit(mouth_closed, (mouth_closedX, mouth_closedY))
        
        mouth_opened = pygame.image.load('me2.png').convert_alpha()
        mouth_opened = pygame.transform.smoothscale(mouth_opened, (40, 18))
        mouth_openedX = 53  # Reset player position
        mouth_openedY = 308
        #screen.blit(mouth_opened, (mouth_openedX, mouth_openedY))
    
        # Draw clickable items
        text1 = "Imagine you have unlimited resources for one cause or initiative. \nWhat would you choose to support, and why?"
        text2 = "If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?"
        text3 = "Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?"
        
        item1_pos, item1_width, item1_height = draw_circle_with_text(screen, "1", 200, 150, item1_clicked)
        item2_pos, item2_width, item2_height = draw_circle_with_text(screen, "2", 550, 200, item2_clicked)
        item3_pos, item3_width, item3_height = draw_circle_with_text(screen, "3", 700, 250, item3_clicked)
        
        
        # Check for click on items
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if item1_pos[0] <= mouse_x <= item1_pos[0] + item1_width and item1_pos[1] <= mouse_y <= item1_pos[1] + item1_height:
                item1_clicked = True
                current_comment_text = text1
                play_text_to_speech(current_comment_text)
            elif item2_pos[0] <= mouse_x <= item2_pos[0] + item2_width and item2_pos[1] <= mouse_y <= item2_pos[1] + item2_height:
                item2_clicked = True
                current_comment_text = text2
                play_text_to_speech(current_comment_text)
            elif item3_pos[0] <= mouse_x <= item3_pos[0] + item3_width and item3_pos[1] <= mouse_y <= item3_pos[1] + item3_height:
                item3_clicked = True
                current_comment_text = text3
                play_text_to_speech(current_comment_text)
        
        # Draw record/stop button
        screen.blit(record_img if not is_recording else stop_img, (720, 320))
        # Draw "Done" button if all items are clicked
        if item1_clicked and item2_clicked and item3_clicked:
            # Define button dimensions and position
            button_x, button_y = 690, 8
            button_width, button_height = 100, 40  # Adjust dimensions as needed
            button_color = (40, 142, 76)  # Green color

            # Draw rounded rectangle button
            draw_rounded_rect(surface, button_color, (button_x, button_y, button_width, button_height), 10)

            # Draw "Done" text centered within the button
            pygame.freetype.init()
            font = pygame.freetype.SysFont('Arial', 24, bold=True)
            text_surface, text_rect = font.render("Done", (255, 255, 255))  # White text
            text_rect.center = (button_x + button_width // 2, button_y + button_height // 2)
            surface.blit(text_surface, text_rect)
        
        # Draw current comment box if there is one
        if current_comment_text:
            draw_comment_box(surface, current_comment_text, 50, 50)

    elif circle_index == 1:
        surface.fill((200, 200, 200))  # Light gray background for circle 1
    elif circle_index == 2:
        surface.fill((240, 240, 240))  # Off-white background for circle 2
    else:
        surface.fill((255, 255, 255))  # Default to white background if index is unrecognized

# Function to draw a comment box
def draw_comment_box(surface, comment, coordX, coordY):
    WHITE = (255, 255, 255)
    BORDER_COLOR = (0, 0, 0)
    FONT_COLOR = (0, 0, 0)
    font_size = 16
    padding = 10
    border_width = 2
    border_radius = 10

    font = pygame.freetype.SysFont('Arial', font_size)

    words = comment.split()
    lines = []
    current_line = ""

    for word in words:
        if font.get_rect(current_line + word + " ")[2] <= 700:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "

    if current_line:
        lines.append(current_line)

    text_height = font.get_sized_height()
    text_width = max(font.get_rect(line)[2] for line in lines)

    box_width = min(text_width + 2 * padding, 700)
    box_height = min(text_height * len(lines) + 2 * padding, 300)

    box_x = coordX
    box_y = coordY

    pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height), border_radius=border_radius)
    pygame.draw.rect(surface, BORDER_COLOR, (box_x, box_y, box_width, box_height), border_width, border_radius=border_radius)

    for i, line in enumerate(lines):
        text_surface, _ = font.render(line, FONT_COLOR)
        surface.blit(text_surface, (box_x + padding, box_y + padding + i * text_height))

def draw_rectangle(surface):
    pygame.draw.rect(surface, (0, 255, 0), (350, 150, 100, 100))

def draw_diamond(surface):
    center = (100, 200)
    points = [(center[0], center[1] - 50), (center[0] - 50, center[1]), (center[0], center[1] + 50), (center[0] + 50, center[1])]
    pygame.draw.polygon(surface, (0, 0, 255), points)

def draw_circle_outline(surface):
    pygame.draw.circle(surface, (255, 255, 0), (400, 200), 50, 2)


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
    
    
def render_recording_text_with_border(surface):
    font = pygame.font.Font(None, 150)
    text = "RECORDING!"

    # Render the border (red) first
    border_thickness = 2
    border_color = (255, 0, 0)  # Red
    for dx, dy in [(border_thickness, 0), (-border_thickness, 0), (0, border_thickness), (0, -border_thickness)]:
        text_surface = font.render(text, True, border_color)
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2 + dx, surface.get_height() // 2 + dy))
        surface.blit(text_surface, text_rect)

    # Render the main text (black) on top
    text_surface = font.render(text, True, (0, 0, 0))  # Black
    text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(text_surface, text_rect)



# Main game loop
running = True
circle_centers = [(100, 150), (130, 250), (200, 200), (280, 150), (350, 210)]
circle_states = [False] * len(circle_centers)  # Initialize all circles as not clicked
current_screen = "main"  # Start with the main screen
clicked_circle_index = -1  # To track which circle was clicked

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if current_screen == "main":
                if event.key == pygame.K_LEFT:
                    PlayerX_change = -0.2
                elif event.key == pygame.K_RIGHT:
                    PlayerX_change = 0.2
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                if not recording:
                    start_recording()
                    recording = True
                else:
                    stop_recording()
                    recording = False
        
        if event.type == pygame.KEYUP:
            if current_screen == "main":
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    PlayerX_change = 0
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if current_screen == "main":
                for i, (circle_x, circle_y) in enumerate(circle_centers):
                    distance = ((mouse_x - circle_x) ** 2 + (mouse_y - circle_y) ** 2) ** 0.5
                    if distance < 15:
                        current_screen = "circle_clicked"
                        clicked_circle_index = i
                        break
            elif current_screen == "circle_clicked":
                if 700 <= mouse_x <= 780 and 50 <= mouse_y <= 80:
                    current_screen = "main"
                    # Change circle color after completing level
                    circle_states[clicked_circle_index] = True

    # Draw button
    if recording:
        screen.blit(stop_img, button_rect)
    else:
        screen.blit(record_img, button_rect)

    pygame.display.flip()
    

    if current_screen == "main":
        # Update player position
        PlayerX += PlayerX_change

        # Clear screen

    # Fill the screen with the background image
        screen.blit(background_image, (0, 0))

# Draw circles with text
        for i, (circle_x, circle_y) in enumerate(circle_centers):
            draw_circle_with_text(screen, str(i), circle_x, circle_y, circle_states[i])

        # Draw player
        screen.blit(player_Img, (PlayerX, PlayerY))
    
    elif current_screen == "circle_clicked":
        draw_new_screen(screen, clicked_circle_index)

        if recording:
            render_recording_text_with_border(screen)

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

# Close the audio stream
if stream and stream.is_active():
    stream.stop_stream()
    stream.close()
audio.terminate()
