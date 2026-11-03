import calendar
import datetime
import json
import os
import streamlit as st

# Configuración básica de página
st.set_page_config(
    page_title="Calendario Turnos",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 1. ESTILOS CSS ADAPTATIVOS PARA PANTALLA DE CELULAR (iOS/Android)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Ajustes generales de contenedor móvil */
    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
        max-width: 480px !important; /* Ancho máximo estándar de smartphone */
        margin: auto;
    }
    
    /* Ocultar barra superior y pie de Streamlit */
    header, footer { visibility: hidden !important; height: 0px !important; }
    
    /* Grilla responsiva de 7 columnas exactas */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 3px;
        width: 100%;
        margin-top: 8px;
        box-sizing: border-box;
    }

    .header-day {
        text-align: center;
        font-weight: 700;
        font-size: 11px;
        color: #64748b;
        padding: 4px 0;
        text-transform: uppercase;
    }

    .empty-cell {
        background: transparent;
        aspect-ratio: 1 / 1.1;
    }

    /* Tarjetas interactivas de días */
    .day-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        aspect-ratio: 1 / 1.1;
        border-radius: 6px;
        text-decoration: none !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-sizing: border-box;
        transition: transform 0.1s ease;
        -webkit-tap-highlight-color: transparent;
    }

    .day-card:active {
        transform: scale(0.93);
    }

    .day-num {
        font-size: 12px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 2px;
    }

    .day-state {
        font-size: 8px;
        font-weight: 800;
        text-transform: uppercase;
        line-height: 1;
    }

    /* Esquema de colores por turno */
    .state-desc {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    .state-t1 {
        background-color: #bae6fd;
        color: #0369a1;
        border: 1px solid #7dd3fc;
    }
    .state-t2 {
        background-color: #fed7aa;
        color: #c2410c;
        border: 1px solid #fdba74;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. PERSISTENCIA DE DATOS EN ARCHIVO JSON
# -------------------------------------------------------------
ARCHIVO_DATOS = "turnos.json"


def cargar_datos():
  if os.path.exists(ARCHIVO_DATOS):
    try:
      with open(ARCHIVO_DATOS, "r") as f:
        datos = json.load(f)
        turnos = {}
        for k, v in datos.get("turnos", {}).items():
          a, m, d = map(int, k.split("-"))
          turnos[(a, m, d)] = v
        return turnos, datos.get("hrs_t1", 8.0), datos.get("hrs_t2", 8.0)
    except Exception:
      pass
  return {}, 8.0, 8.0


def guardar_datos():
  datos = {
      "turnos": {
          f"{k[0]}-{k[1]}-{k[2]}": v for k, v in st.session_state.turnos.items()
      },
      "hrs_t1": st.session_state.hrs_t1,
      "hrs_t2": st.session_state.hrs_t2,
  }
  with open(ARCHIVO_DATOS, "w") as f:
    json.dump(datos, f)


# Carga inicial de estado
if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True

# -------------------------------------------------------------
# 3. INTERACCIÓN POR EVENTOS DE CLICK (QUERY PARAMS)
# -------------------------------------------------------------
params = st.query_params
if "toggle" in params:
  try:
    dia_cliqueado = int(params["toggle"])
    clave = (st.session_state.anio, st.session_state.mes, dia_cliqueado)
    estado_actual = st.session_state.turnos.get(clave, "DESCANSO")
    ciclo = ["DESCANSO", "T1", "T2"]
    siguiente_estado = ciclo[(ciclo.index(estado_actual) + 1) % len(ciclo)]

    st.session_state.turnos[clave] = siguiente_estado
    guardar_datos()
  except Exception:
    pass

  st.query_params.clear()
  st.rerun()

# -------------------------------------------------------------
# 4. VISTA DE LA APLICACIÓN
# -------------------------------------------------------------
st.markdown(
    "<h3 style='text-align: center; margin: 0 0 10px 0;'>📅 Turnos"
    " ARAMARK</h3>",
    unsafe_allow_html=True,
)

# Ajuste de Horas
col_h1, col_h2 = st.columns(2)
with col_h1:
  h1_val = st.number_input(
      "Hrs T1", value=st.session_state.hrs_t1, step=0.5, key="input_h1"
  )
  if h1_val != st.session_state.hrs_t1:
    st.session_state.hrs_t1 = h1_val
    guardar_datos()

with col_h2:
  h2_val = st.number_input(
      "Hrs T2", value=st.session_state.hrs_t2, step=0.5, key="input_h2"
  )
  if h2_val != st.session_state.hrs_t2:
    st.session_state.hrs_t2 = h2_val
    guardar_datos()

# Navegación de Meses
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
if col_m1.button("◄", key="prev_month"):
  if st.session_state.mes == 1:
    st.session_state.mes = 12
    st.session_state.anio -= 1
  else:
    st.session_state.mes -= 1
  st.rerun()

meses_nombres = [
    "",
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]
col_m2.markdown(
    f"<h4 style='text-align: center; margin: 5px 0;'>"
    f"{meses_nombres[st.session_state.mes]} {st.session_state.anio}</h4>",
    unsafe_allow_html=True,
)

if col_m3.button("►", key="next_month"):
  if st.session_state.mes == 12:
    st.session_state.mes = 1
    st.session_state.anio += 1
  else:
    st.session_state.mes += 1
  st.rerun()

# -------------------------------------------------------------
# 5. CONSTRUCCIÓN DE LA GRILLA HTML EN PANTALLA CELULAR
# -------------------------------------------------------------
html_grid = ['<div class="calendar-grid">']

# Encabezados de días
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
for dia_head in dias_semana:
  html_grid.append(f'<div class="header-day">{dia_head}</div>')

# Matriz del calendario
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)

for semana in matriz:
  for dia in semana:
    if dia == 0:
      html_grid.append('<div class="empty-cell"></div>')
    else:
      clave = (st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      clase_css = "state-desc"
      txt_estado = "DESC"
      if estado == "T1":
        clase_css = "state-t1"
        txt_estado = "T1"
      elif estado == "T2":
        clase_css = "state-t2"
        txt_estado = "T2"

      html_grid.append(f"""
                <a href="?toggle={dia}" target="_self" class="day-card {clase_css}">
                    <span class="day-num">{dia}</span>
                    <span class="day-state">{txt_estado}</span>
                </a>
            """)

html_grid.append("</div>")

# Renderizar grilla HTML completa
st.markdown("".join(html_grid), unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. RESUMEN Y HORAS TOTALES
# -------------------------------------------------------------
cnt_t1, cnt_t2, cnt_desc = 0, 0, 0
dias_mes = calendar.monthrange(st.session_state.anio, st.session_state.mes)[1]

for d in range(1, dias_mes + 1):
  k = (st.session_state.anio, st.session_state.mes, d)
  est = st.session_state.turnos.get(k, "DESCANSO")
  if est == "T1":
    cnt_t1 += 1
  elif est == "T2":
    cnt_t2 += 1
  else:
    cnt_desc += 1

total_hrs = (cnt_t1 * st.session_state.hrs_t1) + (
    cnt_t2 * st.session_state.hrs_t2
)

st.divider()
st.metric("Total Horas Trabajadas", f"{total_hrs:.1f} hrs")
st.caption(
    f"**T1:** {cnt_t1} d | **T2:** {cnt_t2} d | **Descansos:** {cnt_desc} d"
)