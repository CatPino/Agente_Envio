import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from app.prompts import SYSTEM_PROMPT
from app.config import Config

load_dotenv()
app = FastAPI(title="Sistema de Logística con RAG")

client = OpenAI(
    base_url=Config.GITHUB_BASE_URL,
    api_key=Config.GITHUB_TOKEN
)

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: ChatRequest):
    from app.rag_pipeline import ejecutar_pipeline_rag
    
    respuesta_ia = ejecutar_pipeline_rag(request.question)
    
    return {
        "respuesta": respuesta_ia,
        "fuentes_consultadas": "Información interna de ChileEnvia (tarifas, políticas y tiempos)"
    }