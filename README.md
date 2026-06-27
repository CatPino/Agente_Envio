Agente de Logística ChileEnvia
Sistema de agente conversacional con memoria, RAG y arquitectura ReAct para gestión de consultas logísticas. Implementa observabilidad completa con métricas en tiempo real y dashboard de monitoreo.

Arquitectura del sistema
```
app/
├── config.py          # Variables de entorno y configuración del modelo
├── main.py            # Servidor FastAPI + lógica del agente ReAct
├── metrics.py         # Cálculo de métricas de observabilidad (IL3.1 + IL3.2)
├── rag_pipeline.py    # Pipeline RAG con FAISS
└── tools.py           # Herramientas del agente + logging estructurado JSONL
base/
├── politica.txt       # Políticas de envío
├── tarifas.txt        # Tarifas por destino y peso
└── tiempo.txt         # Tiempos de entrega por región
dashboard.py           # Dashboard Streamlit de monitoreo
log_operaciones.jsonl  # Registro estructurado de interacciones
```

Componentes principales
Configuración (config.py)
Centraliza las variables del sistema: credenciales, modelo y temperatura.

Modelo: gpt-4o vía GitHub AI Inference
Temperatura: 0.2 para respuestas precisas y reproducibles

RAG — Retrieval-Augmented Generation (rag_pipeline.py)
Fundamenta las respuestas del agente en datos reales de la empresa usando FAISS como base vectorial en memoria, sin infraestructura adicional. Ideal para proyectos donde los datos no cambian frecuentemente.
Arquitectura ReAct (main.py)
El agente sigue un ciclo de razonamiento estructurado:
Thought:      → El agente analiza qué necesita hacer
Action:       → Selecciona y ejecuta una herramienta
Observation:  → Recibe el resultado
...           → Repite si es necesario (máximo 5 pasos)
Final Answer  → Entrega respuesta al usuario
Esto implementa toma de decisiones adaptativa: el agente puede encadenar múltiples herramientas dependiendo de la complejidad de la consulta.
Sistema de memoria (main.py)
La memoria se gestiona por session_id:

Cada sesión tiene su propio historial de mensajes
Cada request al LLM incluye: [system] + [historial] + [nueva pregunta]
Solo se guarda el par (pregunta_usuario, respuesta_final), no los pasos intermedios — mantiene el contexto limpio
El historial se limita a 10 turnos (20 mensajes) para no superar el contexto del modelo

Herramientas disponibles
HerramientaDescripciónconsultar_informacion_enviosConsulta tarifas, tiempos y políticas via RAGguardar_registro_logRegistra acciones e incidencias en el log
Observabilidad y métricas (metrics.py + tools.py)
Cada interacción se registra automáticamente en log_operaciones.jsonl con las siguientes métricas:
MétricaDescripciónLatencia (ms)Tiempo total de respuesta del agenteTasa de éxito (%)Proporción de interacciones sin erroresPasos de razonamientoIteraciones Thought/Action/Observation por respuestaFrecuencia de herramientasConteo de llamadas a cada herramientaLatencia P95Percentil 95 — detecta cuellos de botellaConsistenciaVariabilidad de preguntas únicas vs. total

Instalación y ejecución
1. Clonar el repositorio
git clone https://github.com/CatPino/Agente_Envio
cd Agente_Envio
2. Crear entorno virtual
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
3. Instalar dependencias
pip install -r requirements.txt
pip install streamlit plotly
4. Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto:
GITHUB_TOKEN=tu_token
GITHUB_BASE_URL=https://models.github.ai/inference
MODEL_NAME=gpt-4o
5. Iniciar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
6. Iniciar el dashboard de monitoreo
En una segunda terminal:
streamlit run dashboard.py
El dashboard queda disponible en http://localhost:8501

Endpoints disponibles
MétodoEndpointDescripciónPOST/chatEnviar consulta al agenteGET/memory/{session_id}Inspeccionar historial de sesiónDELETE/memory/{session_id}Limpiar memoria de sesiónGET/metricasVer métricas de observabilidadGET/trazabilidadVer análisis de logs y fallas

Ejemplos de uso
Consulta simple
POST /chat
{
  "question": "¿Cuánto cuesta enviar de Santiago a Coquimbo?",
  "session_id": "cliente_001"
}
Consulta con contexto (memoria)
POST /chat
{
  "question": "¿Y si el paquete pesa más de 5kg?",
  "session_id": "cliente_001"
}

El agente recuerda que se estaba hablando de Coquimbo.
Inspeccionar memoria de sesión
GET /memory/cliente_001
Limpiar memoria de sesión
DELETE /memory/cliente_001
Ver métricas en tiempo real
GET /metricas
Ver análisis de trazabilidad
GET /trazabilidad

Stack tecnológico
ComponenteTecnologíaServidorFastAPI + UvicornModelo de lenguajeGPT-4o vía GitHub ModelsRAG / EmbeddingsLangChain + FAISS + OpenAI EmbeddingsPatrón de agenteReAct (Reasoning + Acting)LoggingJSONL estructuradoDashboardStreamlit + Plotly
