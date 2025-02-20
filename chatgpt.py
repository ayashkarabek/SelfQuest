import pygame
import openai
import pyperclip

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Value Identification")

# Fonts
font = pygame.font.Font(None, 32)

# Input box settings
input_box = pygame.Rect(100, 150, 600, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

# Paste button settings
paste_button = pygame.Rect(100, 210, 100, 32)
button_color = pygame.Color('grey')

# Analyze button settings
analyze_button = pygame.Rect(100, 270, 100, 32)

active = False
text = ''
question = "Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?"
values_identified = ''

# FREQUENCY: Values

# OpenAI API key
openai.api_key = 'sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp'

# List of possible values
values_list = [
    "Accountability", "Generosity", "Achievement", "Giving back", "Adaptability", "Grace",
    "Adventure", "Gratitude", "Altruism", "Growth", "Ambition", "Harmony", "Authenticity", "Health",
    "Balance", "Home", "Beauty", "Honesty", "Being the best", "Hope", "Belonging", "Humility",
    "Career", "Humor", "Caring", "Inclusion", "Collaboration", "Independence", "Commitment",
    "Initiative", "Community", "Integrity", "Compassion", "Intuition", "Competence", "Job security",
    "Confidence", "Joy", "Connection", "Justice", "Contentment", "Kindness", "Contribution", "Knowledge",
    "Cooperation", "Leadership", "Courage", "Learning", "Creativity", "Legacy", "Curiosity", "Leisure",
    "Dignity", "Love", "Diversity", "Loyalty", "Efficiency", "Making a difference", "Environment", "Nature",
    "Equality", "Openness", "Ethics", "Optimism", "Excellence", "Order", "Fairness", "Parenting", "Faith",
    "Patience", "Family", "Patriotism", "Financial stability", "Peace", "Forgiveness", "Perseverance",
    "Freedom", "Personal fulfillment", "Friendship", "Power", "Fun", "Pride", "Future generations", "Recognition",
    "Reliability", "Resourcefulness", "Respect", "Responsibility", "Risk-taking", "Safety", "Security",
    "Self-discipline", "Self-expression", "Self-respect", "Serenity", "Service", "Simplicity", "Spirituality",
    "Sportsmanship", "Stewardship", "Success", "Teamwork", "Thrift", "Time", "Tradition", "Travel", "Trust",
    "Truth", "Understanding", "Uniqueness", "Usefulness", "Vision", "Wealth", "Well-being", "Wholeheartedness",
    "Wisdom"
]

def analyze_response(question, response):
    prompt = (
        "The user answered the question with the following response: '{}'\n"
        "Based on the response, identify the top values the individual seems to hold. "
        "Here is a list of possible values: {}"
    ).format(response, ", ".join(values_list))
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant", "content": prompt}
        ]
    )
    
    values_identified = response.choices[0].message['content'].strip()
    return values_identified

def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2

    # Get the height of the font
    font_height = font.size("Tg")[1]

    while text:
        i = 1

        # Determine if the row of text will be outside our area
        if y + font_height > rect.bottom:
            break

        # Determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # If we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # Render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += font_height + line_spacing

        # Remove the text we just blitted
        text = text[i:]

    return text

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            if paste_button.collidepoint(event.pos):
                text = pyperclip.paste()
            if analyze_button.collidepoint(event.pos):
                values_identified = analyze_response(question, text)
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill((30, 30, 30))
    # Render the question
    draw_text(screen, question, pygame.Color('white'), pygame.Rect(100, 50, 600, 80), font)

    # Render the current text
    draw_text(screen, text, color, pygame.Rect(100, 150, 600, 300), font)  # Increase height to 300 for larger text display
    # Resize the box if the text is too long
    width = max(600, font.size(text)[0] + 10)
    input_box.w = width
    # Blit the input_box rect
    pygame.draw.rect(screen, color, input_box, 2)

    # Render the paste button
    pygame.draw.rect(screen, button_color, paste_button)
    paste_text = font.render("Paste", True, pygame.Color('white'))
    screen.blit(paste_text, (paste_button.x + 10, paste_button.y + 5))

    # Render the analyze button
    pygame.draw.rect(screen, button_color, analyze_button)
    analyze_text = font.render("Analyze", True, pygame.Color('white'))
    screen.blit(analyze_text, (analyze_button.x + 10, analyze_button.y + 5))

    # Display identified values
    if values_identified:
        draw_text(screen, f"Identified values: {values_identified}", pygame.Color('white'), pygame.Rect(100, 400, 600, 200), font)

    pygame.display.flip()

pygame.quit()