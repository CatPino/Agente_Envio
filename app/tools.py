import datetime
import json
import os

LOG_PATH = "log_operaciones.jsonl"

def guardar_registro_log(args):
    texto = args.get("texto", "")
    entrada = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tipo": "log_manual",
        "texto": texto
    }
    _escribir_log(entrada)
    return "Registro guardado correctamente."

def registrar_metricas(session_id, pregunta, respuesta, latencia_ms, pasos, herramientas, error=None):
    entrada = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tipo": "interaccion",
        "session_id": session_id,
        "pregunta": pregunta,
        "respuesta": respuesta[:200],
        "latencia_ms": round(latencia_ms, 2),
        "pasos": pasos,
        "herramientas_usadas": herramientas,
        "exitoso": error is None,
        "error": error
    }
    _escribir_log(entrada)

def _escribir_log(entrada):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")