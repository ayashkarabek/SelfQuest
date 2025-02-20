import gradio as gr
import openai
openai.api_key = "sk-proj-tEgG2Lz9H0r5j7LESL6ET3BlbkFJoQILTcSuiuEg2OPAIwpp"


def transcribe(audio):
#Whisper AI
    audio_file= open(audio, "rb")
    transcript = openai.audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

bot = gr.Interface(fn=transcribe, inputs=gr.Audio(sources="microphone", type="filepath"),outputs="text")

bot.launch()