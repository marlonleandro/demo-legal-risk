"""
Aplicación Streamlit para demostración de Ingeniería de Contexto
en análisis de documentos legales
"""

import streamlit as st
import json
from context_engine import ContextEngine
from llm_client import LLMClient

# Configuración de la página
st.set_page_config(
    page_title="Análisis Legal con Ingeniería de Contexto",
    page_icon="⚖️",
    layout="wide"
)

# Inicializar session state
if 'context_engine' not in st.session_state:
    st.session_state.context_engine = None
if 'document_loaded' not in st.session_state:
    st.session_state.document_loaded = False
if 'document_info' not in st.session_state:
    st.session_state.document_info = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Título principal
st.title("⚖️ Sistema de Análisis Legal con Ingeniería de Contexto")
st.markdown("---")

# Sidebar - Configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selección de proveedor LLM
    provider = st.selectbox(
        "Proveedor de LLM",
        ["anthropic", "openai"],
        help="Selecciona el proveedor de modelo de lenguaje"
    )
    
    # Selección de modelo
    available_models = LLMClient.get_available_models(provider)
    model = st.selectbox(
        "Modelo",
        available_models,
        help="Selecciona el modelo específico a utilizar"
    )
    
    # Temperatura
    temperature = st.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controla la creatividad de las respuestas"
    )
    
    # Botón para inicializar
    if st.button("🔄 Inicializar Motor", type="primary"):
        try:
            st.session_state.context_engine = ContextEngine(
                llm_provider=provider,
                model=model
            )
            if st.session_state.context_engine.llm_client.is_configured():
                st.success("✅ Motor inicializado correctamente")
            else:
                st.error("❌ API key no configurada. Verifica tu archivo .env")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Información del sistema
    st.subheader("📊 Estado del Sistema")
    if st.session_state.context_engine:
        st.success("Motor: Activo")
        st.info(f"Proveedor: {provider}")
        st.info(f"Modelo: {model}")
    else:
        st.warning("Motor: No inicializado")
    
    if st.session_state.document_loaded:
        st.success("Documento: Cargado")
    else:
        st.info("Documento: No cargado")

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Cargar Documento",
    "🔍 Análisis Automático",
    "💬 Consultas Interactivas",
    "🎓 Ingeniería de Contexto",
    "⚖️ Comparación: Con vs Sin Contexto"
])

# Tab 1: Cargar Documento
with tab1:
    st.header("Carga de Documento Legal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Selecciona un documento (PDF o TXT)",
            type=['pdf', 'txt'],
            help="Carga un contrato o documento legal para analizar"
        )
        
        if uploaded_file and st.session_state.context_engine:
            if st.button("📥 Procesar Documento", type="primary"):
                with st.spinner("Procesando documento..."):
                    try:
                        file_type = "pdf" if uploaded_file.name.endswith('.pdf') else "txt"
                        doc_info = st.session_state.context_engine.load_document(
                            uploaded_file,
                            file_type
                        )
                        st.session_state.document_loaded = True
                        st.session_state.document_info = doc_info
                        st.success("✅ Documento procesado exitosamente")
                    except Exception as e:
                        st.error(f"Error al procesar: {str(e)}")
    
    with col2:
        if st.session_state.document_loaded and st.session_state.document_info:
            st.subheader("📋 Metadatos")
            metadata = st.session_state.document_info['metadata']
            st.write(f"**Tipo:** {metadata.get('type', 'N/A')}")
            st.write(f"**Fecha:** {metadata.get('date', 'N/A')}")
            st.write(f"**Secciones:** {metadata.get('sections_count', 0)}")
            st.write(f"**Tokens:** {st.session_state.document_info.get('token_count', 0)}")
            
            if metadata.get('parties'):
                st.write("**Partes:**")
                for party in metadata['parties']:
                    st.write(f"- {party}")
    
    # Mostrar preview del documento
    if st.session_state.document_loaded and st.session_state.document_info:
        st.subheader("👁️ Vista Previa del Documento")
        with st.expander("Ver contenido", expanded=False):
            st.text_area(
                "Contenido",
                st.session_state.document_info['text'][:3000] + "...",
                height=300,
                disabled=True
            )

