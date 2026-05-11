# Agente de Logística ChileEnvia

Sistema de agente conversacional con memoria, RAG y arquitectura ReAct para gestión de consultas logísticas.

# Componentes y Orquestación

Centraliza las variables del sistema: credenciales, modelo, temperatura.
- Modelo: gpt-4 vía GitHub AI Inference
- Temperatura: 0.2 para respuestas precisas y reproducibles

Implementa Retrieval-Augmented Generation para fundamentar las respuestas del agente en datos reales de la empresa.

Implementa FAISS: Es una base vectorial en memoria, sin infraestructura adicional. Ideal para proyectos donde los datos no cambian frecuentemente.


# Arquitectura ReAct

El agente sigue un ciclo de razonamiento estructurado:

Thought:     → El agente analiza qué necesita hacer
Action:      → Selecciona y ejecuta una herramienta
Observation: → Recibe el resultado
    ...      → Repite si es necesario
Final Answer → Entrega respuesta al usuario

Esto implementa toma de decisiones adaptativa: el agente puede encadenar múltiples herramientas dependiendo de la complejidad de la consulta.

# Sistema de Memoria

La memoria se gestiona por session_id:

Cómo funciona:
- Cada sesión tiene su propio historial de mensajes
- Al construir cada request al LLM se incluye: [system] + [historial] + [nueva pregunta]
- Solo se guarda en memoria el par (pregunta_usuario, respuesta_final), no los pasos intermedios de razonamiento — esto mantiene el contexto limpio
- El historial se limita a 10 turnos (20 mensajes) para no superar el contexto del modelo

# Instalación y Ejecución
1. Clonar el repositorio
git clone https://github.com/CatPino/Agente_Envio
cd Agente_Envio

2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Instalar dependencias
pip install -r requirements.txt

4. Configurar variables de entorno (.env)
GITHUB_TOKEN=tu_token
GITHUB_BASE_URL=https://models.github.ai/inference
MODEL_NAME=gpt-4o

5. Iniciar servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Ejemplos de Uso

# Consulta simple
json
POST /chat
{
  "question": "¿Cuánto cuesta enviar de Santiago a Coquimbo?",
  "session_id": "cliente_001"
}
```

Consulta con contexto (memoria)
json
POST /chat
{
  "question": "¿Y si el paquete pesa más de 5kg?",
  "session_id": "cliente_001"
}
El agente recuerda que se estaba hablando de Coquimbo


Inspeccionar memoria de sesión
GET /memory/cliente_001

Limpiar memoria de sesión
DELETE /memory/cliente_001
