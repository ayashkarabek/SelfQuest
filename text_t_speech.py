import pygame
import speech_recognition as sr
import pyttsx3
import openai

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Voice Chat with ChatGPT")

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
except Exception as e:
    print("Error initializing text-to-speech engine:", e)
    engine = None

# OpenAI API key
openai.api_key = 'sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp"'

# Function to transcribe speech to text
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I did not understand that."
    except sr.RequestError:
        return "Sorry, my speech service is down."

# Function to generate a response from GPT
def gpt_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    return response['choices'][0]['message']['content'].strip()

# Function to speak text
def speak_text(text):
    if engine:
        engine.say(text)
        engine.runAndWait()

# Main loop
running = True
initial_prompt = "Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "assistant", "content": initial_prompt}
]

speak_text(initial_prompt)

follow_up_count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            # User presses 'R' to record
            user_input = recognize_speech()
            if user_input.lower() == "quit":
                running = False
            else:
                messages.append({"role": "user", "content": user_input})
                follow_up_count += 1
                
                # Analyze the response and generate a follow-up question or conclusion
                if follow_up_count <= 3:
                    response = gpt_response(messages)
                    messages.append({"role": "assistant", "content": response})
                    print(f"ChatGPT: {response}")
                    speak_text(response)
                else:
                    # Conclude the conversation with top 3 values
                    final_analysis_prompt = "Based on the previous responses, identify the top 3 values the user prioritizes while making decisions."
                    messages.append({"role": "user", "content": final_analysis_prompt})
                    final_response = gpt_response(messages)
                    print(f"ChatGPT: {final_response}")
                    speak_text(final_response)
                    running = False

    screen.fill((255, 255, 255))
    font = pygame.font.Font(None, 36)
    text_surface = font.render("Press 'R' to record your response...", True, (0, 0, 0))
    screen.blit(text_surface, (200, 250))
    pygame.display.flip()

pygame.quit()
