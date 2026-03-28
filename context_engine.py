"""
Motor de orquestación de contexto para ingeniería de contexto
"""

from typing import Dict, List, Optional
from document_processor import DocumentProcessor
from llm_client import LLMClient
from prompt_templates import (
    SYSTEM_PROMPT,
    FEW_SHOT_EXAMPLES,
    build_context_prompt,
    build_analysis_prompt,
    build_risk_analysis_prompt
)

class ContextEngine:
    """
    Orquesta la construcción de contexto y la interacción con LLMs
    """
    
    def __init__(self, llm_provider: str = "anthropic", model: str = None):
        self.doc_processor = DocumentProcessor()
        self.llm_client = LLMClient(provider=llm_provider, model=model)
        self.current_document = None
        self.document_metadata = None
        self.document_sections = None
    
    def load_document(self, file, file_type: str) -> Dict:
        """
        Carga y procesa un documento
        """
        # Extraer texto según tipo
        if file_type == "pdf":
            text = self.doc_processor.extract_text_from_pdf(file)
        else:
            text = self.doc_processor.extract_text_from_txt(file)
        
        # Procesar documento
        self.current_document = text
        self.document_metadata = self.doc_processor.extract_metadata(text)
        self.document_sections = self.doc_processor.identify_sections(text)
        
        # Agregar conteo de secciones a metadata
        self.document_metadata['sections_count'] = len(self.document_sections)
        
        return {
            'text': text,
            'metadata': self.document_metadata,
            'sections': self.document_sections,
            'token_count': self.llm_client.count_tokens(text)
        }
    
    def analyze_document(self, temperature: float = 0.7) -> Dict:
        """
        Realiza un análisis completo del documento
        """
        if not self.current_document:
            raise Exception("No hay documento cargado")
        
        # Construir prompt de análisis
        analysis_prompt = build_analysis_prompt(self.current_document)
        
        # Generar análisis
        response = self.llm_client.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=analysis_prompt,
            temperature=temperature,
            max_tokens=3000
        )
        
        return response
    
    def analyze_risks(self, temperature: float = 0.7) -> Dict:
        """
        Realiza análisis de riesgos del documento
        """
        if not self.current_document:
            raise Exception("No hay documento cargado")
        
        # Construir prompt de análisis de riesgos
        risk_prompt = build_risk_analysis_prompt(self.current_document)
        
        # Generar análisis
        response = self.llm_client.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=risk_prompt,
            temperature=temperature,
            max_tokens=3000
        )
        
        return response
    
    def query_document(
        self,
        query: str,
        use_relevant_sections: bool = True,
        temperature: float = 0.7
    ) -> Dict:
        """
        Responde una pregunta sobre el documento usando contexto orquestado
        """
        if not self.current_document:
            raise Exception("No hay documento cargado")
        
        # Construir contexto
        if use_relevant_sections and self.document_sections:
            # Encontrar secciones relevantes
            relevant_sections = self.doc_processor.find_relevant_sections(
                self.document_sections,
                query,
                top_k=3
            )
            
            # Si no hay secciones relevantes, usar todo el documento
            if not relevant_sections:
                relevant_sections = self.document_sections[:3]
            
            context_prompt = build_context_prompt(
                self.document_metadata,
                relevant_sections,
                query
            )
        else:
            # Usar documento completo
            context_prompt = f"""
DOCUMENTO COMPLETO:
{self.current_document}

PREGUNTA DEL USUARIO:
{query}
"""
        
        # Agregar ejemplos few-shot
        full_prompt = FEW_SHOT_EXAMPLES + "\n\n" + context_prompt
        
        # Generar respuesta
        response = self.llm_client.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=full_prompt,
            temperature=temperature,
            max_tokens=2000
        )
        
        # Agregar información de contexto usado
        response['context_info'] = {
            'used_sections': use_relevant_sections,
            'sections_count': len(relevant_sections) if use_relevant_sections else len(self.document_sections),
            'metadata': self.document_metadata
        }
        
        return response
    
    def get_context_visualization(self, query: str = None) -> Dict:
        """
        Retorna información sobre cómo se construye el contexto
        """
        if not self.current_document:
            return {}
        
        visualization = {
            'document_metadata': self.document_metadata,
            'total_sections': len(self.document_sections),
            'total_tokens': self.llm_client.count_tokens(self.current_document),
            'sections': []
        }
        
        # Si hay query, mostrar secciones relevantes
        if query and self.document_sections:
            relevant = self.doc_processor.find_relevant_sections(
                self.document_sections,
                query,
                top_k=5
            )
            visualization['relevant_sections'] = [
                {
                    'title': s['title'],
                    'preview': s['content'][:200] + '...',
                    'tokens': self.llm_client.count_tokens(s['content'])
                }
                for s in relevant
            ]
        else:
            # Mostrar todas las secciones
            visualization['sections'] = [
                {
                    'title': s['title'],
                    'preview': s['content'][:150] + '...',
                    'tokens': self.llm_client.count_tokens(s['content'])
                }
                for s in self.document_sections[:10]
            ]
        
        return visualization
