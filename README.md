Sistema ChileEnvia:
Este proyecto implementa un asistente de inteligencia artificial basado en la arquitectura RAG (Retrieval-Augmented Generation) para resolver consultas sobre tarifas, políticas y tiempos de entrega de la empresa de envios.

Características y Cumplimiento de Indicadores (IL)
El sistema ha sido diseñado siguiendo los estándares de arquitectura de IA moderna:

IL 1.1 (Configuración de Modelos): Uso de gpt-4o con parámetros optimizados (temperature=0.2) para garantizar respuestas precisas y evitar alucinaciones en datos críticos.

IL 1.2 (Flujos RAG con Múltiples Fuentes): Integración de datos internos desde archivos de texto (tarifas.txt, politica.txt, tiempo.txt) mediante un cargador de directorios dinámico.

IL 1.3 (Arquitectura de Solución): Implementación de una base de datos vectorial con FAISS y una cadena de recuperación de información con LangChain (RetrievalQA).

IL 1.4 (Documentación y Trazabilidad): Respuestas que indican las fuentes consultadas para asegurar transparencia en la información entregada al usuario.

Requisitos e Instalación
Para ejecutar este proyecto en un entorno local o Codespaces, sigue estos pasos:

1. Clonar el repositorio y configurar el entorno
Bash
git clone <url-de-tu-repo>
cd ProyectoEnvios
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instalar dependencias
Bash
pip install -r requirements.txt

5. Variables de Entorno
Crea un archivo .env en la raíz con tus credenciales:

Fragmento de código
GITHUB_TOKEN=tu_token_aqui

GITHUB_BASE_URL=https://models.github.ai/inference

MODEL_NAME=gpt-4o-mini

Ejecución del Servidor
Inicia la API con Uvicorn:
Bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Cómo probar la API
Una vez que el servidor esté corriendo, puedes enviar una solicitud POST a la ruta /chat.

Endpoint: (URL publica de codespace)/chat 

Cuerpo de la petición (JSON):

JSON
{
  "question": "¿cuanto sale un envio de santiago a la region de coquimbo?"
}
