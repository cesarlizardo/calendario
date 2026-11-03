import calendar
import datetime
import json
import os
import streamlit as st

# Configuración de página optimizada para móvil
st.set_page_config(
    page_title="Calendario Turnos",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# CSS ESTRUCTURAL PARA PANTALLAS DE IPHONE (SAFARI / CHROME)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Ocultar margen superior predeterminado */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        max-width: 100% !important;
        overflow-x: hidden !important;
    }

    /* Reducir tamaño del título en móviles */
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
    }

    /* Forzar que las 7 columnas ocupen EXACTAMENTE el 100% sin scroll horizontal */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 1px !important;
        justify-content: space-between !important;
    }

    /* Ajuste fino para cada una de las 7 columnas */
    div[data-testid="column"] {
        width: 14.28% !important;
        min-width: 0px !important;
        flex: 1 1 14.28% !important;
        padding: 0px !important;
    }

    /* Formato táctil compacto para los botones del calendario */
    div.stButton > button {
        width: 100% !important;
        height: 46px !important;
        min-height: 46px !important;
        padding: 1px 0px !important;
        font-size: 10px !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        white-space: pre-wrap !important;
        border-radius: 4px !important;
        margin: 0px !important;
    }

    /* Formato específico para inputs de horas */
    div[data-testid="stNumberInput"] input {
        font-size: 12px !important;
        padding: 4px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# PERSISTENCIA DE DATOS (GUARDADO AUTOMÁTICO JSON)
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


if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True

# -------------------------------------------------------------
# VISTA INTERACTIVA
# -------------------------------------------------------------
st.markdown("<h1>📅 Turnos ARAMARK</h1>", unsafe_allow_html=True)

# Configuración de horas
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

# Navegación mensual
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
if col_m1.button("◄", key="btn_prev_mes"):
  if st.session_state.mes == 1:
    st.session_state.mes = 12
    st.session_state.anio -= 1
  else:
    st.session_state.mes -= 1
  st.rerun()

meses = [
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
    f"<h4 style='text-align: center; margin: 4px 0;'>{meses[st.session_state.mes]} {st.session_state.anio}</h4>",
    unsafe_allow_html=True,
)

if col_m3.button("►", key="btn_next_mes"):
  if st.session_state.mes == 12:
    st.session_state.mes = 1
    st.session_state.anio += 1
  else:
    st.session_state.mes += 1
  st.rerun()

# Cabecera de días
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
cols_head = st.columns(7)
for idx, dia in enumerate(dias_semana):
  cols_head[idx].markdown(
      f"<div style='text-align:center; font-weight:bold; font-size:11px;'>{dia}</div>",
      unsafe_allow_html=True,
  )

# Grilla de días
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
ciclo = ["DESCANSO", "T1", "T2"]

for idx_sem, semana in enumerate(matriz):
  cols = st.columns(7)
  for idx_dia, dia in enumerate(semana):
    if dia != 0:
      clave = (st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      lbl = f"{dia}\nDesc" if estado == "DESCANSO" else f"{dia}\n{estado}"

      if cols[idx_dia].button(
          lbl, key=f"d_{st.session_state.anio}_{st.session_state.mes}_{dia}"
      ):
        next_idx = (ciclo.index(estado) + 1) % len(ciclo)
        st.session_state.turnos[clave] = ciclo[next_idx]
        guardar_datos()
        st.rerun()

# Cálculo de totales
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
    f"**T1:** {cnt_t1} d | **T2:** {cnt_t2} d | **Desc:** {cnt_desc} d"
)