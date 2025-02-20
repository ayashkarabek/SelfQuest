import pygame
import pygame.freetype
import pyttsx3

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 400))

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
record_img = pygame.image.load('record.png').convert_alpha()  # Replace with your record button image path
record_img = pygame.transform.smoothscale(record_img, (64, 64))

stop_img = pygame.image.load('stop.png').convert_alpha()      # Replace with your stop button image path
stop_img = pygame.transform.smoothscale(stop_img, (64, 64))

# Define global variables
is_recording = False  # Initial state for recording

# Variables to track the state of each item circle
item1_clicked = False
item2_clicked = False
item3_clicked = False

# Initialize text-to-speech engine
engine = pyttsx3.init()

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
        
    global is_recording, item1_clicked, item2_clicked, item3_clicked
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
    
        # Draw clickable items
        text1 = "This is text for item 1."
        text2 = "This is text for item 2."
        text3 = "This is text for item 3."
        
        item1_pos, item1_width, item1_height = draw_circle_with_text(screen, "1", 200, 150, item1_clicked)
        item2_pos, item2_width, item2_height = draw_circle_with_text(screen, "2", 400, 150, item2_clicked)
        item3_pos, item3_width, item3_height = draw_circle_with_text(screen, "3", 600, 150, item3_clicked)

        # Add audio functionality when clicking on each circle
        if item1_clicked:
            engine.say(text1)
            engine.runAndWait()
        if item2_clicked:
            engine.say(text2)
            engine.runAndWait()
        if item3_clicked:
            engine.say(text3)
            engine.runAndWait()

    pygame.display.update()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if 200 <= pos[0] <= 220 and 130 <= pos[1] <= 170:
                item1_clicked = not item1_clicked
            elif 400 <= pos[0] <= 420 and 130 <= pos[1] <= 170:
                item2_clicked = not item2_clicked
            elif 600 <= pos[0] <= 620 and 130 <= pos[1] <= 170:
                item3_clicked = not item3_clicked

    screen.fill((174, 207, 240))  # White background
    draw_new_screen(screen, 0)
    pygame.display.update()

pygame.quit()