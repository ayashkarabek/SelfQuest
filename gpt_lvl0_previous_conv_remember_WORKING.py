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
pygame.display.set_caption("Level 0: question 1 testing.")


# Fonts
font = pygame.font.Font(None, 32)


# Input box settings
input_box = pygame.Rect(100, 150, 600, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive


active = False
text = ''
question = ["Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?",
          "If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?",
          "Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?"
      ]
values_identified = ''
ai_message_count = 0
follow_up_count = 0
responses_file = 'user_responses_lvl0.json'
user_responses = []
ai_response_text = ''  # Add this variable to store AI's response


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


def load_responses():
  """Load previous user responses from a file."""
  global user_responses
  if os.path.exists(responses_file):
      with open(responses_file, 'r') as file:
          user_responses = json.load(file)
  else:
      user_responses = []


def save_response(response):
  """Save the user's response to a file."""
  user_responses.append(response)
  with open(responses_file, 'w') as file:
      json.dump(user_responses, file)


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
      save_response(text)
      handle_ai_response1(text)


def audio_to_text(audio_file):
  """Convert audio to text using Whisper API."""
  with open(audio_file, "rb") as audio:
      response = openai.Audio.transcribe("whisper-1", audio)
      text = response["text"]
      return text

def handle_ai_response1(user_response):
   """Handle the AI response after the user answers the question."""
   global question, ai_message_count, values_identified, follow_up_count, user_responses, ai_response_text


   user_responses.append(user_response)  # Store the user's response
   save_response(user_response)  # Save the user's response to a file


   if ai_message_count >= 4 + follow_up_count:
       return


   messages = [
       {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. Start with the question: {question[0]}. Follow-up questions(ONE question at a time) should help the user answer this question by requesting more details or examples. After 5 messages from the assistant, including a thank you message and summary of top 3 values, the conversation should end.NOTE: conversation can't end with question, it should thank user for answers and mention top 3 values"},
       {"role": "assistant", "content": f"Start with the question: {question[1]}. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response to this question. Limit follow-up questions to two and ensure they are related to the original question. Your response should not exceed 50 words."}
   ]




   # Include previous user responses in the conversation history
   for i, resp in enumerate(user_responses[:-1]):
       messages.append({"role": "user", "content": resp})
       if i % 2 == 0:
           messages.append({"role": "assistant", "content": "I understand. Could you provide more details, examples, or past stories related to the original question?"})


   # Add the latest user response
   messages.append({"role": "user", "content": user_response})


   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=messages
   )


   ai_message = response.choices[0].message['content'].strip()
   print(ai_message)  # Print to terminal
   ai_response_text = ai_message  # Store AI's response for display
   play_text_to_speech(ai_message)


   ai_message_count += 1


   # Check if a follow-up is needed based on user response
   if ai_message_count >= 4:
       values_identified = ai_message  # Assuming the last response mentions top 3 values
       print("Conversation ended.")
   elif "I don't know" in user_response or "I'm not sure" in user_response:
       follow_up_count += 1
       print("Asking a follow-up question due to unclear response.")
   elif "tell me more about" in ai_message.lower() or "can you elaborate" in ai_message.lower():
       follow_up_count += 1
       print("Asking for more details related to the original question.")


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
          image.setscolorkey(bkg)
      else:
          image = font.render(text[:i], aa, color)


      surface.blit(image, (rect.left, y))
      y += font_height + line_spacing
      text = text[i:]


  return text


def play_text_to_speech(text_to_speak, language='en'):
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


   # Clear previous responses at the start of each run
   if os.path.exists(responses_file):
       os.remove(responses_file)
   user_responses.clear()


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
           play_text_to_speech(question[0])
           one_time = False


       screen.fill((30, 30, 30))
       draw_text(screen, question[0], pygame.Color('white'), pygame.Rect(100, 50, 600, 80), font)
      
       # Show AI's response on the screen
       if ai_response_text:
           draw_text(screen, ai_response_text, pygame.Color('white'), pygame.Rect(100, 150, 600, 200), font)


       width = max(600, font.size(text)[0] + 10)
       input_box.w = width
       pygame.draw.rect(screen, color, input_box, 2)


       # Display identified values (if applicable)
       if values_identified:
           draw_text(screen, f"Identified values: {values_identified}", pygame.Color('white'), pygame.Rect(100, 350, 600, 50), font)


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



