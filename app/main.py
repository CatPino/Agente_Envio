import os
import re
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from app.config import Config
from app.rag_pipeline import consultar_informacion_envios
from app.tools import guardar_registro_log

load_dotenv()

app = FastAPI(title="Agente de Logística ChileEnvia")

client = OpenAI(
    base_url=Config.GITHUB_BASE_URL,
    api_key=Config.GITHUB_TOKEN
)

# Memoria conversacional por sesión 

conversation_memory: dict[str, list] = {}

tools = {
    "consultar_informacion_envios": {
        "function": consultar_informacion_envios,
        "description": "Útil para consultar tarifas, tiempos de entrega y políticas de ChileEnvia.",
        "args": {"query": "la duda del usuario"}
    },
    "guardar_registro_log": {
        "function": guardar_registro_log,
        "description": "Útil para registrar acciones, pedidos o incidencias por escrito.",
        "args": {"texto": "el resumen de lo ocurrido para el log"}
    }
}


def create_system_prompt(tools_dict: dict) -> str:
    """
    Construye el system prompt del agente ReAct.
    Incluye instrucciones de memoria, planificación y formato de razonamiento.
    """
    prompt = """Eres un agente experto de ChileEnvia con capacidad de memoria y planificación.
Tu objetivo es ayudar a los usuarios con sus envíos de forma precisa y contextual.

IMPORTANTE - MEMORIA:
- Tienes acceso al historial completo de la conversación.
- Usa el contexto previo para dar respuestas coherentes y personalizadas.
- Si el usuario hace referencia a algo mencionado antes, úsalo sin pedir que lo repita.

IMPORTANTE - PLANIFICACIÓN:
- Antes de actuar, analiza si necesitas una o varias herramientas.
- Si la pregunta es compleja, descompónla en pasos.
- Si ya obtuviste información relevante en este turno, no la busques de nuevo.

Debes seguir este formato de razonamiento:

Thought: Razonamiento sobre qué hacer a continuación y por qué.
Action: {"tool": "nombre_herramienta", "args": {"arg_name": "valor"}}
Observation: Resultado de la herramienta.
... (repite Thought/Action/Observation si es necesario)
Final Answer: Respuesta final clara y completa para el usuario.

Herramientas disponibles:
"""
    for name, details in tools_dict.items():
        prompt += f"\n- {name}: {details['description']} Args: {details['args']}"
    return prompt


class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"  # Identificador de sesión para memoria


class ChatResponse(BaseModel):
    respuesta: str
    session_id: str
    pasos: int  # Cuántos pasos de razonamiento tomó el agente


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id
    system_prompt = create_system_prompt(tools)

    if session_id not in conversation_memory:
        conversation_memory[session_id] = []

    messages = (
        [{"role": "system", "content": system_prompt}]
        + conversation_memory[session_id]
        + [{"role": "user", "content": request.question}]
    )

    pasos = 0

    for _ in range(5):
        pasos += 1
        response = client.chat.completions.create(
            model=Config.MODEL_NAME,
            messages=messages,
            temperature=Config.TEMPERATURE,
            max_tokens=800
        )

        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})

        if "Final Answer:" in content:
            respuesta_final = content.split("Final Answer:")[-1].strip()

            # Log automático de cada interacción
            guardar_registro_log({
                "texto": f"[session: {session_id}] Pregunta: {request.question} | Respuesta: {respuesta_final[:100]}..."
            })

            # Guardar en memoria: pregunta del usuario + respuesta final del agente
            conversation_memory[session_id].append(
                {"role": "user", "content": request.question}
            )
            conversation_memory[session_id].append(
                {"role": "assistant", "content": respuesta_final}
            )

            # Limitar memoria a últimas 10 interacciones (5 pares)
            if len(conversation_memory[session_id]) > 20:
                conversation_memory[session_id] = conversation_memory[session_id][-20:]

            return ChatResponse(
                respuesta=respuesta_final,
                session_id=session_id,
                pasos=pasos
            )

        action_match = re.search(r"Action:\s*(\{[^{}]+\})", content)
        if action_match:
            try:
                action_data = json.loads(action_match.group(1).strip())
                tool_name = action_data["tool"]
                tool_args = action_data["args"]

                if tool_name in tools:
                    observation = tools[tool_name]["function"](tool_args)
                else:
                    observation = f"Herramienta '{tool_name}' no encontrada."

                messages.append({"role": "user", "content": f"Observation: {observation}"})

            except Exception as e:
                messages.append({"role": "user", "content": f"Observation: Error - {str(e)}"})

    return ChatResponse(
        respuesta="Lo siento, no pude procesar tu consulta en el tiempo esperado. Por favor intenta de nuevo.",
        session_id=session_id,
        pasos=pasos
    )


@app.delete("/memory/{session_id}")
async def clear_memory(session_id: str):
    """Endpoint para limpiar la memoria de una sesión específica."""
    if session_id in conversation_memory:
        del conversation_memory[session_id]
        return {"mensaje": f"Memoria de sesión '{session_id}' eliminada correctamente."}
    return {"mensaje": f"No se encontró sesión '{session_id}'."}


@app.get("/memory/{session_id}")
async def get_memory(session_id: str):
    """Endpoint para inspeccionar el historial de una sesión."""
    historial = conversation_memory.get(session_id, [])
    return {"session_id": session_id, "turnos": len(historial) // 2, "historial": historial}


@app.get("/")
async def root():
    return {"mensaje": "Agente ChileEnvia activo", "endpoints": ["/chat", "/memory/{session_id}"]}