# Tab 2: Análisis Automático
with tab2:
    st.header("Análisis Automático del Documento")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Primero debes cargar un documento en la pestaña 'Cargar Documento'")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Análisis Completo", type="primary"):
                with st.spinner("Analizando documento..."):
                    try:
                        response = st.session_state.context_engine.analyze_document(
                            temperature=temperature
                        )
                        st.subheader("Resultado del Análisis")
                        st.markdown(response['content'])
                        
                        with st.expander("📈 Información de Uso"):
                            st.json(response['usage'])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("⚠️ Análisis de Riesgos", type="primary"):
                with st.spinner("Analizando riesgos..."):
                    try:
                        response = st.session_state.context_engine.analyze_risks(
                            temperature=temperature
                        )
                        st.subheader("Análisis de Riesgos")
                        st.markdown(response['content'])
                        
                        with st.expander("📈 Información de Uso"):
                            st.json(response['usage'])
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Tab 3: Consultas Interactivas
with tab3:
    st.header("Consultas Interactivas sobre el Documento")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Primero debes cargar un documento en la pestaña 'Cargar Documento'")
    else:
        # Ejemplos de consultas
        st.subheader("💡 Ejemplos de Consultas")
        example_queries = [
            "¿Cuáles son las obligaciones principales del contratante?",
            "Identifica las cláusulas de terminación anticipada",
            "¿Qué riesgos legales detectas en este contrato?",
            "Resume las condiciones de pago",
            "¿Hay cláusulas de confidencialidad?"
        ]
        
        cols = st.columns(3)
        for i, query in enumerate(example_queries):
            with cols[i % 3]:
                if st.button(query, key=f"example_{i}"):
                    st.session_state.current_query = query
        
        st.markdown("---")
        
        # Input de consulta
        query = st.text_area(
            "Tu pregunta:",
            value=st.session_state.get('current_query', ''),
            height=100,
            placeholder="Escribe tu pregunta sobre el documento..."
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            use_relevant = st.checkbox(
                "Usar solo secciones relevantes",
                value=True,
                help="Optimiza el contexto usando solo las secciones más relevantes"
            )
        
        with col2:
            if st.button("🚀 Consultar", type="primary"):
                if query:
                    with st.spinner("Generando respuesta..."):
                        try:
                            response = st.session_state.context_engine.query_document(
                                query=query,
                                use_relevant_sections=use_relevant,
                                temperature=temperature
                            )
                            
                            # Agregar a historial
                            st.session_state.chat_history.append({
                                'query': query,
                                'response': response['content'],
                                'usage': response['usage']
                            })
                            
                            # Mostrar respuesta
                            st.subheader("💬 Respuesta")
                            st.markdown(response['content'])
                            
                            # Información de contexto
                            with st.expander("🔍 Información de Contexto"):
                                st.json(response.get('context_info', {}))
                            
                            with st.expander("📈 Uso de Tokens"):
                                st.json(response['usage'])
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                else:
                    st.warning("Por favor escribe una pregunta")
        
        # Historial de consultas
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("📜 Historial de Consultas")
            for i, item in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"Consulta {len(st.session_state.chat_history) - i}: {item['query'][:50]}..."):
                    st.markdown(f"**Pregunta:** {item['query']}")
                    st.markdown(f"**Respuesta:** {item['response']}")

