import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# ── Configuración de la página ─────────────────────────────────────
st.set_page_config(
    page_title="Analizador de Texto",
    page_icon="📊",
    layout="wide"
)

# ── Estilos ────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #fffde7; color: #333333; }

div.stButton > button {
    background-color: #f9a825;
    color: white;
    border-radius: 10px;
    padding: 10px 24px;
    border: none;
    font-size: 16px;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover { background-color: #f57f17; color: white; }
section[data-testid="stSidebar"] { background-color: #fff9c4; }
h1, h2, h3 { color: #f57f17; }

.tarjeta {
    background-color: #fff8e1;
    border-left: 5px solid #f9a825;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Título ─────────────────────────────────────────────────────────
st.title("📝 Analizador de Texto con TextBlob")
st.markdown("Analiza el sentimiento, subjetividad, palabras clave y frases de cualquier texto.")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Opciones")
    modo = st.selectbox("Modo de entrada:", ["Texto directo", "Archivo de texto"])
    st.markdown("---")
    st.markdown("""
    **📖 Guía rápida**

    - **Sentimiento**: de `-1` (negativo) a `+1` (positivo)
    - **Subjetividad**: de `0` (objetivo) a `1` (subjetivo)

    ---
    El texto se traduce al inglés automáticamente para mejor precisión con TextBlob.
    """)

# ── Stop words ─────────────────────────────────────────────────────
STOP_WORDS = set([
    "a","al","algo","algunas","algunos","ante","antes","como","con","contra",
    "cual","cuando","de","del","desde","donde","durante","e","el","ella",
    "ellas","ellos","en","entre","era","eras","es","esa","esas","ese","eso",
    "esos","esta","estas","este","esto","estos","ha","había","han","has",
    "hasta","he","la","las","le","les","lo","los","me","mi","mis","mucho",
    "muchos","muy","nada","ni","no","nos","o","os","otra","otras","otro",
    "otros","para","pero","poco","por","porque","que","quien","quienes","se",
    "sea","sean","según","si","sido","sin","sobre","son","soy","su","sus",
    "también","tanto","te","tener","tiene","tienen","todo","todos","tu","tus",
    "tú","un","una","uno","unos","y","ya","yo",
    "a","about","above","after","again","all","am","an","and","any","are",
    "as","at","be","because","been","before","being","below","between","both",
    "but","by","did","do","does","doing","down","during","each","few","for",
    "from","had","has","have","having","he","her","here","hers","him","his",
    "how","i","if","in","into","is","it","its","me","more","most","my","no",
    "nor","not","of","off","on","once","only","or","other","our","ours","out",
    "over","own","same","she","should","so","some","such","than","that","the",
    "their","them","then","there","these","they","this","those","through","to",
    "too","under","until","up","very","was","we","were","what","when","where",
    "which","while","who","whom","why","with","would","you","your","yours"
])

# ── Funciones ──────────────────────────────────────────────────────
translator = Translator()

def traducir_texto(texto):
    try:
        return translator.translate(texto, src='es', dest='en').text
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

def contar_palabras(texto):
    palabras = re.findall(r'\b\w+\b', texto.lower())
    filtradas = [p for p in palabras if p not in STOP_WORDS and len(p) > 2]
    contador = {}
    for p in filtradas:
        contador[p] = contador.get(p, 0) + 1
    return dict(sorted(contador.items(), key=lambda x: x[1], reverse=True)), filtradas

def procesar_texto(texto):
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento  = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_orig  = [f.strip() for f in re.split(r'[.!?]+', texto) if f.strip()]
    frases_trad  = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases = [{"original": frases_orig[i], "traducido": frases_trad[i]}
              for i in range(min(len(frases_orig), len(frases_trad)))]
    contador, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases,
        "contador_palabras": contador,
        "palabras": palabras,
        "texto_original": texto,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(r):
    # ── Métricas rápidas ───────────────────────────────────────────
    st.markdown("### 📊 Resumen")
    c1, c2, c3 = st.columns(3)

    sent = r["sentimiento"]
    subj = r["subjetividad"]

    if sent > 0.05:
        etiqueta, emoji_sent = "Positivo", "😊"
    elif sent < -0.05:
        etiqueta, emoji_sent = "Negativo", "😔"
    else:
        etiqueta, emoji_sent = "Neutral", "😐"

    with c1:
        st.metric(f"{emoji_sent} Sentimiento", f"{sent:.2f}", etiqueta)
    with c2:
        st.metric("🧠 Subjetividad", f"{subj:.2f}",
                  "Alta" if subj > 0.5 else "Baja")
    with c3:
        st.metric("📝 Palabras clave", len(r["contador_palabras"]))

    st.markdown("---")

    # ── Barras de progreso ─────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎭 Sentimiento y Subjetividad")
        st.write("**Sentimiento** (−1 negativo → +1 positivo)")
        st.progress((sent + 1) / 2)
        if sent > 0.05:
            st.success(f"📈 Positivo ({sent:.2f})")
        elif sent < -0.05:
            st.error(f"📉 Negativo ({sent:.2f})")
        else:
            st.info(f"📊 Neutral ({sent:.2f})")

        st.write("**Subjetividad** (0 objetivo → 1 subjetivo)")
        st.progress(subj)
        if subj > 0.5:
            st.warning(f"💭 Alta subjetividad ({subj:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({subj:.2f})")

    with col2:
        st.markdown("### 🔤 Palabras más frecuentes")
        if r["contador_palabras"]:
            top10 = dict(list(r["contador_palabras"].items())[:10])
            st.bar_chart(top10)

    st.markdown("---")

    # ── Traducción ─────────────────────────────────────────────────
    with st.expander("🌐 Ver traducción completa"):
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**Texto original (Español):**")
            st.text(r["texto_original"])
        with cb:
            st.markdown("**Texto traducido (Inglés):**")
            st.text(r["texto_traducido"])

    # ── Análisis por frases ────────────────────────────────────────
    st.markdown("### 🔍 Análisis por frases")
    if r["frases"]:
        for i, frase_dict in enumerate(r["frases"][:10], 1):
            orig = frase_dict["original"]
            trad = frase_dict["traducido"]
            try:
                s = TextBlob(trad).sentiment.polarity
                emoji_f = "😊" if s > 0.05 else "😟" if s < -0.05 else "😐"
                color   = "success" if s > 0.05 else "error" if s < -0.05 else "info"
                getattr(st, color)(
                    f"{i}. {emoji_f} **\"{orig}\"**  \n"
                    f"↳ *{trad}* — sentimiento: `{s:.2f}`"
                )
            except:
                st.write(f"{i}. **\"{orig}\"** → *{trad}*")
    else:
        st.info("No se detectaron frases.")

    # ── Tabla de palabras clave ────────────────────────────────────
    st.markdown("### 📋 Tabla de palabras clave")
    if r["contador_palabras"]:
        df = pd.DataFrame(
            list(r["contador_palabras"].items())[:20],
            columns=["Palabra", "Frecuencia"]
        )
        st.dataframe(df, use_container_width=True)

# ── Lógica principal ───────────────────────────────────────────────
if modo == "Texto directo":
    st.markdown("### ✏️ Ingresa tu texto")
    texto = st.text_area("", height=200,
                         placeholder="Escribe o pega aquí el texto a analizar...")
    if st.button("🔍 Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando..."):
                resultados = procesar_texto(texto)
            crear_visualizaciones(resultados)
        else:
            st.warning("⚠️ Por favor ingresa algún texto.")

elif modo == "Archivo de texto":
    st.markdown("### 📂 Carga un archivo")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("👁️ Ver contenido del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("🔍 Analizar archivo"):
                with st.spinner("Analizando archivo..."):
                    resultados = procesar_texto(contenido)
                crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# ── Info y pie de página ───────────────────────────────────────────
with st.expander("📚 Sobre el análisis"):
    st.markdown("""
    - **Sentimiento**: de `-1` (muy negativo) a `+1` (muy positivo)
    - **Subjetividad**: de `0` (muy objetivo) a `1` (muy subjetivo)
    - El texto se traduce automáticamente al inglés para mayor precisión
    - Las palabras vacías (artículos, preposiciones) se excluyen del conteo
    """)

st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y TextBlob")
