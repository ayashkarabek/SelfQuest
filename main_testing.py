
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
import json
import openai
import os
import requests



from chatgpt_tested_class import AudioRecorder

from elevenlabs import play
from elevenlabs.client import ElevenLabs

    
# Initialize Pygame
pygame.init()

user_choices = { 'level1': { 'selected_event': None, 'values': [], 'goals': [] } }
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

mouth_closed = pygame.image.load('me1.png').convert_alpha()
mouth_closed = pygame.transform.smoothscale(mouth_closed, (30, 12))
mouth_closedX = 54  # Reset player position
mouth_closedY = 55
        
mouth_opened = pygame.image.load('me2.png').convert_alpha()
mouth_opened = pygame.transform.smoothscale(mouth_opened, (30, 12))
mouth_openedX = 53  # Reset player position
mouth_openedY = 308
#screen.blit(mouth_opened, (mouth_openedX, mouth_openedY))

# Variables to track the state of each item circle
item1_clicked_lvl0 = False
item1_clicked_lvl1 = False
item2_clicked_lvl0 = False
item2_clicked_lvl1 = False
item3_clicked_lvl0 = False
item3_clicked_lvl1 = False
item4_clicked_lvl1 = False
item5_clicked_lvl1 = False
item6_clicked_lvl1 = False
welcome_lvl0 = True
welcome_lvl1 = True

# Current visible comment box
current_comment_box = None
current_comment_text0 = ""
current_comment_text1 = ""
welcome_text_shown0 = True 
welcome_text_shown1 = True

Welcome_page_txt = "Welcome to the game 'M-Tanu'. You will be role playing and making decisions to various situations. Click level zero to get started!"


mouth_closed = pygame.image.load('me1.png').convert_alpha()
mouth_closed = pygame.transform.smoothscale(mouth_closed, (20, 12))

mouth_open = pygame.image.load('me2.png').convert_alpha()
mouth_open = pygame.transform.smoothscale(mouth_open, (20, 12))

mouth_closedX = 32  # Reset player position
mouth_closedY = 306

situa = "You are a high school student excited about participating in a major upcoming school event. The school has announced several events to encourage student involvement and skill development, including sports day, the science fair, and the drama club performance. Your task is to navigate through the preparation process."
problem_sports_day = "1. Team or Individual Event (Scenario: You need to choose between participating in a team sport (e.g., relay race) or an individual event (e.g., 100m sprint). The team event requires collaboration and teamwork, while the individual event allows you to rely solely on your own abilities; Goal: Assess your preference for teamwork versus individual achievement and make a choice that reflects your personal values.); 2. Balancing Practice and Schoolwork (Scenario: Sports Day is approaching, and you need to balance your practice sessions with your schoolwork. Focusing too much on practice might affect your grades, but not practicing enough could hurt your performance; Goal: Develop time management skills to balance both academic and athletic commitments.); 3. Handling a Team Conflict (Scenario: There’s a disagreement within your relay team about the running order. One member insists on being the anchor despite others thinking someone else might be faster; Goal: Learn to mediate team conflicts and come to a decision that benefits the team’s overall performance.)"
problems_science_fair = "1. Working Alone or with a Partner (Scenario: You've been given the option to work alone or with a partner on your science fair project. If you work alone, you have full control over the project, but it might be more challenging to complete everything on time. If you work with a partner, you can share the workload, but you need to coordinate and collaborate effectively; Goal: Evaluate the pros and cons of working alone versus with a partner, and make a decision that aligns with your values of independence or collaboration.); 2. Time Allocation (Scenario: You have limited time to prepare for the science fair. You need to allocate your time effectively between researching your topic, constructing your project, and preparing your presentation; Goal: Learn to prioritize tasks and manage time efficiently to achieve the best outcome.); 3.Resolving a Conflict with a Teammate (Scenario: You and your partner disagree on the direction of the project. Your partner wants to focus on a different aspect of the topic that you think is less important; Goal: Develop conflict resolution skills and find a compromise that satisfies both parties and improves the project.)"
problems_drama_club = "1. Choosing a Role (Scenario: You have the option to choose between a major role and a minor role in the drama performance. The major role requires more time and effort but offers more visibility and recognition. The minor role is less demanding but still important for the play’s success; Goal: Reflect on your comfort with visibility and responsibility and make a decision that aligns with your values and goals.); 2. Balancing Rehearsals and Personal Time (Scenario: The drama performance is in a few weeks, and rehearsals are getting more frequent and intense. You need to balance your commitment to the performance with your personal time and other responsibilities; Goal: Practice effective time management and learn to balance multiple commitments.) 3. Dealing with Performance Anxiety (Scenario: As the performance date approaches, you start feeling anxious about performing in front of an audience. You need to decide whether to push through the anxiety or ask for a smaller role; Goal: Develop strategies to manage anxiety and make decisions that prioritize your mental well-being while still contributing to the team.)"

