import os
import re
import pandas as pd
import requests
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from app.gemini_auth import get_google_oauth_token  # Import helper

load_dotenv()
SERVICE_ACCOUNT_PATH = "service-account.json"
GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"
# To use Flash model instead, uncomment and change the model:
# GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-data-agent-blond.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "AI Data Agent backend running"}

@app.post("/upload/")
async def upload_excel(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    try:
        df = pd.read_excel(file_location)
        columns = list(df.columns)
        preview = df.head(5).to_dict(orient="records")
    except Exception as e:
        print("Excel loading error:", e)
        return JSONResponse(status_code=400, content={"error": str(e)})
    return {
        "filename": file.filename,
        "detail": "File uploaded successfully",
        "columns": columns,
        "preview": preview,
    }

class QuestionRequest(BaseModel):
    filename: str
    question: str

def parse_and_execute_query(df: pd.DataFrame, question: str):
    # (Your classic query regex logic can go here)
    return "Sorry, I can't answer that question yet."

def extract_python_code(raw):
    """
    Robustly extract Python code from markdown/LLM result blocks.
    Ignores lines starting with triple backticks or a 'python' hint.
    """
    lines = raw.strip().split('\n')
    code_lines = [
        line for line in lines
        if not line.strip().startswith("```") and line.strip().lower() != "python"
    ]
    return '\n'.join(code_lines).strip()


@app.post("/question/")
async def answer_question(req: QuestionRequest):
    file_location = os.path.join(UPLOAD_DIR, req.filename)
    if not os.path.exists(file_location):
        return JSONResponse(status_code=400, content={"error": "File not found"})
    try:
        df = pd.read_excel(file_location)
        answer = parse_and_execute_query(df, req.question)
        return {"answer": answer}
    except Exception as e:
        print("Question processing error:", e)
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/llm_question/")
async def llm_answer_question(req: QuestionRequest):
    file_location = os.path.join(UPLOAD_DIR, req.filename)
    if not os.path.exists(file_location):
        return JSONResponse(status_code=400, content={"error": "File not found"})
    try:
        df = pd.read_excel(file_location)
        columns = list(df.columns)
        sample_data = df.head(5).to_dict(orient="records")

        prompt = f"""
You are a helpful Python data assistant. Given a pandas DataFrame called df with columns: {columns}, answer the following question:
{req.question}
Provide Python code that computes the answer and assigns it to a variable called result. Use only df.
Here is sample data: {sample_data}
Python code:
"""

        token = get_google_oauth_token(SERVICE_ACCOUNT_PATH)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        json_body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        r = requests.post(GEMINI_CHAT_URL, headers=headers, json=json_body)
        if r.status_code != 200:
            print("Gemini API error:", r.status_code, r.text)
            return JSONResponse(status_code=500, content={"error": f"Gemini API error: {r.text}"})
        response_json = r.json()
        raw_code = response_json["candidates"][0]["content"]["parts"][0]["text"]
        code_snippet = extract_python_code(raw_code)
        local_vars = {"df": df}
        try:
            exec(code_snippet, {}, local_vars)
            answer = local_vars.get("result", "No variable 'result' returned")
        except Exception as exec_err:
            answer = f"Code execution error: {exec_err}\nGenerated code:\n{code_snippet}"
        return {"answer": str(answer)}
    except Exception as e:
        print("LLM endpoint error:", e)
        return JSONResponse(status_code=400, content={"error": str(e)})
