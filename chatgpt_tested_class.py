import pygame
import pyaudio
import wave
import os
import threading
from gtts import gTTS
import openai

class AudioRecorder:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen settings
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Audio Recorder and Value Identification")

        # Fonts
        self.font = pygame.font.Font(None, 32)

        # Input box settings
        self.input_box = pygame.Rect(100, 150, 600, 32)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive

        self.active = False
        self.text = ''
        self.question = "Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?"
        self.values_identified = ''
        self.ai_message_count = 0
        self.follow_up_count = 0

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

        # List of possible values
        self.values_list = [
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

        # Load and resize images
        self.record_img = pygame.image.load("record.png")
        self.stop_img = pygame.image.load("stop.png")

        self.record_img = pygame.transform.scale(self.record_img, (64, 64))
        self.stop_img = pygame.transform.scale(self.stop_img, (64, 64))

        # Button states
        self.recording = False
        self.button_rect = self.record_img.get_rect(center=(750, 350))

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
            self.handle_ai_response(self.text)

    def audio_to_text(self, audio_file):
        """Convert audio to text using Whisper API."""
        with open(audio_file, "rb") as audio:
            response = openai.Audio.transcribe("whisper-1", audio)
            text = response["text"]
            return text

    def handle_ai_response(self, user_response):
        """Handle the AI response after the user answers the question."""
        if self.ai_message_count >= 3 + self.follow_up_count:
            return

        messages = [
            {"role": "system", "content": "You are a conversational agent to help user (high school student) for self reflection and self determination, understanding the inner feelings of the user, values they prioritize when they make decisions."},
            {"role": "assistant", "content": "The conversation should flow naturally. Start with the following question in the first message: 'Imagine you have unlimited resources for one cause or initiative. What would you choose to do, and why?' Remember, the user should answer to the question 'Imagine you have unlimited resources for one cause or initiative. What would you choose to do, and why?', the follow-up questions, all should help to answer to this question. After the first user response, say, 'I understand.' Comment on their answer, analyze it, and determine if the given information is sufficient to identify their top 3 values. If more information is needed, ask only one follow-up, open-ended question message. If the information is sufficient, thank the user and mention their top 3 values in a maximum of 15 words. The conversation should stop after 4 messages from chatgpt side, and the 4th one being thank you and top 3 value mentioning."},
        ]

        if self.ai_message_count == 0:
            messages.append({"role": "user", "content": user_response})
        elif self.ai_message_count > 0:
            # Check if user response indicates uncertainty about allocation
            if "spend your resources" not in user_response.lower():
                messages.append({"role": "assistant", "content": "How would you choose to allocate resources towards this cause or initiative?"})
            messages.append({"role": "user", "content": user_response})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        ai_message = response.choices[0].message['content'].strip()
        print(ai_message)  # Print to terminal
        self.play_text_to_speech(ai_message)

        self.ai_message_count += 1

        if self.ai_message_count >= 3 + self.follow_up_count:
            # Analyze values based on responses
            identified_values = self.analyze_values(messages)
            self.values_identified = ", ".join(identified_values[:3])  # Assume top 3 values based on analysis
            print(f"Top 3 values identified: {self.values_identified}")
            self.play_text_to_speech(f"Your top values are {self.values_identified}. Thank you for sharing your thoughts.")
            print("Conversation ended.")
        elif "I don't know" in user_response or "I'm not sure" in user_response:
            self.follow_up_count += 1
            print("Asking a follow-up question due to unclear response.")

    def analyze_values(self, messages):
        """Analyze user responses to identify top values."""
        user_responses = [msg["content"] for msg in messages if msg["role"] == "user"]

        values_count = {value: 0 for value in self.values_list}

        # Count occurrences of each value in user responses
        for response in user_responses:
            for value in self.values_list:
                if value.lower() in response.lower():
                    values_count[value] += 1

        # Sort values by count (most mentioned first)
        sorted_values = sorted(values_count.items(), key=lambda x: x[1], reverse=True)
        top_values = [value[0] for value in sorted_values if value[1] > 0]  # Filter out values with zero mentions

        return top_values

    def draw_text(self, surface, text, color, rect, font, aa=False, bkg=None):
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

    def play_text_to_speech(self, text_to_speak, language='en'):
        """Convert text to speech and play it."""
        speech = gTTS(text=text_to_speak, lang=language, slow=False)
        speech.save("output.mp3")
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

    def main(self):
        running = True
        one_time = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect.collidepoint(event.pos):
                        if not self.recording:
                            self.start_recording()
                            self.recording = True
                        else:
                            self.stop_recording()
                            self.recording = False
                    self.color = self.color_active if self.active else self.color_inactive
                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode

            if one_time:
                self.play_text_to_speech(self.question)
                one_time = False    

            self.screen.fill((30, 30, 30))
            self.draw_text(self.screen, self.question, pygame.Color('white'), pygame.Rect(100, 50, 600, 80), self.font)
            self.draw_text(self.screen, self.text, self.color, pygame.Rect(100, 150, 600, 300), self.font)
            width = max(600, self.font.size(self.text)[0] + 10)
            self.input_box.w = width
            pygame.draw.rect(self.screen, self.color, self.input_box, 2)

            # Display identified values (if applicable)
            if self.values_identified:
                self.draw_text(self.screen, f"Identified values: {self.values_identified}", pygame.Color('white'), pygame.Rect(100, 400, 600, 200), self.font)

            if self.recording:
                self.screen.blit(self.stop_img, self.button_rect)
            else:
                self.screen.blit(self.record_img, self.button_rect)

            pygame.display.flip()

        pygame.quit()

        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.main()
