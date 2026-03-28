"""
Procesador de documentos para extracción y segmentación de texto
"""

import re
from typing import List, Dict
import PyPDF2
from io import BytesIO

class DocumentProcessor:
    """Procesa y segmenta documentos legales"""
    
    def __init__(self, max_chunk_size: int = 2000):
        self.max_chunk_size = max_chunk_size
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error al procesar PDF: {str(e)}")
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Extrae texto de un archivo TXT"""
        try:
            return txt_file.read().decode('utf-8')
        except Exception as e:
            raise Exception(f"Error al procesar TXT: {str(e)}")
    
    def identify_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Identifica secciones en el documento basándose en patrones comunes
        """
        sections = []
        
        # Patrones para identificar títulos de secciones
        patterns = [
            r'(?:^|\n)(CLÁUSULA|CLAUSULA|ARTÍCULO|ARTICULO|SECCIÓN|SECCION)\s+(\d+|[IVXLCDM]+)[:\.\-\s]+([^\n]+)',
            r'(?:^|\n)(\d+)\.\s+([A-ZÁÉÍÓÚÑ][^\n]+)',
            r'(?:^|\n)([A-ZÁÉÍÓÚÑ\s]{3,}):',
        ]
        
        # Buscar secciones
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                start_pos = match.start()
                title = match.group(0).strip()
                sections.append({
                    'position': start_pos,
                    'title': title
                })
        
        # Ordenar por posición
        sections.sort(key=lambda x: x['position'])
        
        # Extraer contenido de cada sección
        for i, section in enumerate(sections):
            start = section['position']
            end = sections[i + 1]['position'] if i + 1 < len(sections) else len(text)
            section['content'] = text[start:end].strip()
        
        # Si no se encontraron secciones, dividir por párrafos
        if not sections:
            sections = self._split_by_paragraphs(text)
        
        return sections
    
    def _split_by_paragraphs(self, text: str) -> List[Dict[str, str]]:
        """Divide el texto en párrafos cuando no se detectan secciones"""
        paragraphs = text.split('\n\n')
        sections = []
        
        for i, para in enumerate(paragraphs):
            if para.strip():
                sections.append({
                    'position': i,
                    'title': f'Párrafo {i + 1}',
                    'content': para.strip()
                })
        
        return sections
    
    def chunk_text(self, text: str, chunk_size: int = None) -> List[str]:
        """
        Divide el texto en chunks manejables respetando límites de oraciones
        """
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        # Dividir por oraciones
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_metadata(self, text: str) -> Dict[str, str]:
        """
        Extrae metadatos del documento (fecha, partes, tipo)
        """
        metadata = {
            'type': 'Documento Legal',
            'title': 'Sin título',
            'date': 'No especificada',
            'parties': []
        }
        
        # Buscar fecha
        date_pattern = r'\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b'
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        if date_match:
            metadata['date'] = date_match.group(0)
        
        # Buscar tipo de documento
        doc_types = ['CONTRATO', 'CONVENIO', 'ACUERDO', 'ESCRITURA']
        for doc_type in doc_types:
            if doc_type in text.upper()[:500]:
                metadata['type'] = doc_type.title()
                break
        
        # Buscar partes
        parties_pattern = r'(?:entre|ENTRE)\s+([^,\n]+)\s+(?:y|Y)\s+([^,\n]+)'
        parties_match = re.search(parties_pattern, text[:1000])
        if parties_match:
            metadata['parties'] = [
                parties_match.group(1).strip(),
                parties_match.group(2).strip()
            ]
        
        return metadata
    
    def find_relevant_sections(self, sections: List[Dict], query: str, top_k: int = 3) -> List[Dict]:
        """
        Encuentra las secciones más relevantes para una consulta
        """
        # Palabras clave de la consulta
        query_words = set(query.lower().split())
        
        # Calcular relevancia de cada sección
        scored_sections = []
        for section in sections:
            content_lower = section['content'].lower()
            score = sum(1 for word in query_words if word in content_lower)
            scored_sections.append((score, section))
        
        # Ordenar por relevancia y retornar top_k
        scored_sections.sort(reverse=True, key=lambda x: x[0])
        return [section for score, section in scored_sections[:top_k] if score > 0]