# Tab 4: Visualización de Contexto
with tab4:
    st.header("🎓 Ingeniería de Contexto en Acción")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Primero debes cargar un documento")
    else:
        st.markdown("""
        Esta sección demuestra **paso a paso** cómo funciona la Ingeniería de Contexto,
        mostrando cada componente y técnica aplicada.
        """)
        
        # Input para query de ejemplo
        viz_query = st.text_input(
            "Escribe una consulta para ver cómo se construye el contexto:",
            placeholder="Ej: ¿Cuáles son las obligaciones del contratante?"
        )
        
        if st.button("🔍 Ver Ingeniería de Contexto", type="primary"):
            st.markdown("---")
            
            # PASO 1: Documento Original
            st.subheader("📄 PASO 1: Documento Original")
            st.info("El documento completo tiene demasiada información. Necesitamos optimizar el contexto.")
            
            viz_data = st.session_state.context_engine.get_context_visualization(viz_query)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Tokens Totales", viz_data['total_tokens'])
            with col2:
                st.metric("📑 Secciones", viz_data['total_sections'])
            with col3:
                st.metric("💰 Costo Estimado", f"${viz_data['total_tokens'] * 0.000003:.4f}")
            
            st.markdown("---")
            
            # PASO 2: Extracción de Metadatos
            st.subheader("🔍 PASO 2: Extracción de Metadatos")
            st.success("✅ Técnica: **Metadata Extraction** - Extraemos información estructurada del documento")
            
            metadata = viz_data['document_metadata']
            col1, col2 = st.columns(2)
            with col1:
                st.json({
                    "Tipo de Documento": metadata.get('type', 'N/A'),
                    "Fecha": metadata.get('date', 'N/A'),
                    "Secciones": metadata.get('sections_count', 0)
                })
            with col2:
                if metadata.get('parties'):
                    st.write("**Partes Identificadas:**")
                    for party in metadata['parties']:
                        st.write(f"• {party}")
            
            st.markdown("---")
            
            # PASO 3: Segmentación (Chunking)
            st.subheader("✂️ PASO 3: Segmentación del Documento (Chunking)")
            st.success("✅ Técnica: **Semantic Chunking** - Dividimos el documento en secciones lógicas")
            
            st.write(f"El documento se dividió en **{viz_data['total_sections']} secciones** basándose en:")
            st.write("• Cláusulas y artículos")
            st.write("• Títulos y subtítulos")
            st.write("• Estructura semántica")
            
            with st.expander("Ver todas las secciones identificadas"):
                for i, section in enumerate(viz_data['sections'][:10], 1):
                    st.write(f"**{i}. {section['title']}** ({section['tokens']} tokens)")
            
            st.markdown("---")
            
            # PASO 4: Retrieval (si hay query)
            if viz_query and 'relevant_sections' in viz_data:
                st.subheader("🎯 PASO 4: Recuperación de Secciones Relevantes (Retrieval)")
                st.success("✅ Técnica: **Keyword-based Retrieval** - Seleccionamos solo las secciones relevantes")
                
                st.write(f"**Consulta:** {viz_query}")
                st.write(f"**Resultado:** {len(viz_data['relevant_sections'])} de {viz_data['total_sections']} secciones son relevantes")
                
                # Calcular reducción de tokens
                relevant_tokens = sum(s['tokens'] for s in viz_data['relevant_sections'])
                reduction = ((viz_data['total_tokens'] - relevant_tokens) / viz_data['total_tokens']) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tokens Originales", viz_data['total_tokens'])
                with col2:
                    st.metric("Tokens Relevantes", relevant_tokens, delta=f"-{reduction:.1f}%")
                with col3:
                    st.metric("Ahorro de Costo", f"${(viz_data['total_tokens'] - relevant_tokens) * 0.000003:.4f}")
                
                st.write("**Secciones seleccionadas:**")
                for i, section in enumerate(viz_data['relevant_sections'], 1):
                    with st.expander(f"✓ Sección {i}: {section['title']}"):
                        st.write(section['preview'])
                        st.caption(f"Tokens: {section['tokens']}")
                
                st.markdown("---")
            
            # PASO 5: Construcción del Prompt
            st.subheader("🏗️ PASO 5: Construcción del Prompt (Prompt Engineering)")
            st.success("✅ Técnicas: **System Prompt + Context + Few-Shot Examples**")
            
            tab_system, tab_context, tab_fewshot = st.tabs(["System Prompt", "Context Prompt", "Few-Shot Examples"])
            
            with tab_system:
                st.write("**Propósito:** Define el rol y comportamiento del modelo")
                st.code("""Eres un asistente legal experto especializado en análisis 
de contratos y documentos legales.

Tu rol es:
- Analizar documentos legales con precisión y detalle
- Identificar cláusulas importantes, riesgos y obligaciones
- Proporcionar respuestas claras y fundamentadas
- Citar secciones específicas del documento
- Mantener un tono profesional y objetivo""", language="text")
            
            with tab_context:
                st.write("**Propósito:** Proporciona el contexto específico del documento")
                if viz_query and 'relevant_sections' in viz_data:
                    st.code(f"""INFORMACIÓN DEL DOCUMENTO:
- Tipo: {metadata.get('type', 'N/A')}
- Fecha: {metadata.get('date', 'N/A')}
- Secciones relevantes: {len(viz_data['relevant_sections'])}

SECCIONES RELEVANTES:
{viz_data['relevant_sections'][0]['title']}
{viz_data['relevant_sections'][0]['preview'][:200]}...

PREGUNTA DEL USUARIO:
{viz_query}""", language="text")
                else:
                    st.info("Escribe una consulta arriba para ver cómo se construye el contexto")
            
            with tab_fewshot:
                st.write("**Propósito:** Ejemplos que guían el formato de respuesta")
                st.code("""Pregunta: "¿Cuáles son las obligaciones del contratante?"
Respuesta: "Según el documento, las obligaciones principales son:
1. [Obligación 1 con referencia a la sección]
2. [Obligación 2 con referencia a la sección]
Estas obligaciones están detalladas en la Cláusula X."

Pregunta: "¿Hay cláusulas de terminación?"
Respuesta: "Sí, el contrato incluye:
- Terminación por causa justificada: [detalles]
- Terminación anticipada: [detalles]
Referencia: Cláusula Y, Sección Z." """, language="text")
            
            st.markdown("---")
            
            # PASO 6: Optimización
            st.subheader("⚡ PASO 6: Optimización del Contexto")
            st.success("✅ Técnicas aplicadas para optimizar costo y rendimiento")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Técnicas de Optimización:**")
                st.write("✓ Chunking semántico")
                st.write("✓ Retrieval selectivo")
                st.write("✓ Metadata extraction")
                st.write("✓ Token counting")
                st.write("✓ Context windowing")
            
            with col2:
                st.write("**Beneficios:**")
                st.write("• Reducción de costos")
                st.write("• Respuestas más rápidas")
                st.write("• Mayor precisión")
                st.write("• Mejor relevancia")
                st.write("• Escalabilidad")
            
            st.markdown("---")
            
            # PASO 7: Resultado Final
            st.subheader("🎯 PASO 7: Resultado Final")
            
            if viz_query:
                st.info("💡 **Ahora haz clic en la pestaña 'Consultas Interactivas' para ver la respuesta del LLM con este contexto optimizado**")
            else:
                st.warning("Escribe una consulta arriba para completar el flujo")
            
            # Resumen de técnicas
            st.markdown("---")
            st.subheader("📚 Resumen de Técnicas de Ingeniería de Contexto")
            
            techniques = {
                "Metadata Extraction": "Extracción de información estructurada del documento",
                "Semantic Chunking": "División inteligente del documento en secciones lógicas",
                "Keyword Retrieval": "Selección de fragmentos relevantes basada en la consulta",
                "Prompt Engineering": "Construcción de prompts efectivos con system/context/user",
                "Few-Shot Learning": "Ejemplos que guían el formato de respuesta",
                "Token Optimization": "Gestión eficiente de tokens para reducir costos",
                "Context Windowing": "Limitación del contexto a información relevante"
            }
            
            for technique, description in techniques.items():
                st.write(f"**{technique}:** {description}")

