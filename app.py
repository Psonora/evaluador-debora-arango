import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuración de página
st.set_page_config(page_title="Evaluación Rectoría 2027-2031", page_icon="⚖️", layout="wide")

SYSTEM_PROMPT = """
Actúa como un SISTEMA DE VERIFICACIÓN Y EVALUACIÓN DOCUMENTAL para el proceso de selección de Rectoría 2027–2031 del Tecnológico de Artes Débora Arango.
Tu función NO es recomendar, elegir ni ordenar candidatos. Analiza objetivamente la documentación aportada aplicando exclusivamente los criterios oficiales del proceso (Acuerdo 244 de 2018).

REGLA FUNDAMENTAL:
- NO infieras información no acreditada. Lo que solo esté en la Hoja de Vida sin soporte no puntúa.
- Aplica las fases oficializadas:
  FASE 1: Requisitos Habilitantes (CUMPLE / NO CUMPLE / REQUIERE REVISIÓN).
  FASE 2: Matriz de 120 puntos (Gobernanza 30pt, Calidad Académica 25pt, Sostenibilidad Financiera 25pt, Relacionamiento Estratégico 20pt, Crecimiento Territorial 20pt).
- Aplica el control de doble valoración y restricciones cualitativas.
- Salida requerida: Tabla Fase 1, Tabla Fase 2, Resumen de Cierre (Puntos acreditados, por revisar, evidencias faltantes, alertas de doble valoración, observaciones).
"""

def extract_text_from_pdfs(uploaded_files):
    combined_text = ""
    for uploaded_file in uploaded_files:
        combined_text += f"\n\n--- INICIO DEL DOCUMENTO: {uploaded_file.name} ---\n"
        try:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    combined_text += text + "\n"
        except Exception as e:
            combined_text += f"[Error al leer el archivo: {str(e)}]\n"
        combined_text += f"--- FIN DEL DOCUMENTO: {uploaded_file.name} ---\n"
    return combined_text

st.title("⚖️ Sistema de Verificación Documental - Rectoría 2027–2031")
st.caption("Tecnológico de Artes Débora Arango | Evaluación objetiva conforme a norma")

with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("Clave de API de Gemini:", type="password")
    selected_model = st.selectbox("Modelo:", ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-2.5-flash"])
    temperature = st.slider("Temperatura:", 0.0, 0.5, 0.0, step=0.05)

uploaded_files = st.file_uploader("Sube los documentos PDF del candidato:", type=["pdf"], accept_multiple_files=True)
extra_text = st.text_area("Texto adicional o transcriptorio (Opcional):", height=100)

if st.button("🚀 Iniciar Verificación Documental", type="primary"):
    if not api_key:
        st.error("⚠️ Por favor, ingrese su API Key de Gemini en la barra lateral.")
    elif not uploaded_files and not extra_text.strip():
        st.warning("⚠️ Adjunte al menos un documento PDF.")
    else:
        with st.spinner("Procesando expediente bajo el marco normativo oficial..."):
            doc_content = extract_text_from_pdfs(uploaded_files) if uploaded_files else ""
            if extra_text.strip():
                doc_content += f"\n\n--- TEXTO ADICIONAL ---\n{extra_text.strip()}\n"
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=SYSTEM_PROMPT,
                    generation_config={"temperature": temperature}
                )
                response = model.generate_content(f"Evalúa objetivamente el siguiente expediente:\n\n{doc_content}")
                st.markdown(response.text)
                
                st.download_button(
                    label="📥 Descargar Informe",
                    data=response.text,
                    file_name="Informe_Evaluacion_Rectoria.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error en la ejecución: {str(e)}")
