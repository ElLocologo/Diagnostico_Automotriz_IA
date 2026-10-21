import os
import json
import streamlit as st

# Configuración de página con estética moderna
st.set_page_config(
    page_title="Explorador de Árboles con IA",
    page_icon="🌳",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una presentación premium
st.markdown("""
<style>
    /* Estilo del contenedor principal */
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563EB, #7C3AED);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Breadcrumb / Migas de pan */
    .breadcrumb-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
    }
    @media (prefers-color-scheme: dark) {
        .breadcrumb-box {
            background-color: #1E293B;
            border-color: #334155;
            color: #F1F5F9;
        }
    }
    .breadcrumb-item {
        color: #2563EB;
        font-weight: 600;
    }
    .breadcrumb-sep {
        color: #94A3B8;
        font-weight: 400;
    }
    
    /* Tarjeta de pregunta actual */
    .question-card {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .question-card {
            background: #0F172A;
            border-color: #1E293B;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
    }
    
    /* Badge de nivel */
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #EFF6FF;
        color: #1D4ED8;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    @media (prefers-color-scheme: dark) {
        .level-badge {
            background-color: #1E3A8A;
            color: #93C5FD;
        }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Funciones para manejo de datos del árbol
# -------------------------------------------------------------
JSON_FILE = "EstructurasDeDatos.json"

def cargar_arbol(ruta_archivo=JSON_FILE):
    """Carga el árbol desde el archivo JSON de forma segura."""
    if not os.path.exists(ruta_archivo):
        return None, f"No se encontró el archivo '{ruta_archivo}'."
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if not isinstance(datos, dict) or "valor" not in datos:
                return None, "El formato del JSON debe contener al menos un nodo raíz con la clave 'valor'."
            return datos, None
    except json.JSONDecodeError as e:
        return None, f"Error al decodificar JSON: {e}"
    except Exception as e:
        return None, f"Error al leer archivo: {e}"

# -------------------------------------------------------------
# Inicialización del estado de la sesión
# -------------------------------------------------------------
if "arbol" not in st.session_state or st.session_state.arbol is None:
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    st.session_state.historial = [arbol] if arbol else []
    st.session_state.explicacion_ia = None

def reiniciar_navegacion():
    """Reinicia la navegación al nodo raíz."""
    if st.session_state.arbol:
        st.session_state.historial = [st.session_state.arbol]
    else:
        st.session_state.historial = []
    st.session_state.explicacion_ia = None

def recargar_archivo():
    """Recarga el archivo JSON desde el disco para reflejar cambios externos."""
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    reiniciar_navegacion()

# -------------------------------------------------------------
# Barra lateral (Configuración y utilidades)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    # Selector de modelo Ollama
    modelo_ollama = st.text_input(
        "Modelo de Ollama:",
        value="llama-automotriz",
        help="Nombre del modelo descargado localmente (ej: llama-automotriz, llama3, mistral, gemma:2b)"
    )
    
    temperatura = st.slider(
        "Creatividad (Temperatura):",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    
    st.markdown("---")
    st.markdown("### 📂 Gestión del Árbol")
    if st.button("🔄 Recargar JSON", use_container_width=True, help="Vuelve a leer 'EstructurasDeDatos.json'"):
        recargar_archivo()
        st.toast("Árbol recargado correctamente", icon="✅")
        st.rerun()

    if st.button("⏪ Reiniciar Recorrido", use_container_width=True):
        reiniciar_navegacion()
        st.rerun()

    # Previsualización del JSON
    with st.expander("👀 Ver estructura del JSON activo"):
        if st.session_state.arbol:
            st.json(st.session_state.arbol)
        else:
            st.warning("No hay árbol cargado.")

# -------------------------------------------------------------
# Cabecera principal
# -------------------------------------------------------------
st.markdown('<div class="main-title">🌳 Explorador de Estructuras de Datos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Navegación dinámica por ramas y explicación inteligente con Ollama</div>', unsafe_allow_html=True)

# Manejo de error si no existe el archivo JSON
if st.session_state.error_arbol:
    st.error(st.session_state.error_arbol)
    st.stop()

# Nodo actual y camino recorrido
historial = st.session_state.historial
if not historial:
    st.session_state.historial = [st.session_state.arbol]
    historial = st.session_state.historial

nodo_actual = historial[-1]
camino_titulos = [nodo["valor"] for nodo in historial]
nivel_actual = len(historial)
hijos = nodo_actual.get("hijos", [])

# -------------------------------------------------------------
# Miga de pan / Breadcrumb Dinámica
# -------------------------------------------------------------
breadcrumb_html = '<div class="breadcrumb-box"><span>📍 <b>Ruta actual:</b></span> '
for idx, tit in enumerate(camino_titulos):
    if idx > 0:
        breadcrumb_html += '<span class="breadcrumb-sep">➔</span> '
    breadcrumb_html += f'<span class="breadcrumb-item">{tit}</span> '
breadcrumb_html += '</div>'
st.markdown(breadcrumb_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# Lógica de Paso a Paso: Pregunta y Sub-ramas
# -------------------------------------------------------------
if hijos:
    # AÚN HAY SUB-RAMAS: Mostramos la pregunta dinámica correspondiente
    st.session_state.explicacion_ia = None # Limpiamos explicación previa
    
    # Generación dinámica de la pregunta según el nodo o campo personalizado en JSON
    if "pregunta" in nodo_actual:
        pregunta_texto = nodo_actual["pregunta"]
    elif nivel_actual == 1:
        pregunta_texto = f"¿Qué categoría principal de **{nodo_actual['valor']}** deseas explorar?"
    else:
        pregunta_texto = f"Dentro de **{nodo_actual['valor']}**, ¿qué sub-rama o concepto quieres consultar?"

    st.markdown(f"""
    <div class="question-card">
        <span class="level-badge">Paso {nivel_actual}</span>
        <h3 style="margin-top:0.3rem; margin-bottom:0.5rem; font-weight:600;">{pregunta_texto}</h3>
        <p style="color:#64748B; font-size:0.9rem; margin-bottom:0;">Selecciona una opción para continuar el recorrido:</p>
    </div>
    """, unsafe_allow_html=True)

    # Renderizado dinámico de las opciones (botones de selección de subramal)
    cols = st.columns(min(len(hijos), 3))
    for i, hijo in enumerate(hijos):
        col_act = cols[i % len(cols)]
        etiqueta = hijo.get("valor", f"Opción {i+1}")
        
        # Si tiene hijos, mostramos icono de carpeta/rama; si es hoja, icono de documento
        icono = "📁" if hijo.get("hijos") else "📄"
        
        if col_act.button(f"{icono} {etiqueta}", key=f"btn_hijo_{nivel_actual}_{i}", use_container_width=True):
            st.session_state.historial.append(hijo)
            st.rerun()

    # Botones de navegación hacia atrás
    st.markdown("<br>", unsafe_allow_html=True)
    col_nav1, col_nav2, _ = st.columns([1, 1, 2])
    with col_nav1:
        if nivel_actual > 1:
            if st.button("⬅️ Paso anterior", use_container_width=True):
                st.session_state.historial.pop()
                st.rerun()
    with col_nav2:
        if nivel_actual > 1:
            if st.button("🔄 Desde el inicio", use_container_width=True):
                reiniciar_navegacion()
                st.rerun()

else:
    # -------------------------------------------------------------
    # NIVEL FINAL (HOJA): Se consulta a la IA (Ollama)
    # -------------------------------------------------------------
    st.markdown(f"""
    <div class="question-card" style="border-left: 5px solid #10B981;">
        <span class="level-badge" style="background-color: #D1FAE5; color: #047857;">Nivel Final Alcanzado</span>
        <h3 style="margin-top: 0.3rem; margin-bottom: 0.5rem;">Concepto: <b>{nodo_actual['valor']}</b></h3>
        <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 0;">
            Has llegado al final de este ramal. A continuación se genera la explicación con el modelo local de IA.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Botón para regresar
    col_back1, col_back2, _ = st.columns([1, 1, 2])
    with col_back1:
        if st.button("⬅️ Elegir otro subramal", use_container_width=True):
            st.session_state.historial.pop()
            st.rerun()
    with col_back2:
        if st.button("🔄 Reiniciar exploración", use_container_width=True):
            reiniciar_navegacion()
            st.rerun()

    st.markdown("---")
    st.subheader(f"🤖 Explicación del modelo local ({modelo_ollama})")

# Contenedor de la explicación adaptado a mecánica
    prompt = (
        f"Actúa como un mecánico experto. El usuario necesita asistencia con: '{nodo_actual['valor']}' "
        f"dentro de la categoría {camino_titulos[1] if len(camino_titulos) > 1 else camino_titulos[0]}. "
        "Estructura tu respuesta con: 1) Pasos clave para la revisión o diagnóstico, 2) Herramientas o precauciones necesarias, "
        "y 3) Una recomendación de seguridad. Sé claro, directo y profesional."
    )

    # Generación con Ollama (Streaming en tiempo real)
    try:
        import ollama

        if st.session_state.explicacion_ia is None:
            with st.spinner(f"Consultando a {modelo_ollama} vía Ollama..."):
                stream = ollama.chat(
                    model=modelo_ollama,
                messages=[
                {"role": "user", "content": prompt}
            ],
                    options={"temperature": temperatura},
                    stream=True
                )
                # Función generadora para streaming con st.write_stream
                def generar_stream():
                    for chunk in stream:
                        yield chunk['message']['content']

                respuesta_completa = st.write_stream(generar_stream)
                st.session_state.explicacion_ia = respuesta_completa
        else:
            # Mostrar la explicación almacenada en la sesión si no se ha cambiado de nodo
            st.markdown(st.session_state.explicacion_ia)
            
            if st.button("🔄 Regenerar respuesta"):
                st.session_state.explicacion_ia = None
                st.rerun()

    except Exception as e:
        error_msg = str(e)
        st.error("⚠️ No se pudo comunicar con el servidor local de Ollama.")
        
        col_err1, col_err2 = st.columns([1, 1])
        with col_err1:
            if st.button("🔄 Reintentar conexión con Ollama", use_container_width=True):
                st.session_state.explicacion_ia = None
                st.rerun()
        with col_err2:
            if st.button("💡 Ver explicación de prueba (Modo Offline)", use_container_width=True):
                st.session_state.explicacion_ia = (
                    f"### 📘 Explicación demostrativa: {nodo_actual['valor']}\n\n"
                    f"* **Jerarquía**: `{' > '.join(camino_titulos)}`\n"
                    f"* **Definición**: En ciencias de la computación, `{nodo_actual['valor']}` es un componente esencial dentro de las estructuras de datos.\n"
                    f"* **Funcionamiento**: Permite organizar, gestionar y optimizar el acceso a la información según las reglas de su categoría padre (`{camino_titulos[-2] if len(camino_titulos) > 1 else 'Estructura'}`).\n"
                    f"* **Nota**: Esta es una respuesta de prueba local. Para obtener la explicación generada por la IA en tiempo real, inicia Ollama en tu computadora (`ollama serve`)."
                )
                st.rerun()

        with st.expander("🛠️ ¿Cómo solucionarlo?"):
            st.markdown(f"""
            1. **Verifica que Ollama esté iniciado**:
               Abre una terminal y ejecuta:
               ```bash
               ollama serve
               ```
               O abre la aplicación de escritorio de **Ollama**.
            
            2. **Verifica tener el modelo `{modelo_ollama}`**:
               En tu terminal ejecuta:
               ```bash
               ollama run {modelo_ollama}
               ```
            
            **Detalle del error técnico:**
            `{error_msg}`
            """)
