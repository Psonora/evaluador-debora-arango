import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# Configuración de la página
st.set_page_config(page_title="Evaluación Rectoría 2027-2031", page_icon="⚖️", layout="wide")

# PROMPT DEL SISTEMA COMPLETO Y NORMATIVO
SYSTEM_PROMPT = """
Actúa como un SISTEMA DE VERIFICACIÓN Y EVALUACIÓN DOCUMENTAL para el proceso de selección de Rectoría 2027–2031 del Tecnológico de Artes Débora Arango.

Tu función NO es recomendar, elegir ni ordenar candidatos. Tu función es analizar objetivamente la documentación aportada por cada candidato y aplicar exclusivamente los criterios oficiales del proceso.

FUENTES Y NORMA PRINCIPAL:
- Criterios de evaluación para la selección de Rectoría 2027–2031.
- Acuerdo 244 de 2018.

REGLA FUNDAMENTAL:
- NO infieras información que no esté documentalmente acreditada.
- Una afirmación escrita únicamente en el CV no genera puntuación si no está respaldada por un documento válido.
- Toda experiencia, cargo, proyecto, función o resultado puntuable debe poder verificarse mediante un documento expedido por una entidad competente que identifique claramente rol, periodo y alcance.

FASE 1 — REQUISITOS HABILITANTES:
Verifica individualmente utilizando exclusivamente: CUMPLE, NO CUMPLE o REQUIERE REVISIÓN (explica qué documento sustenta cada conclusión):
1. Ciudadanía colombiana en ejercicio.
2. Ausencia de condenas o sanciones incompatibles.
3. Título profesional universitario y título de posgrado de IES reconocida por el MEN (convalidación si es extranjero).
4. Mínimo 10 años de experiencia profesional, de los cuales mínimo 5 años sean de experiencia académica o administrativa en IES.
5. No estar en edad de retiro forzoso al momento de la inscripción.
6. No estar incurso en inhabilidades o incompatibilidades constitucionales o legales.

FASE 2 — EVALUACIÓN DE HOJA DE VIDA (MATRIZ DE 120 PUNTOS):

1. GOBERNANZA Y DIRECCIÓN INSTITUCIONAL (Máximo 30 puntos):
   - Rector, Vicerrector o Representante Legal en IES: 30 puntos.
   - Director, Decano, Secretario General o equivalente en IES: 20 puntos.
   - Coordinador o Jefe de unidad académica/administrativa en IES: 10 puntos.
   (Regla: Otorgar únicamente el puntaje del cargo de mayor jerarquía acreditado).

2. SISTEMAS DE CALIDAD ACADÉMICA (Máximo 25 puntos):
   - Liderazgo en creación/renovación de programas y obtención de registros calificados: 10 puntos.
   - Programas del área artística: 5 puntos.
   - Liderazgo en autoevaluación, acreditación institucional o SIAC: 10 puntos.

3. SOSTENIBILIDAD FINANCIERA Y DE PROYECTOS (Máximo 25 puntos):
   - Responsabilidad directa sobre presupuesto: 10 puntos.
   - Dirección/liderazgo de proyectos y convocatorias: 10 puntos.
   - Proyectos del sector artístico, cultural o creativo: 5 puntos.

4. RELACIONAMIENTO ESTRATÉGICO (Máximo 20 puntos):
   - Liderazgo o representación institucional en convenios, mesas técnicas o proyectos conjuntos: 10 puntos.
   - Par académico reconocido o integrante de redes de educación superior: 10 puntos.

5. CRECIMIENTO E IMPACTO TERRITORIAL (Máximo 20 puntos):
   - Liderazgo en extensión, regionalización o proyectos de ampliación de cobertura: 10 puntos.
   - Gestión de convenios de cooperación/internacionalización: 10 puntos.

PARA CADA CRITERIO DE LA FASE 2 DETALLA:
1. Criterio evaluado.
2. Puntaje máximo.
3. Puntaje asignado.
4. Estado (ACREDITADO / NO ACREDITADO / REQUIERE REVISIÓN).
5. Documento sustento.
6. Evidencia concreta encontrada.
7. Periodo acreditado.
8. Cargo o rol acreditado.
9. Alcance/responsabilidad.
10. Explicación breve del puntaje.

CONTROL DE DOBLE VALORACIÓN:
Identifica expresamente cuando una evidencia podría estar siendo utilizada en más de un criterio y determina qué aspecto específico corresponde a cada criterio sin duplicar el mismo hecho.

ESTRICTAS PROHIBICIONES:
NO evalúes personalidad, simpatía, liderazgo percibido, apariencia, género, ideología, opinión política, ni hagas prospección de éxito.

ESTRUCTURA DE SALIDA OBLIGATORIA:
1. Tabla de Requisitos Habilitantes (Fase 1).
2. Tabla de Evaluación Matriz de 120 Puntos (Fase 2).
3. Resumen Final de Cierre:
   - Total de puntos documentalmente acreditados.
   - Puntos que requieren revisión.
   - Evidencias faltantes.
   - Posibles alertas de doble valoración.
   - Observaciones para revisión humana.
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

# Barra lateral de configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key_input = st.text_input("Clave de API de Gemini:", type="password")
    api_key = api_key_input.strip() if api_key_input else ""
    
    selected_model = None
    if api_key:
        try:
            genai.configure(api_key=api_key)
            all_models = [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]
            flash_models = [m for m in all_models if 'flash' in m.lower()]
            other_models = [m for m in all_models if 'flash' not in m.lower()]
            model_options = flash_models + other_models
            
            if model_options:
                selected_model = st.selectbox("Modelo habilitado en tu cuenta:", model_options)
            else:
                selected_model = st.selectbox("Modelo:", ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash"])
        except Exception:
            selected_model = st.selectbox("Modelo (Manual):", ["models/gemini-1.5-flash-latest", "models/gemini-1.5-flash"])
    else:
        st.info("🔑 Ingresa tu API Key para detectar los modelos disponibles.")
        selected_model = "models/gemini-1.5-flash-latest"

# GUÍA VISUAL Y LISTADO DE DOCUMENTOS EN EL ENTORNO PRINCIPAL
with st.expander("📌 **GUÍA DE DOCUMENTOS Y SOPORTES REQUERIDOS (HACER CLIC PARA DESPLEGAR)**", expanded=True):
    st.markdown("""
    Para que el sistema aplique correctamente la matriz de verificación (Acuerdo 244 de 2018), se recomienda adjuntar los siguientes documentos en formato PDF:

    1. **📄 Hoja de Vida (CV) del Candidato:** Resume la trayectoria académica y profesional.
    2. **🪪 Documento de Identidad:** Cédula de ciudadanía o soporte habilitante de nacionalidad.
    3. **🎓 Títulos y Posgrados:**
       - Título profesional universitario.
       - Título de posgrado (Especialización, Maestría o Doctorado en IES reconocida o resolución de convalidación del MEN).
    4. **📜 Certificaciones Laborales Académicas y Administrativas:**
       - Soportes que acrediten mínimo 10 años de experiencia profesional general.
       - Soportes que acrediten mínimo 5 años en IES (cargos de Gobernanza, Dirección, Decanaturas, Coordinaciones, etc., especificando fechas exactas de inicio/fin y funciones).
    5. **🏛️ Soportes de Calidad Académica y Proyectos:**
       - Resoluciones o certificaciones de liderazgo en registros calificados, autoevaluación o acreditación (especialmente del área artística si aplica).
       - Certificados de ejecución o gestión presupuestal y de proyectos.
    6. **🤝 Evidencias de Relacionamiento y Territorio:**
       - Actas, convenios o certificados de representación institucional, redes de Educación Superior, pares académicos o proyectos de extensión e internacionalización.

    > **⚠️ Recordatorio importante:** Toda afirmación que esté únicamente en el CV y no cuente con su respectivo certificado o soporte PDF adjunto, **no generará puntuación**.
    """)

uploaded_files = st.file_uploader("Sube los documentos PDF del candidato (puedes seleccionar varios archivos a la vez):", type=["pdf"], accept_multiple_files=True)
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
                # Temperatura fija en 0.0 para objetividad estricta
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=SYSTEM_PROMPT,
                    generation_config={"temperature": 0.0}
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
                err_msg = str(e)
                if "429" in err_msg or "Quota" in err_msg or "quota" in err_msg:
                    st.error("⏳ **Límite de velocidad superado.** Espera de 10 a 15 segundos y vuelve a pulsar el botón.")
                elif "404" in err_msg:
                    st.error("❌ Modelo no disponible en este momento. Por favor selecciona otro en el menú de la barra lateral.")
                else:
                    st.error(f"Error en la ejecución: {err_msg}")
