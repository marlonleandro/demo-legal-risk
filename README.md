# Sistema de Análisis Legal con Ingeniería de Contexto

## Descripción del Caso

Este proyecto demuestra la aplicación de **Ingeniería de Contexto** en el análisis de documentación legal. El sistema permite a los usuarios cargar documentos legales, construir contexto relevante mediante técnicas de orquestación, y obtener respuestas precisas utilizando modelos de lenguaje (LLMs).

### Caso de Uso: Análisis de Contratos Legales

El sistema ayuda a analizar contratos, identificar cláusulas importantes, detectar riesgos potenciales y responder preguntas específicas sobre documentos legales.

## Arquitectura de la Aplicación

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFAZ STREAMLIT                        │
│  (Carga de documentos, configuración, visualización)        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              ORQUESTADOR DE CONTEXTO                         │
│  • Extracción de texto                                       │
│  • Segmentación de documentos                                │
│  • Identificación de secciones relevantes                    │
│  • Construcción de contexto jerárquico                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           CONSTRUCTOR DE PROMPTS                             │
│  • System prompt (rol y comportamiento)                      │
│  • Context prompt (documentos y metadatos)                   │
│  • User prompt (pregunta específica)                         │
│  • Few-shot examples (ejemplos de análisis)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 API LLM                                      │
│  • Anthropic Claude (recomendado)                            │
│  • OpenAI GPT                                                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              PROCESADOR DE RESPUESTA                         │
│  • Formateo de resultados                                    │
│  • Extracción de insights                                    │
│  • Visualización de hallazgos                                │
└─────────────────────────────────────────────────────────────┘
```

## Componentes de Ingeniería de Contexto

### 1. **Orquestación de Contexto**
- Extracción inteligente de información relevante
- Priorización de secciones según la consulta
- Gestión de límites de tokens

### 2. **Construcción de Contexto Jerárquico**
- Metadatos del documento
- Resumen ejecutivo
- Secciones específicas
- Cláusulas relevantes

### 3. **Técnicas Implementadas**
- **Chunking**: División inteligente de documentos largos
- **Retrieval**: Selección de fragmentos relevantes
- **Prompt Engineering**: Construcción de prompts efectivos
- **Few-shot Learning**: Ejemplos para guiar al modelo
- **Chain of Thought**: Razonamiento paso a paso

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. Crear archivo `.env` en la raíz del proyecto:

```env
ANTHROPIC_API_KEY=tu_api_key_aqui
OPENAI_API_KEY=tu_api_key_aqui
```

2. Configurar el proveedor de LLM preferido en la interfaz

## Uso

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

## Funcionalidades

1. **Carga de Documentos**: Soporta PDF y TXT
2. **Análisis Automático**: Identifica estructura y secciones clave
3. **Consultas Interactivas**: Haz preguntas sobre el documento
4. **Visualización de Ingeniería de Contexto**: Muestra paso a paso cómo se construye el contexto
5. **Comparación Con vs Sin Contexto**: Demuestra el impacto real de la optimización
6. **Métricas de Rendimiento**: Tokens, costos, velocidad
7. **Exportación de Resultados**: Historial de consultas

## Estructura del Proyecto

```
.
├── app.py                      # Aplicación principal Streamlit
├── context_engine.py           # Motor de orquestación de contexto
├── llm_client.py              # Cliente para APIs de LLM
├── document_processor.py       # Procesamiento de documentos
├── prompt_templates.py         # Templates de prompts
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno (no incluido)
├── README.md                   # Este archivo
└── examples/                   # Documentos de ejemplo
    └── contrato_ejemplo.txt
```

## Tecnologías

- **Streamlit**: Interfaz de usuario
- **Anthropic Claude / OpenAI GPT**: Modelos de lenguaje
- **PyPDF2**: Procesamiento de PDFs
- **Python-dotenv**: Gestión de variables de entorno
- **Tiktoken**: Conteo de tokens

## Ejemplos de Consultas

- "¿Cuáles son las obligaciones principales del contratante?"
- "Identifica cláusulas de terminación anticipada"
- "¿Qué riesgos legales detectas en este contrato?"
- "Resume las condiciones de pago"
- "¿Hay cláusulas de confidencialidad?"

## Licencia

MIT License
