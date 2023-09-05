from fastapi import FastAPI, UploadFile
from dotenv import load_dotenv
import json
import os
import openai

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/talk")
async def post_audio(file: UploadFile): #we are passing the file as an argument of type UploadFile
    user_message = transcribe_audio(file) #we are calling the function transcribe_audio and passing the file as an argument
    chat_response = get_chat_response(user_message)




#functions
def transcribe_audio(file):
    audio_file= open(file.filename, "rb") # we are opening the file in file.name and reading the file in bytes
    transcript = openai.Audio.transcribe("whisper-1", audio_file) #We are then sending the file to transcribe in openai
    print(transcript)
    return transcript

def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message['text']})
 
    gpt_response = gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    
    parsed_gpt_response = gpt_response['choices'][0]['message']['content']
    
    # Save messages    
    save_messages(user_message['text'], parsed_gpt_response)

    
def load_messages():
    messages = []
    file = 'db.json'
    
#IF FILE IS EMPTY 
    empty = os.stat(file).st_size == 0 #THIS WILL TELL US IF THE FILE IS EMPTY OR NOT

#IF NOT EMPTY
    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    
    else:
        messages.append(
            {"role": "system", "content": "You are a interviewing the user for a front-end React developer position. Ask short questions that are relevant to a junior level developer. Your name is Greg. The user is Travis. Keep resposes under 30 words and be funny sometimes."}
        )        
        
    return messages

def save_messages(user_message, gpt_response):
    file = 'db.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})
    with open(file, 'w') as f: #we are opening the file in write mode
        json.dump(messages, f) #we are dumping the messages into the file
    
    