import json
from pathlib import Path
from collections import Counter
import statistics

LOG_PATH = "log_operaciones.jsonl"

def cargar_logs():
    path = Path(LOG_PATH)
    if not path.exists():
        return []
    registros = []
    with open(path, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                try:
                    registros.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue
    return registros

def calcular_metricas():
    logs = cargar_logs()
    interacciones = [r for r in logs if r.get("tipo") == "interaccion"]

    if not interacciones:
        return {
            "total_interacciones": 0,
            "tasa_exito": 0,
            "tasa_error": 0,
            "latencia_promedio_ms": 0,
            "latencia_max_ms": 0,
            "latencia_min_ms": 0,
            "latencia_p95_ms": 0,
            "pasos_promedio": 0,
            "herramientas_frecuencia": {},
            "consistencia_nota": "Sin datos suficientes"
        }

    latencias = [r["latencia_ms"] for r in interacciones if "latencia_ms" in r]
    exitosos = [r for r in interacciones if r.get("exitoso")]
    errores = [r for r in interacciones if not r.get("exitoso")]

    todas_herramientas = []
    for r in interacciones:
        todas_herramientas.extend(r.get("herramientas_usadas", []))

    latencias_sorted = sorted(latencias)
    p95_index = int(len(latencias_sorted) * 0.95) if latencias_sorted else 0

    preguntas = [r.get("pregunta", "") for r in interacciones]
    preguntas_unicas = len(set(preguntas))
    consistencia = (
        f"{preguntas_unicas} preguntas únicas de {len(preguntas)} total "
        f"({round(preguntas_unicas/len(preguntas)*100)}% variabilidad)"
        if preguntas else "Sin datos"
    )

    return {
        "total_interacciones": len(interacciones),
        "tasa_exito": round(len(exitosos) / len(interacciones) * 100, 1),
        "tasa_error": round(len(errores) / len(interacciones) * 100, 1),
        "latencia_promedio_ms": round(statistics.mean(latencias), 1) if latencias else 0,
        "latencia_max_ms": round(max(latencias), 1) if latencias else 0,
        "latencia_min_ms": round(min(latencias), 1) if latencias else 0,
        "latencia_p95_ms": round(latencias_sorted[p95_index], 1) if latencias_sorted else 0,
        "pasos_promedio": round(
            statistics.mean([r["pasos"] for r in interacciones if "pasos" in r]), 2
        ) if interacciones else 0,
        "herramientas_frecuencia": dict(Counter(todas_herramientas)),
        "consistencia_nota": consistencia
    }

def analizar_logs_falla():
    """Identifica patrones de falla — cubre IL3.2."""
    logs = cargar_logs()
    interacciones = [r for r in logs if r.get("tipo") == "interaccion"]
    errores = [r for r in interacciones if not r.get("exitoso")]

    hallazgos = []
    if errores:
        hallazgos.append(f"Se detectaron {len(errores)} errores.")
        for e in errores[:5]:
            hallazgos.append(f"  · [{e.get('timestamp','')}] session={e.get('session_id','')} — {e.get('error','sin detalle')}")

    lentas = [r for r in interacciones if r.get("latencia_ms", 0) > 5000]
    if lentas:
        hallazgos.append(f"{len(lentas)} respuestas con latencia > 5s (posible cuello de botella en LLM o RAG).")

    alto_pasos = [r for r in interacciones if r.get("pasos", 0) >= 5]
    if alto_pasos:
        hallazgos.append(f"{len(alto_pasos)} consultas alcanzaron el límite de pasos (5). Posible prompt ambiguo o herramienta no encontrada.")

    return hallazgos if hallazgos else ["Sin fallas detectadas en el log actual."]