messages_history = []
possible_messages = [
    
    [
       {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. Start with the question: 'Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?'. Follow-up questions(ONE question at a time) should help the user answer this question by requesting more details or examples. After 5 messages from the assistant, including a thank you message and summary of top 3 values for this question, the conversation should end.NOTE: conversation can't end with question, it should thank user for answers and mention top 3 values AND say to click circle 2 to continue"},
       {"role": "assistant", "content": f"Start with the question: 'Imagine you have unlimited resources for one cause or initiative. What would you choose to support, and why?'. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response to this question. Limit follow-up questions to two and ensure they are related to the original question. Your response should not exceed 20 words."}
   ],
    [
       {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. Start with the question: 'If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?'. Follow-up questions(ONE question at a time) should help the user answer this question by requesting more details or examples. After 5 messages from the assistant, including a thank you message and summary of top 3 values for this question, the conversation should end.NOTE: conversation can't end with question, it should thank user for answers and mention top 3 values AND say to click circle 3 to continue"},
       {"role": "assistant", "content": f"Start with the question: 'If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?'. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response to this question. Limit follow-up questions to two and ensure they are related to the original question. Your response should not exceed 20 words."}
   ],
    [
       {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. Start with the question: 'Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?'. Follow-up questions(ONE question at a time) should help the user answer this question by requesting more details or examples. After 5 messages from the assistant, including a thank you message and summary of top 3 values for the entire conversation(including answers to all 3 questions), the conversation should end.NOTE: conversation can't end with question, it should thank user for answers and mention top 3 values AND congratulate fo rfinishing level 0 say to click Done to go to the next level"},
       {"role": "assistant", "content": f"Start with the question: 'Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?'. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response to this question. Limit follow-up questions to two and ensure they are related to the original question. Your response should not exceed 20 words."}
   ], 
    [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 1 - Understanding User's Values(overall, there will be six sections). In this section, we help the user define their values from a particular situation. The situation is: {situa}. All six sections are interconnected with each other, and while moving from one section to another, the player is encouraged to use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Start with the situation introduction: {situa}. Then, ask the user to select one of the school events from list: Sports Day, Science Fair, Drama Club Performance. they want to get involved in. Help with follow-up questions to understand how the event resonates with their interests and values. Goal of the conversation is to assist the user in identifying key personal values that influenced their choice. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should be related to the original question. Your response should not exceed 30 words and ask one question at a time. Maximum 6 messages are allowed from gpt side, 7th message being the closing thanking the user and mentioning top 3values and telling user to click circle 2 to continue on planning. Never end the conversation by asking question and thanking, if the response is not detailed enough, and you need to ask question, just give it as a statement, like think about this question, then thank and then end; asking question and thanking user and ending conversation is not acceptable. "}
    ],
     [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 2 - Setting Goals Based on User's Values (overall, there will be six sections). In this section, after selecting an event in section 1, the player sets specific, measurable goals fot the values based on section 1.You should be able to remember the values from setion 1 in case i ask you about them, they should only be related to my answer for section 1 do not go off topic. All six sections are interconnected with each other, and while moving from one section to another, the player should use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Review the previous response on section 1, and recall the user’s event selection and top 3 values, and tell the user summary of the previous discussion in section 1 in 15 words. The goal of this conversation is to help player set clear, achievable objectives that align with their values and the chosen event. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should help to meet the goal of the conversation. Your response should not exceed 30 words, and ask one question at a time. Maximum eight messages are allowed from the GPT side, 8th message being the closing, thank the user for their input and mention the goals they set for every value and tell user to click circle 3 to continue playing."}
    ], 
      [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 3 - Decision-Making Scenarios (overall, there will be six sections). In this section, after selecting an event in section 1, and setting goals for those values in section 2, the player encounters various scenarios requiring critical decisions. All six sections are interconnected with each other, and while moving from one section to another, the player is encouraged to use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Review the previous response on section 1, section 2; and tell the user the summary of what they have done untill now, and what they will do in this section. Then, generate a problematic scenario according to the analysis of the previous response: I will provide 3 sub problems for each activity, and your job is to choose one of them and tell it to the user, and guide the user on decision making. Science fair 3 problematic situation within the scenario: {problems_science_fair}; Sports day: {problem_sports_day}; Drama club performance: {problems_drama_club}. The goal of this conversation is to enhance decision-making skills by considering the potential outcomes and aligning choices with personal values and goals. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should help to meet the goal of the conversation. Your response should not exceed 30 words, and ask one question at a time. Maximum 6 messages are allowed from the GPT side, 7th message being the closing, thank the user for their input and mention the important decisions they made in this conversation, and and tell the user click circle 4 to continue. Never end the conversation by asking question and thanking, if the response is not detailed enough, and you need to ask question, just give it as a statement, like think about this question, then thank and then end; asking question and thanking user and ending conversation is not acceptable."}
    ], 
       [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 4 - Reflecting on Past Decisions (overall, there will be six sections). In this section, after selecting an event in section 1, and setting goals for those values in section 2, making important decisions for problematic scenarios in section 3, the player reflects on previous experiences with school events or projects. All six sections are interconnected with each other, and while moving from one section to another, the player is encouraged to use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Review the previous response on section 1, section 2, section 3; and tell the user the event they chose, and values discussed in section 1, and goals settled in section 2, and important decisions made in section 3, and tell it all in 25 words. In this section players answer prompts about past successes and challenges, such as: Describe a time when teamwork was crucial. What worked well and what didn’t?; Recall a project where time management was a challenge. How did you handle it?. The goal of this conversation is to make user to encourage introspection and learning from past experiences to make better decisions in the future. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should help to meet the goal of the conversation. Your response should not exceed 30 words, and ask one question at a time. Maximum 6 messages are allowed from the GPT side, 7th message being the closing, thank the user for their input and summarizing this conversation, and tell the user clicl circle 5 to continue. Never end the conversation by asking question and thanking, if the response is not detailed enough, and you need to ask question, just give it as a statement, like think about this question, then thank and then end; asking question and thanking user and ending conversation is not acceptable."}
       ], 
       [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 5 - Building Confidence (overall, there will be six sections). In this section, after selecting an event in section 1, and setting goals for those values in section 2, making important decisions for problematic scenarios in section 3, and reflecting on the past decisions in section 4, the player participates in confidence-building exercises. All six sections are interconnected with each other, and while moving from one section to another, the player is encouraged to use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Review the previous response on section 1, section 2, section 3, section 4; and tell the user the event they chose, and values discussed in section 1, and goals settled in section 2, and important decisions made in section 3, and reflections in section 4, and tell it all in 30 words. Player participates in confidence-building exercises such as: Practicing a presentation in front of a virtual audience that provides positive and constructive feedback; Completing mini-games that simulate event-related tasks (e.g., answering science quiz questions, performing a short drama scene, etc.) - Choose the exercises through analyzing the user’s response. The goal of this conversation is to boost the player's confidence in their abilities and readiness for the event. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should help to meet the goal of the conversation. Your response should not exceed 30 words, and ask one question at a time. Maximum 6 messages are allowed from the GPT side, 7th message being the closing, thank the user for their input and summarizing this conversation, then tell user to click circle 6 to continue. Never end the conversation by asking question and thanking, if the response is not detailed enough, and you need to ask question, just give it as a statement, like think about this question, then thank and then end; asking question and thanking user and ending conversation is not acceptable."}
       ],
       [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the prompt for section 6 - Seeking Support (overall, there will be six sections). In this section, after selecting an event in section 1, and setting goals for those values in section 2, making important decisions for problematic scenarios in section 3, reflecting on the past decisions in section 4, and boosting confidence/readiness for the event in section 5, the player learns about the importance of seeking support and resources. All six sections are interconnected with each other, and while moving from one section to another, the player is encouraged to use the information from the previous section(remember only 6 sections)."},
        {"role": "assistant", "content": f"Review the previous response on section 1, section 2, section 3, section 4, section 5; and tell the user the event they chose, and values discussed in section 1, and goals settled in section 2, and important decisions made in section 3, and reflections in section 4, and reminding they are ready/confidence increase in section 5, and tell it all in 30 words. Player are presented with scenarios where they must choose how and whom to ask for help: Asking a teacher for additional guidance on the science project; Seeking feedback from a friend on their drama performance; Requesting assistance from a parent with project materials. - Choose the support through analyzing the user’s response. The goal of this conversation is to demonstrate the value of support networks and teach effective ways to seek and utilize help to user. If the user's response is vague or incomplete, ask follow-up questions to gather more details specifically about their response. Follow-up questions should help to meet the goal of the conversation. Your response should not exceed 30 words, and ask one question at a time. Maximum 6 messages are allowed from the GPT side, 7th message being the closing, thank the user for their input and summarizing this conversation, and congratulate user for finishing level 1! Never end the conversation by asking question and thanking, if the response is not detailed enough, and you need to ask question, just give it as a statement, like think about this question, then thank and then end; asking question and thanking user and ending conversation is not acceptable."}
       ],
        [
        {"role": "system", "content": f"You are a conversational agent to help a high school student with self-reflection and self-determination. This is the welcoming page gpt's prompts. Welcome user, and help to navigate the user."},
        {"role": "assistant", "content": f"You should welcome the user, tell the user 'Welcome to SelfQuest where you discover more about yourself! I am minion, and will assist you in this process. Click the levels in ascending order, and for now, only 2 levels are ready: level 0 and level 1' only whenever user is lost, and clicks"}
       ]
    
]
level_val = 9;

#ASK FOR THE URL

def play_text_to_speech(text_to_speak):
    
    client = ElevenLabs(
    api_key="f7b693441b9361408f2e7c0c2ef721be", # Defaults to ELEVEN_API_KEY
    )
    
    response = client.text_to_speech.convert(
        voice_id="IKne3meq5aSn9XLyUdCD", # Adam pre-made voice
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text_to_speak,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
    )

    play(response)
    
"""

def play_text_to_speech(text_to_speak):
    # Eleven Labs API endpoint
    api_key = "f7b693441b9361408f2e7c0c2ef721be"

    url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb/stream"

    payload = {"text": text_to_speak}
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    save_file_path = "./output.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    playsound(save_file_path)





def play_text_to_speech(text_to_speak, language='en'):

    speech = gTTS(text=text_to_speak, lang=language, slow=False)
    speech.save("output.mp3")
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

"""
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
    global welcome_lvl0,welcome_lvl1, welcome_text_shown0, welcome_text_shown1, level_val
    global is_recording, item1_clicked_lvl0, item2_clicked_lvl0, item3_clicked_lvl0, item1_clicked_lvl1, item2_clicked_lvl1, item3_clicked_lvl1, item4_clicked_lvl1, item5_clicked_lvl1, item6_clicked_lvl1, current_comment_box, current_comment_text0, current_comment_text1, current_screen
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
        mouth_closedX = 54  # Reset player position
        mouth_closedY = 304
        screen.blit(mouth_closed, (mouth_closedX, mouth_closedY))
        
        mouth_opened = pygame.image.load('me2.png').convert_alpha()
        mouth_opened = pygame.transform.smoothscale(mouth_opened, (40, 18))
        mouth_openedX = 53  # Reset player position
        mouth_openedY = 308
        #screen.blit(mouth_opened, (mouth_openedX, mouth_openedY))
    
        # Draw clickable items
        level0_text = ["Imagine you have unlimited resources for one cause or initiative. \nWhat would you choose to support, and why?", 
                       "If you had to advise someone younger than you on how to live a \nfulfilling life, what advice would you give them?",
                       "Consider the people you admire most. What qualities do they possess \nthat you find most inspiring or valuable?"
        ]
        item1_pos_lvl0, item1_width_lvl0, item1_height_lvl0 = draw_circle_with_text(screen, "1", 200, 150, item1_clicked_lvl0)
        item2_pos_lvl0, item2_width_lvl0, item2_height_lvl0 = draw_circle_with_text(screen, "2", 550, 200, item2_clicked_lvl0)
        item3_pos_lvl0, item3_width_lvl0, item3_height_lvl0 = draw_circle_with_text(screen, "3", 700, 250, item3_clicked_lvl0)
        
        #only question-> answer: no need for story
        Welcome_text_lvl0 = "Welcome to Level 0! \nCongratulations on reaching the starting point of your journey. In this level, you'll explore various topics through a series of questions designed to prepare you for the challenges ahead. Get ready to reflect, discover, and have fun! \nAre you ready to begin? Click the circle 1 to get your first question!"
        
        # Check for click on items
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if item1_pos_lvl0[0] <= mouse_x <= item1_pos_lvl0[0] + item1_width_lvl0 and item1_pos_lvl0[1] <= mouse_y <= item1_pos_lvl0[1] + item1_height_lvl0:
                item1_clicked_lvl0 = True
                
                level_val = 0
                current_comment_text0 = level0_text[0]
                play_text_to_speech(current_comment_text0)
                welcome_text_shown0 = False
                
                
            elif item2_pos_lvl0[0] <= mouse_x <= item2_pos_lvl0[0] + item2_width_lvl0 and item2_pos_lvl0[1] <= mouse_y <= item2_pos_lvl0[1] + item2_height_lvl0:
                item2_clicked_lvl0 = True
                level_val = 1
                current_comment_text0 = level0_text[1]
                play_text_to_speech(current_comment_text0)
                
            elif item3_pos_lvl0[0] <= mouse_x <= item3_pos_lvl0[0] + item3_width_lvl0 and item3_pos_lvl0[1] <= mouse_y <= item3_pos_lvl0[1] + item3_height_lvl0:
                item3_clicked_lvl0 = True
                level_val = 2
                current_comment_text0 = level0_text[2]
                play_text_to_speech(current_comment_text0)
        
        # Draw record/stop button
        screen.blit(record_img if not is_recording else stop_img, (720, 320))
        # Draw "Done" button if all items are clicked
        if item1_clicked_lvl0 and item2_clicked_lvl0 and item3_clicked_lvl0:
            draw_done_button(surface)
        # Draw current comment box if there is one
        if current_comment_text0:
            draw_comment_box(surface, current_comment_text0, 50, 50)
            
        if welcome_text_shown0:
            draw_comment_box(surface, Welcome_text_lvl0, 40, 30)
            if welcome_lvl0:
                play_text_to_speech(Welcome_text_lvl0)
                welcome_lvl0 = False
        

    elif circle_index == 1:
        surface.fill((174, 207, 240))  # White background for circle 0
        background_image = pygame.image.load('level1.jpg').convert()
        background_image = pygame.transform.scale(background_image, (800, 400))
        screen.blit(background_image, (0, 0))
        
        player_Img = pygame.image.load('Group 49.png').convert_alpha()
        player_Img = pygame.transform.smoothscale(player_Img, (100, 100))
        PlayerX = 10  # Reset player position
        PlayerY = 290
        screen.blit(player_Img, (PlayerX, PlayerY))
        
        mouth_closed = pygame.image.load('me1.png').convert_alpha()
        mouth_closed = pygame.transform.smoothscale(mouth_closed, (30, 15))
        mouth_closedX = 45  # Reset player position
        mouth_closedY = 330
        screen.blit(mouth_closed, (mouth_closedX, mouth_closedY))
        
        mouth_opened = pygame.image.load('me2.png').convert_alpha()
        mouth_opened = pygame.transform.smoothscale(mouth_opened, (40, 18))
        mouth_openedX = 53  # Reset player position
        mouth_openedY = 308
        #screen.blit(mouth_opened, (mouth_openedX, mouth_openedY))
        
        item1_pos_lvl1, item1_width_lvl1, item1_height_lvl1 = draw_circle_with_text(screen, "1", 100, 280, item1_clicked_lvl1)
        item2_pos_lvl1, item2_width_lvl1, item2_height_lvl1 = draw_circle_with_text(screen, "2", 150, 170, item2_clicked_lvl1)
        item3_pos_lvl1, item3_width_lvl1, item3_height_lvl1 = draw_circle_with_text(screen, "3", 285, 250, item3_clicked_lvl1)
        item4_pos_lvl1, item4_width_lvl1, item4_height_lvl1 = draw_circle_with_text(screen, "4", 450, 230, item4_clicked_lvl1)
        item5_pos_lvl1, item5_width_lvl1, item5_height_lvl1 = draw_circle_with_text(screen, "5", 500, 170, item5_clicked_lvl1)
        item6_pos_lvl1, item6_width_lvl1, item6_height_lvl1 = draw_circle_with_text(screen, "6", 600, 200, item6_clicked_lvl1)
        
        Welcome_text_lvl1 = "Welcome to Level 1! \n In this level, you are a high school student excited about participating in a major upcoming school event. The school has announced several events to encourage student involvement and skill development, including sports day, the science fair, and the drama club performance. Your task is to navigate through the preparation process. \n Click the circle 1 to continue."

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if item1_pos_lvl1[0] <= mouse_x <= item1_pos_lvl1[0] + item1_width_lvl1 and item1_pos_lvl1[1] <= mouse_y <= item1_pos_lvl1[1] + item1_height_lvl1:
                item1_clicked_lvl1 = True
                level_val = 3
                current_comment_text1 = "As you prepare for the upcoming school event, think about which activity resonates most with your interests and values. Would you thrive in the collaborative and competitive spirit of Sports Day, the creative and innovative environment of the Science Fair, or the expressive and cooperative atmosphere of the Drama Club Performance? Choose the event that best aligns with your personal values and let's explore why this choice is important to you."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
                
                
            elif item2_pos_lvl1[0] <= mouse_x <= item2_pos_lvl1[0] + item2_width_lvl1 and item2_pos_lvl1[1] <= mouse_y <= item2_pos_lvl1[1] + item2_height_lvl1:
                item2_clicked_lvl1 = True
                level_val = 4
                current_comment_text1 = "Now that you've chosen your event and identified values, it's time to set specific and measurable goals that align with your values. What do you hope to achieve through this event? If you've chosen the Science Fair, for example, your goals might include completing a project on renewable energy, presenting your findings confidently, and collaborating effectively with a partner. Let's outline your objectives to ensure they are clear and achievable."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
                
            elif item3_pos_lvl1[0] <= mouse_x <= item3_pos_lvl1[0] + item3_width_lvl1 and item3_pos_lvl1[1] <= mouse_y <= item3_pos_lvl1[1] + item3_height_lvl1:
                item3_clicked_lvl1 = True
                level_val = 5
                current_comment_text1 = "As you dive deeper into preparing for your event, you'll face various scenarios that require critical decisions. These situations will test your ability to prioritize, collaborate, and resolve conflicts. For instance, if you're preparing for the Science Fair, you might need to decide whether to work alone or with a partner, how to allocate your time efficiently, or how to handle a disagreement with a teammate. Your choices should reflect your values and help you navigate these challenges successfully."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
        
            elif item4_pos_lvl1[0] <= mouse_x <= item4_pos_lvl1[0] + item4_width_lvl1 and item4_pos_lvl1[1] <= mouse_y <= item4_pos_lvl1[1] + item4_height_lvl1:
                item4_clicked_lvl1 = True
                level_val = 6
                current_comment_text1 = "Reflecting on past experiences can provide valuable insights for your current preparations. Think about previous school events or projects you've been involved in. Describe a time when teamwork was crucial—what worked well and what didn't? Recall a project where time management was a challenge—how did you handle it? By reflecting on these experiences, you can learn important lessons to make better decisions moving forward."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
        
            elif item5_pos_lvl1[0] <= mouse_x <= item5_pos_lvl1[0] + item5_width_lvl1 and item5_pos_lvl1[1] <= mouse_y <= item5_pos_lvl1[1] + item5_height_lvl1:
                item5_clicked_lvl1 = True
                level_val = 7
                current_comment_text1 = "Confidence is key to succeeding in any event. Let's participate in some confidence-building exercises to boost your readiness. Whether it's practicing a presentation in front of a virtual audience that provides feedback, or completing mini-games that simulate event-related tasks, these activities will help you feel more prepared and confident in your abilities."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
        
            elif item6_pos_lvl1[0] <= mouse_x <= item6_pos_lvl1[0] + item6_width_lvl1 and item6_pos_lvl1[1] <= mouse_y <= item6_pos_lvl1[1] + item6_height_lvl1:
                item6_clicked_lvl1 = True
                level_val = 8
                current_comment_text1 = "Knowing when and how to seek support is an essential skill. Imagine scenarios where you might need assistance—asking a teacher for additional guidance on your science project, seeking feedback from a friend on your drama performance, or requesting help from a parent with project materials. Let's explore the importance of support networks and learn effective ways to seek and utilize help to ensure your success in the event."
                play_text_to_speech(current_comment_text1)
                welcome_text_shown1 = False
        
        # Draw record/stop button
        screen.blit(record_img if not is_recording else stop_img, (720, 320))
        # Draw "Done" button if all items are clicked
        if item1_clicked_lvl1 and item2_clicked_lvl1 and item3_clicked_lvl1 and item4_clicked_lvl1 and item5_clicked_lvl1 and item6_clicked_lvl1:
            draw_done_button(surface)
        # Draw current comment box if there is one
        if current_comment_text1:
            draw_comment_box(surface, current_comment_text1, 50, 20)
            
        if welcome_text_shown1:
            draw_comment_box(surface, Welcome_text_lvl1, 40, 30)
            if welcome_lvl1:
                play_text_to_speech(Welcome_text_lvl1)
                welcome_lvl1 = False

        
    elif circle_index == 2:
        surface.fill((240, 240, 240))  # Off-white background for circle 2
    else:
        surface.fill((255, 255, 255))  # Default to white background if index is unrecognized

def draw_done_button(surface):
    button_x, button_y = 690, 8
    button_width, button_height = 100, 40  # Adjust dimensions as needed
    button_color = (40, 142, 76)  # Green color

    def draw_rounded_rect(surface, color, rect, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    # Draw rounded rectangle button
    draw_rounded_rect(surface, button_color, (button_x, button_y, button_width, button_height), 10)

    # Draw "Done" text centered within the button
    pygame.freetype.init()
    font = pygame.freetype.SysFont('Arial', 24, bold=True)
    text_surface, text_rect = font.render("Done", (255, 255, 255))  # White text
    text_rect.center = (button_x + button_width // 2, button_y + button_height // 2)
    surface.blit(text_surface, text_rect)

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
    return text;

def load_conversation_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file_path}")
                return []
    return []

def save_conversation_history(file_path, history):
    with open(file_path, 'w') as file:
        json.dump(history, file, indent=4)

# Usage
history_file_path = 'conversation_history1.json'
messages_history = load_conversation_history(history_file_path)

def handle_user_input(user_message, curr_messages, messages_history, history_file_path):
    # Append user's message to current messages
    curr_messages.append({"role": "user", "content": user_message})

    # Combine the conversation history with the current messages
    combined_messages = messages_history + curr_messages

    # Call the OpenAI API to get a response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=combined_messages
    )

    # Extract and print the AI's response
    ai_message = response.choices[0].message['content'].strip()
    print(ai_message)  # Print to terminal

    # Append AI's message to current messages
    curr_messages.append({"role": "assistant", "content": ai_message})

    # Update the conversation history
    messages_history.append({"role": "user", "content": user_message})
    messages_history.append({"role": "assistant", "content": ai_message})

    # Save updated conversation history
    save_conversation_history(history_file_path, messages_history)

    # Play text-to-speech
    play_text_to_speech(ai_message)

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
                    msg = stop_recording()
                    handle_user_input(msg, possible_messages[level_val], messages_history,history_file_path)
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
                if 640 <= mouse_x <= 740 and 0 <= mouse_y <= 40:
                    current_screen = "main"
                    # Change circle color after completing level
                    circle_states[clicked_circle_index] = True

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

    if recording:
        render_recording_text_with_border(screen)

    # Draw button
    if recording:
        screen.blit(stop_img, button_rect)
    else:
        screen.blit(record_img, button_rect)
         
    screen.blit(mouth_closed, (mouth_closedX, mouth_closedY))
    pygame.display.flip()

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

# Close the audio stream
if stream and stream.is_active():
    stream.stop_stream()
    stream.close()
audio.terminate()