import calendar
import datetime
import json
import os
import streamlit as st

# -------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="Calendario Turnos ARAMARK",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 2. ESTILOS CSS: FORZAR 7 COLUMNAS HORIZONTALES EN MÓVIL
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Reset de márgenes en pantalla móvil */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        max-width: 460px !important;
        margin: auto;
    }
    
    /* Ocultar barra de navegación superior de Streamlit */
    header[data-testid="stHeader"], footer, #MainMenu {
        display: none !important;
    }

    /* FORZAR 7 COLUMNAS EN UNA SOLA FILA HORIZONTAL (Sin apilar en vertical) */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 2px !important;
        width: 100% !important;
        margin-bottom: 2px !important;
    }

    div[data-testid="column"], div[data-testid="stColumn"] {
        width: 14.285% !important;
        min-width: 0 !important;
        max-width: 14.285% !important;
        flex: 1 1 14.285% !important;
        padding: 0 !important;
    }

    /* ESTILO DE LOS BOTONES TÁCTILES DEL CALENDARIO */
    div[data-testid="stColumn"] button {
        width: 100% !important;
        min-height: 48px !important;
        height: 48px !important;
        padding: 2px 0px !important;
        margin: 0 !important;
        border-radius: 6px !important;
        font-size: 11px !important;
        line-height: 1.1 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        white-space: pre-wrap !important;
        -webkit-tap-highlight-color: transparent !important;
        transition: transform 0.08s ease !important;
    }

    div[data-testid="stColumn"] button:active {
        transform: scale(0.92) !important;
    }

    div[data-testid="stColumn"] button p {
        font-size: 11px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }

    /* COLORES POR ESTADO DE TURNO VÍA ARIA-LABEL */
    /* Descanso */
    div[data-testid="stColumn"] button[aria-label*="DESC"] {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border: 1px solid #334155 !important;
    }

    /* Turno 1 (Azul) */
    div[data-testid="stColumn"] button[aria-label*="T1"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        box-shadow: 0 1px 3px rgba(2, 132, 199, 0.4) !important;
    }

    /* Turno 2 (Naranja) */
    div[data-testid="stColumn"] button[aria-label*="T2"] {
        background-color: #ea580c !important;
        color: #ffffff !important;
        border: 1px solid #fb923c !important;
        box-shadow: 0 1px 3px rgba(234, 88, 12, 0.4) !important;
    }

    /* Día de Hoy (Borde verde) */
    div[data-testid="stColumn"] button[aria-label*="★"] {
        box-shadow: 0 0 0 2px #10b981 !important;
    }

    /* Encabezados de días de la semana */
    .day-header {
        text-align: center;
        font-weight: 800;
        font-size: 11px;
        color: #94a3b8;
        padding: 4px 0;
        text-transform: uppercase;
    }

    .empty-cell {
        height: 48px;
        width: 100%;
        background: transparent;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 3. PERSISTENCIA DE DATOS JSON
# -------------------------------------------------------------
ARCHIVO_DATOS = "turnos.json"


def fecha_key(anio: int, mes: int, dia: int) -> str:
  return f"{anio:04d}-{mes:02d}-{dia:02d}"


def cargar_datos():
  if os.path.exists(ARCHIVO_DATOS):
    try:
      with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        datos = json.load(f)
        return (
            datos.get("turnos", {}),
            float(datos.get("hrs_t1", 8.0)),
            float(datos.get("hrs_t2", 8.0)),
        )
    except Exception:
      pass
  return {}, 8.0, 8.0


def guardar_datos():
  datos = {
      "turnos": st.session_state.turnos,
      "hrs_t1": st.session_state.hrs_t1,
      "hrs_t2": st.session_state.hrs_t2,
  }
  with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)


if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True


# -------------------------------------------------------------
# 4. CALLBACKS INSTANTÁNEOS (SIN RECARGAR PÁGINA)
# -------------------------------------------------------------
def toggle_turno(fecha_str: str):
  ciclo = ["DESCANSO", "T1", "T2"]
  actual = st.session_state.turnos.get(fecha_str, "DESCANSO")
  siguiente = ciclo[(ciclo.index(actual) + 1) % len(ciclo)]
  st.session_state.turnos[fecha_str] = siguiente
  guardar_datos()


def prev_mes():
  if st.session_state.mes == 1:
    st.session_state.mes = 12
    st.session_state.anio -= 1
  else:
    st.session_state.mes -= 1


def next_mes():
  if st.session_state.mes == 12:
    st.session_state.mes = 1
    st.session_state.anio += 1
  else:
    st.session_state.mes += 1


def ir_hoy():
  hoy = datetime.date.today()