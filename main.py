from fastapi import FastAPI
from pydantic import BaseModel
from auth.auth import register_user
from fastapi import HTTPException
from auth.auth import authenticate_user, create_access_token
from datetime import timedelta
from fastapi import Depends
from auth.auth import get_current_user
from llm.prompts import gen_prompt, gen_advice, analyze_journal, generate_insights
from llm.db import get_entries, save, get_hist, delete_journal, get_dashboard_data
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class RegisterModel(BaseModel):
    user_id: str
    password: str

@app.post("/register")
def register(data: RegisterModel):
    return register_user(data.user_id, data.password)

@app.post("/login")
def login(data: RegisterModel):
    user = authenticate_user(data.user_id, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(
        data={"sub": user["user_id"]},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": token, "token_type": "bearer"}

class JournalInput(BaseModel):
    journal: str

@app.get("/prompt")
def get_prompt(user_id: str = Depends(get_current_user)):
    #print("user id from ", user_id)
    entries = get_entries(user_id)
    prompt = gen_prompt(entries)
    return {"prompt": prompt}

@app.post("/journal")
def write_journal(data: JournalInput, user_id: str = Depends(get_current_user)):
    prompt = gen_prompt(get_entries(user_id))
    advice = gen_advice(data.journal)
    metadata = analyze_journal(data.journal)
    save(user_id, prompt, data.journal, advice, metadata)
    return {"advice": advice}

@app.get("/dashboard")
def dashboard_data(user_id: str = Depends(get_current_user)):
    data = get_dashboard_data(user_id)
    insights = generate_insights(data["entries_text"])
    
    return {
        "mood_trend": data["mood_trend"],
        "word_cloud_data": data["word_cloud_data"],
        "topic_distribution": data["topic_distribution"],
        "insights": insights
    }

'''def get_current_user():
    return "sayantan123"''' # Replace with a real user_id in your database


@app.get("/history")
def get_history(user_id: str = Depends(get_current_user)):
    #print("user id from ", user_id)
    return get_hist(user_id)

@app.delete("/history/{journal_id}")
def del_history(journal_id:str,user_id:str = Depends(get_current_user)):
    del_count = delete_journal(user_id,journal_id)
    if del_count  == 0:
        raise HTTPException(status_code=404, detail="Journal not found or unauthorized")
    return {"message":"Journal deleted successfully"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
