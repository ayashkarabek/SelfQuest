import pygame
import pygame.freetype
import pyttsx3

# Initialize Pygame
pygame.init()

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Set voice to a young woman (you might need to adjust this based on available voices)
engine.setProperty('voice', voices[1].id)  # This is an example, choose the appropriate index

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
        item2_pos, item2_width, item2_height = draw_circle_with_text(screen, "2", 550, 200, item2_clicked)
        item3_pos, item3_width, item3_height = draw_circle_with_text(screen, "3", 700, 250, item3_clicked)
        
        # Check for click on items
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if item1_pos[0] <= mouse_x <= item1_pos[0] + item1_width and item1_pos[1] <= mouse_y <= item1_pos[1] + item1_height:
                item1_clicked = True
                draw_comment_box(surface, text1, 50, 50)
                engine.say(text1)
                engine.runAndWait()
            elif item2_pos[0] <= mouse_x <= item2_pos[0] + item2_width and item2_pos[1] <= mouse_y <= item2_pos[1] + item2_height:
                item2_clicked = True
                draw_comment_box(surface, text2, 50, 50)
                engine.say(text2)
                engine.runAndWait()
            elif item3_pos[0] <= mouse_x <= item3_pos[0] + item3_width and item3_pos[1] <= mouse_y <= item3_pos[1] + item3_height:
                item3_clicked = True
                draw_comment_box(surface, text3, 50, 50)
                engine.say(text3)
                engine.runAndWait()
        
        # Draw record/stop button
        screen.blit(record_img if not is_recording else stop_img, (720, 320))
        # Draw "Done" button if all items are clicked
        if item1_clicked and item2_clicked and item3_clicked:
            # Define button dimensions and position
            button_x, button_y = 680, 30
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

    elif circle_index == 1:
        surface.fill((200, 200, 200))  # Light gray background for circle 1
        draw_rectangle(surface)
        
        button_x, button_y = 680, 30
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
    
    elif circle_index == 2:
        surface.fill((150, 150, 150))  # Dark gray background for circle 2
        draw_diamond(surface)
        
        button_x, button_y = 680, 30
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
        
    elif circle_index == 3:
        surface.fill((100, 100, 100))  # Even darker gray background for circle 3
        draw_circle_outline(surface)
        
        button_x, button_y = 680, 30
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
        
    elif circle_index == 4:
        surface.fill((255, 255, 255))
    
        button_x, button_y = 680, 30
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
    
    
def draw_comment_box(surface, text, x, y):
    pygame.freetype.init()
    font = pygame.freetype.SysFont('Arial', 16)
    rect_width = 10 + font.get_rect(text)[2]
    rect_height = 10 + font.get_rect(text)[3]
    
    pygame.draw.rect(surface, (255, 255, 255), (x, y, rect_width, rect_height))  # White comment box
    pygame.draw.rect(surface, (0, 0, 0), (x, y, rect_width, rect_height), 2)  # Black border
    
    font.render_to(surface, (x + 5, y + 5), text, (0, 0, 0))  # Render text in comment box

def draw_rectangle(surface):
    pygame.draw.rect(surface, (0, 255, 0), (350, 150, 100, 100))  # Green rectangle

def draw_diamond(surface):
    center = (100, 200)
    points = [(center[0], center[1] - 50), (center[0] - 50, center[1]), (center[0], center[1] + 50), (center[0] + 50, center[1])]
    pygame.draw.polygon(surface, (0, 0, 255), points)  # Blue diamond

def draw_circle_outline(surface):
    pygame.draw.circle(surface, (255, 255, 0), (400, 200), 50, 2)  # Yellow circle outline

# Function to toggle recording state and change button image
def toggle_recording():
    global is_recording, record_img, stop_img
    is_recording = not is_recording
    record_img = pygame.image.load('record.png').convert_alpha() if not is_recording else pygame.image.load('stop.png').convert_alpha()
    record_img = pygame.transform.smoothscale(record_img, (64, 64))

# Game loop
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
                elif 700 <= mouse_x <= 764 and 300 <= mouse_y <= 364:
                    toggle_recording()

    if current_screen == "main":
        # Update player position
        PlayerX += PlayerX_change

        # Clear screen
        screen.blit(background_image, (0, 0))

        # Draw circles with text
        for i, (circle_x, circle_y) in enumerate(circle_centers):
            draw_circle_with_text(screen, str(i), circle_x, circle_y, circle_states[i])

        # Draw player
        screen.blit(player_Img, (PlayerX, PlayerY))
    
    elif current_screen == "circle_clicked":
        draw_new_screen(screen, clicked_circle_index)

    # Update display
    pygame.display.update()

# Quit Pygame
pygame.quit()