# Tab 5: Comparación Con vs Sin Contexto
with tab5:
    st.header("⚖️ Comparación: Con vs Sin Ingeniería de Contexto")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Primero debes cargar un documento")
    else:
        st.markdown("""
        Esta sección demuestra el **impacto real** de aplicar técnicas de ingeniería de contexto,
        comparando resultados con y sin optimización.
        """)
        
        comparison_query = st.text_area(
            "Escribe tu consulta:",
            placeholder="Ej: ¿Cuáles son las obligaciones del proveedor?",
            height=80
        )
        
        if st.button("🔬 Ejecutar Comparación", type="primary"):
            if comparison_query:
                col1, col2 = st.columns(2)
                
                # Columna 1: SIN Ingeniería de Contexto
                with col1:
                    st.subheader("❌ Sin Ingeniería de Contexto")
                    st.caption("Enviando documento completo sin optimización")
                    
                    with st.spinner("Procesando..."):
                        try:
                            start_time = __import__('time').time()
                            response_without = st.session_state.context_engine.query_document(
                                query=comparison_query,
                                use_relevant_sections=False,
                                temperature=temperature
                            )
                            time_without = __import__('time').time() - start_time
                            
                            st.info(f"⏱️ Tiempo: {time_without:.2f}s")
                            st.info(f"🎫 Tokens entrada: {response_without['usage']['input_tokens']}")
                            st.info(f"💰 Costo: ${response_without['usage']['input_tokens'] * 0.000003:.4f}")
                            
                            st.markdown("**Respuesta:**")
                            st.markdown(response_without['content'])
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Columna 2: CON Ingeniería de Contexto
                with col2:
                    st.subheader("✅ Con Ingeniería de Contexto")
                    st.caption("Usando retrieval, chunking y optimización")
                    
                    with st.spinner("Procesando..."):
                        try:
                            start_time = __import__('time').time()
                            response_with = st.session_state.context_engine.query_document(
                                query=comparison_query,
                                use_relevant_sections=True,
                                temperature=temperature
                            )
                            time_with = __import__('time').time() - start_time
                            
                            st.success(f"⏱️ Tiempo: {time_with:.2f}s")
                            st.success(f"🎫 Tokens entrada: {response_with['usage']['input_tokens']}")
                            st.success(f"💰 Costo: ${response_with['usage']['input_tokens'] * 0.000003:.4f}")
                            
                            st.markdown("**Respuesta:**")
                            st.markdown(response_with['content'])
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                
                # Análisis comparativo
                st.markdown("---")
                st.subheader("📊 Análisis Comparativo")
                
                try:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        token_reduction = ((response_without['usage']['input_tokens'] - 
                                          response_with['usage']['input_tokens']) / 
                                         response_without['usage']['input_tokens'] * 100)
                        st.metric(
                            "Reducción de Tokens",
                            f"{token_reduction:.1f}%",
                            delta=f"-{response_without['usage']['input_tokens'] - response_with['usage']['input_tokens']}"
                        )
                    
                    with col2:
                        time_improvement = ((time_without - time_with) / time_without * 100)
                        st.metric(
                            "Mejora en Velocidad",
                            f"{time_improvement:.1f}%",
                            delta=f"-{time_without - time_with:.2f}s"
                        )
                    
                    with col3:
                        cost_without = response_without['usage']['input_tokens'] * 0.000003
                        cost_with = response_with['usage']['input_tokens'] * 0.000003
                        cost_savings = ((cost_without - cost_with) / cost_without * 100)
                        st.metric(
                            "Ahorro de Costo",
                            f"{cost_savings:.1f}%",
                            delta=f"-${cost_without - cost_with:.4f}"
                        )
                    
                    with col4:
                        # Proyección a escala
                        queries_per_day = 1000
                        monthly_savings = (cost_without - cost_with) * queries_per_day * 30
                        st.metric(
                            "Ahorro Mensual*",
                            f"${monthly_savings:.2f}",
                            help="*Proyección con 1000 consultas/día"
                        )
                    
                    # Insights
                    st.markdown("---")
                    st.subheader("💡 Insights")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Ventajas de la Ingeniería de Contexto:**")
                        st.write("✓ Menor consumo de tokens")
                        st.write("✓ Respuestas más rápidas")
                        st.write("✓ Reducción significativa de costos")
                        st.write("✓ Mayor precisión (contexto relevante)")
                        st.write("✓ Escalabilidad mejorada")
                    
                    with col2:
                        st.markdown("**Cuándo aplicar cada enfoque:**")
                        st.write("**Sin optimización:** Documentos cortos (<2000 tokens)")
                        st.write("**Con optimización:** Documentos largos, alta frecuencia de consultas")
                        st.write("**Híbrido:** Análisis inicial sin optimización, consultas específicas con optimización")
                
                except Exception as e:
                    st.warning("No se pudo generar el análisis comparativo")
            else:
                st.warning("Por favor escribe una consulta")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Sistema de Análisis Legal con Ingeniería de Contexto</p>
    <p>Demostrando técnicas de orquestación de contexto, chunking, retrieval y prompt engineering</p>
</div>
""", unsafe_allow_html=True)
