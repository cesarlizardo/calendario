import calendar
import datetime
import json
import os
import streamlit as st

st.set_page_config(
    page_title="Calendario ARAMARK",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 1. CSS PARA FORZAR GRILLA DE 7 COLUMNAS EN PANTALLAS MÓVILES
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Evita que Streamlit apile las 7 columnas verticalmente en móviles */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
        padding: 0px !important;
    }
    /* Estilo tipo cuadrícula táctil para botones */
    div.stButton > button {
        width: 100% !important;
        padding: 4px 1px !important;
        font-size: 10px !important;
        font-weight: bold !important;
        line-height: 1.1 !important;
        white-space: pre-wrap !important;
        height: 52px !important;
        border-radius: 6px !important;
        margin: 0px !important;
    }
    /* Maximizar área útil en iPhone */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. PERSISTENCIA DE DATOS (GUARDADO EN ARCHIVO JSON)
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


# Cargar datos guardados previamente
if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True

# -------------------------------------------------------------
# 3. INTERFAZ GRÁFICA
# -------------------------------------------------------------
st.title("📅 Calendario Turnos")

# Horas configurables por turno
col_h1, col_h2 = st.columns(2)
with col_h1:
  h1_val = st.number_input(
      "Hrs Turno 1", value=st.session_state.hrs_t1, step=0.5
  )
  if h1_val != st.session_state.hrs_t1:
    st.session_state.hrs_t1 = h1_val
    guardar_datos()

with col_h2:
  h2_val = st.number_input(
      "Hrs Turno 2", value=st.session_state.hrs_t2, step=0.5
  )
  if h2_val != st.session_state.hrs_t2:
    st.session_state.hrs_t2 = h2_val
    guardar_datos()

# Navegación entre meses
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
if col_m1.button("◄"):
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
    f"<h4 style='text-align: center; margin:0;'>{meses[st.session_state.mes]} {st.session_state.anio}</h4>",
    unsafe_allow_html=True,
)

if col_m3.button("►"):
  if st.session_state.mes == 12:
    st.session_state.mes = 1
    st.session_state.anio += 1
  else:
    st.session_state.mes += 1
  st.rerun()

# Encabezados de días de la semana
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
cols_head = st.columns(7)
for idx, dia in enumerate(dias_semana):
  cols_head[idx].markdown(
      f"<p style='text-align:center; font-weight:bold; margin:0;'>{dia}</p>",
      unsafe_allow_html=True,
  )

# Grilla mensual
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
ciclo = ["DESCANSO", "T1", "T2"]

for semana in matriz:
  cols = st.columns(7)
  for idx, dia in enumerate(semana):
    if dia != 0:
      clave = (st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      lbl = f"{dia}\nDesc" if estado == "DESCANSO" else f"{dia}\n{estado}"

      if cols[idx].button(
          lbl, key=f"btn_{st.session_state.anio}_{st.session_state.mes}_{dia}"
      ):
        next_idx = (ciclo.index(estado) + 1) % len(ciclo)
        st.session_state.turnos[clave] = ciclo[next_idx]
        guardar_datos()
        st.rerun()

# Totales y cálculo
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
    f"**T1:** {cnt_t1} días  |  **T2:** {cnt_t2} días  |  **Descansos:**"
    f" {cnt_desc} días"
)