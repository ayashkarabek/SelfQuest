# chat_module.py

import pyaudio
from gtts import gTTS
import wave
import os
import threading
import pygame
import openai
import json

class ChatModule:
    def __init__(self):
        self.one_time = True
        self.active = False
        self.text = ''
        self.question = ["Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?",
                         "If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?",
                         "Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?"]
        self.values_identified = ''
        self.ai_message_count = 0
        self.follow_up_count = 0
        self.responses_file = 'user_responses_lvl0.json'
        self.user_responses = []
        self.ai_response_text = ''  # Add this variable to store AI's response

        # Initialize Pygame
        pygame.init()

        # OpenAI API key
        openai.api_key = 'sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp'

        # Parameters for recording
        self.FORMAT = pyaudio.paInt16
        self.RATE = 44100
        self.CHUNK = 1024

        # Global variables
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording_thread = None
        self.frames = []

        self.load_responses()

    def load_responses(self):
        """Load previous user responses from a file."""
        if os.path.exists(self.responses_file):
            with open(self.responses_file, 'r') as file:
                self.user_responses = json.load(file)
        else:
            self.user_responses = []

    def save_response(self, response):
        """Save the user's response to a file."""
        self.user_responses.append(response)
        with open(self.responses_file, 'w') as file:
            json.dump(self.user_responses, file)

    def get_next_filename(self, prefix="recording", extension=".wav"):
        """Get the next available filename in the sequence."""
        i = 1
        while os.path.exists(f"{prefix}{i}{extension}"):
            i += 1
        return f"{prefix}{i}{extension}"

    def record_audio(self, stream, frames):
        """Record audio in chunks and save to frames."""
        while getattr(self.recording_thread, "do_run", True):
            data = stream.read(self.CHUNK)
            frames.append(data)

    def start_recording(self):
        """Start audio recording in a separate thread."""
        self.frames = []
        try:
            self.stream = self.audio.open(format=self.FORMAT,
                                          channels=2,
                                          rate=self.RATE,
                                          input=True,
                                          frames_per_buffer=self.CHUNK)
        except OSError as e:
            print(f"Stereo not supported: {e}, falling back to mono.")
            self.stream = self.audio.open(format=self.FORMAT,
                                          channels=1,
                                          rate=self.RATE,
                                          input=True,
                                          frames_per_buffer=self.CHUNK)

        self.recording_thread = threading.Thread(target=self.record_audio, args=(self.stream, self.frames))
        self.recording_thread.do_run = True
        self.recording_thread.start()
        print("Recording...")

    def stop_recording(self):
        """Stop audio recording and save to file."""
        if self.recording_thread:
            self.recording_thread.do_run = False
            self.recording_thread.join()

        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()

        output_filename = self.get_next_filename()
        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(self.stream._channels)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))

        print(f"Audio saved to {output_filename}")
        self.text = self.audio_to_text(output_filename)
        if self.text:
            print(f"Transcription: {self.text}")
            self.save_response(self.text)
            self.handle_ai_response(self.text)

    def audio_to_text(self, audio_file):
        """Convert audio to text using Whisper API."""
        with open(audio_file, "rb") as audio:
            response = openai.Audio.transcribe("whisper-1", audio)
            text = response["text"]
            return text

    def handle_ai_response(self, user_response):
        """Handle the AI response after the user answers the question."""
        self.user_responses.append(user_response)  # Store the user's response
        self.save_response(user_response)  # Save the user's response to a file

        if self.ai_message_count >= 4 + self.follow_up_count:
            return

        messages = [
            {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. Start with the question: {self.question[0]}. Follow-up questions(ONE question at a time) should help the user answer this question by requesting more details or examples. After 5 messages from the assistant, including a thank you message and summary of top 3 values, the conversation should end.NOTE: conversation can't end with question, it should thank user for answers and mention top 3 values"},
            {"role": "assistant", "content": f"Start with the question: {self.question[1]}. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response to this question. Limit follow-up questions to two and ensure they are related to the original question. Your response should not exceed 50 words."}
        ]

        # Include previous user responses in the conversation history
        for i, resp in enumerate(self.user_responses[:-1]):
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
        self.ai_response_text = ai_message  # Store AI's response for display
        self.play_text_to_speech(ai_message)

        self.ai_message_count += 1

        # Check if a follow-up is needed based on user response
        if self.ai_message_count >= 4:
            self.values_identified = ai_message  # Assuming the last response mentions top 3 values
            print("Conversation ended.")
        elif "I don't know" in user_response or "I'm not sure" in user_response:
            self.follow_up_count += 1
            print("Asking a follow-up question due to unclear response.")
        elif "tell me more about" in ai_message.lower() or "can you elaborate" in ai_message.lower():
            self.follow_up_count += 1
            print("Asking for more details related to the original question.")

    def play_text_to_speech(self, text_to_speak, language='en'):
        speech = gTTS(text=text_to_speak, lang=language, slow=False)
        speech.save("output.mp3")
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()
