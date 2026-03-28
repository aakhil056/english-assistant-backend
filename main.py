import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

# Allow your GitHub website to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

class TextInput(BaseModel):
    text: str
    practice_mode: bool = False
    ignore_capitalization: bool = False

@app.post("/check-grammar")
async def check_grammar(input_data: TextInput):
    if not model:
        return {"tutor_feedback": "I am online, but I am missing my Google API Key!"}

    if input_data.practice_mode:
        prompt = f"""
        You are a supportive spoken-English tutor. The student is talking to you.
        Student said: "{input_data.text}"
        RULES:
        1. IGNORE capitalization and minor punctuation.
        2. If their grammar is wrong, gently correct them in 1 or 2 short sentences.
        3. If perfect, praise them.
        4. DO NOT ask a follow-up question.
        """
    else:
        prompt = f"""
        You are an English tutor. Student wrote: "{input_data.text}"
        Correct any spelling or grammar mistakes briefly. DO NOT ask follow-up questions.
        """

    try:
        response = model.generate_content(prompt)
        feedback = response.text.replace("*", "")
        return {"tutor_feedback": feedback.strip()}
    except Exception as e:
        return {"tutor_feedback": "I had a quick glitch. Please say that again!"}

@app.get("/")
async def root():
    return {"message": "XLR8 Academy Backend is Running!"}
