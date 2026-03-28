"""
Templates de prompts para ingeniería de contexto en análisis legal
"""

SYSTEM_PROMPT = """Eres un asistente legal experto especializado en análisis de contratos y documentos legales.

Tu rol es:
- Analizar documentos legales con precisión y detalle
- Identificar cláusulas importantes, riesgos y obligaciones
- Proporcionar respuestas claras y fundamentadas
- Citar secciones específicas del documento cuando sea relevante
- Mantener un tono profesional y objetivo

Siempre basa tus respuestas en el contenido del documento proporcionado."""

FEW_SHOT_EXAMPLES = """
Ejemplos de análisis:

Pregunta: "¿Cuáles son las obligaciones del contratante?"
Respuesta: "Según el documento, las obligaciones principales del contratante son:
1. [Obligación 1 con referencia a la sección]
2. [Obligación 2 con referencia a la sección]
Estas obligaciones están detalladas en la Cláusula X del contrato."

Pregunta: "¿Hay cláusulas de terminación?"
Respuesta: "Sí, el contrato incluye las siguientes condiciones de terminación:
- Terminación por causa justificada: [detalles]
- Terminación anticipada: [detalles]
- Período de notificación: [detalles]
Referencia: Cláusula Y, Sección Z."
"""

def build_context_prompt(document_metadata: dict, relevant_sections: list, query: str) -> str:
    """
    Construye el prompt de contexto con información del documento
    """
    context = f"""
INFORMACIÓN DEL DOCUMENTO:
- Tipo: {document_metadata.get('type', 'Documento Legal')}
- Título: {document_metadata.get('title', 'Sin título')}
- Fecha: {document_metadata.get('date', 'No especificada')}
- Número de secciones: {document_metadata.get('sections_count', 0)}

SECCIONES RELEVANTES DEL DOCUMENTO:
"""
    
    for i, section in enumerate(relevant_sections, 1):
        context += f"\n--- Sección {i} ---\n"
        context += f"Título: {section.get('title', 'Sin título')}\n"
        context += f"Contenido:\n{section.get('content', '')}\n"
    
    context += f"\n\nPREGUNTA DEL USUARIO:\n{query}"
    
    return context

def build_analysis_prompt(document_text: str) -> str:
    """
    Construye prompt para análisis inicial del documento
    """
    return f"""Analiza el siguiente documento legal y proporciona:

1. Resumen ejecutivo (2-3 párrafos)
2. Partes involucradas
3. Objeto del contrato
4. Obligaciones principales de cada parte
5. Condiciones de pago (si aplica)
6. Duración y terminación
7. Cláusulas importantes (confidencialidad, penalizaciones, etc.)
8. Riesgos potenciales identificados

DOCUMENTO:
{document_text}

Proporciona un análisis estructurado y profesional."""

def build_risk_analysis_prompt(document_text: str) -> str:
    """
    Construye prompt específico para análisis de riesgos
    """
    return f"""Realiza un análisis de riesgos del siguiente documento legal.

Identifica:
1. Riesgos legales (cláusulas ambiguas, falta de protecciones)
2. Riesgos financieros (penalizaciones, costos ocultos)
3. Riesgos operacionales (obligaciones difíciles de cumplir)
4. Cláusulas desfavorables
5. Recomendaciones de mitigación

Para cada riesgo, indica:
- Nivel de severidad (Alto/Medio/Bajo)
- Sección del documento donde se encuentra
- Impacto potencial
- Recomendación

DOCUMENTO:
{document_text}"""
