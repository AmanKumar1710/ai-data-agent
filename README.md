# AI Data Agent

An AI-powered web application to upload Excel files, preview data, ask questions about the data, and get smart Python-based answers using Google Gemini's Generative AI.

## Features

- Upload Excel `.xls` or `.xlsx` files
- Preview first 5 rows and column headers
- Ask natural language questions about your data
- Receive smart AI-generated Python code answers executed in backend
- Supports large context questions with Gemini 2.5 AI model

## Tech Stack

- Frontend: React.js  
- Backend: FastAPI (Python)  
- AI Integration: Google Gemini API (Generative Language API)  
- Authentication: Google Service Account OAuth 2.0  
- Deployment: Recommended free hosting on Vercel (frontend) and Render (backend)

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Cloud project with Generative Language API enabled
- Service account JSON key downloaded

### Backend Setup

1. Clone repo and navigate to `/backend`
2. Create a Python virtual environment  
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

text
3. Install dependencies  
pip install -r requirements.txt

text
4. Place your Google service account JSON file as `backend/service-account.json`
5. Set environment variables in `.env` if any (optional)
6. Run backend local server  
uvicorn app.main:app --reload

text

### Frontend Setup

1. Navigate to `/frontend`
2. Install dependencies  
npm install

text
3. Create `.env` file with backend URL  
REACT_APP_BACKEND_URL=http://localhost:8000

text
4. Run React frontend  
npm start

text

## Usage

1. Open the frontend app in your browser (default `http://localhost:3000`)
2. Upload an Excel file
3. Ask questions in natural language about your data
4. View AI-generated Python code answer and the result

## Deployment

- Deploy frontend on [Vercel](https://vercel.com)  
- Deploy backend on [Render](https://render.com) or [Railway](https://railway.app)  
- Configure environment variables and CORS for cross-domain requests
- Securely add your Google service account key and API credentials

## Notes

- The AI-generated code is executed in backend Python environment; ensure security when deploying publicly
- Supported Excel file types are `.xls` and `.xlsx`
- The Gemini model has a token limit; very large files/questions may be truncated
