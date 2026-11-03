import calendar
import datetime
import json
import os
import streamlit as st

# Configuración básica de página
st.set_page_config(
    page_title="Calendario Turnos ARAMARK",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# 1. ESTILOS CSS INQUEBRANTABLES PARA PANTALLA MÓVIL VERTICAL
# -------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Ajustes generales del contenedor principal móvil */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        max-width: 440px !important;
        margin: auto;
    }
    
    /* Ocultar barra superior y footer de Streamlit */
    header, footer, #MainMenu { visibility: hidden !important; height: 0px !important; }
    
    /* Encabezado de navegación de mes */
    .nav-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        margin: 8px 0 12px 0;
        width: 100%;
    }

    .nav-btn {
        background-color: rgba(148, 163, 184, 0.2);
        color: inherit !important;
        text-decoration: none !important;
        padding: 8px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        text-align: center;
        -webkit-tap-highlight-color: transparent;
    }

    .nav-title {
        font-size: 16px;
        font-weight: 800;
        text-align: center;
        flex-grow: 1;
    }

    .today-btn {
        background-color: #10b981;
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 12px;
        text-align: center;
        -webkit-tap-highlight-color: transparent;
    }

    /* GRILLA INQUEBRANTABLE DE 7 COLUMNAS EN CELULAR */
    .calendar-grid {
        display: grid !important;
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 4px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    .header-day {
        text-align: center;
        font-weight: 800;
        font-size: 11px;
        color: #94a3b8;
        padding: 4px 0;
        text-transform: uppercase;
    }

    .empty-cell {
        background: transparent;
        aspect-ratio: 1 / 1.15;
    }

    /* Tarjetas táctiles por día */
    .day-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        aspect-ratio: 1 / 1.15;
        border-radius: 8px;
        text-decoration: none !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-sizing: border-box;
        transition: transform 0.1s ease;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }

    .day-card:active {
        transform: scale(0.90);
    }

    .day-num {
        font-size: 13px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 3px;
    }

    .day-state {
        font-size: 8.5px;
        font-weight: 800;
        text-transform: uppercase;
        line-height: 1;
    }

    /* Colores compatibles con modo claro y oscuro */
    .state-desc {
        background-color: rgba(148, 163, 184, 0.15);
        color: inherit;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }

    .state-t1 {
        background-color: #0284c7;
        color: #ffffff !important;
        border: 1px solid #38bdf8;
        box-shadow: 0 2px 4px rgba(2, 132, 199, 0.25);
    }

    .state-t2 {
        background-color: #ea580c;
        color: #ffffff !important;
        border: 1px solid #fb923c;
        box-shadow: 0 2px 4px rgba(234, 88, 12, 0.25);
    }

    /* Resaltado del día de hoy */
    .is-today {
        outline: 2px solid #10b981;
        outline-offset: -1px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. PERSISTENCIA DE DATOS JSON (CLAVES UNIFICADAS)
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


# Estado inicial
if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True

# -------------------------------------------------------------
# 3. GESTIÓN DE EVENTOS VIA QUERY PARAMS
# -------------------------------------------------------------
params = st.query_params

if "toggle" in params:
  try:
    dia_cliqueado = int(params["toggle"])
    clave = fecha_key(
        st.session_state.anio, st.session_state.mes, dia_cliqueado
    )
    estado_actual = st.session_state.turnos.get(clave, "DESCANSO")
    ciclo = ["DESCANSO", "T1", "T2"]
    siguiente_estado = ciclo[(ciclo.index(estado_actual) + 1) % len(ciclo)]

    st.session_state.turnos[clave] = siguiente_estado
    guardar_datos()
  except Exception:
    pass
  st.query_params.clear()
  st.rerun()

if "nav" in params:
  action = params["nav"]
  if action == "prev":
    if st.session_state.mes == 1:
      st.session_state.mes = 12
      st.session_state.anio -= 1
    else:
      st.session_state.mes -= 1
  elif action == "next":
    if st.session_state.mes == 12:
      st.session_state.mes = 1
      st.session_state.anio += 1
    else:
      st.session_state.mes += 1
  elif action == "hoy":
    hoy = datetime.date.today()
    st.session_state.mes = hoy.month
    st.session_state.anio = hoy.year

  st.query_params.clear()
  st.rerun()

# -------------------------------------------------------------
# 4. ENCABEZADO Y NAVEGACIÓN EN HTML
# -------------------------------------------------------------
st.markdown(
    "<h3 style='text-align: center; margin: 0;'>📅 Turnos ARAMARK</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 11px; margin-bottom: 8px;'>Toca"
    " cualquier día: <b>DESC ➔ T1 ➔ T2</b></p>",
    unsafe_allow_html=True,
)

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
nombre_mes = meses_nombres[st.session_state.mes]

nav_html = f"""
<div class="nav-container">
    <a href="?nav=prev" target="_self" class="nav-btn">◄</a>
    <div class="nav-title">{nombre_mes} {st.session_state.anio}</div>
    <a href="?nav=next" target="_self" class="nav-btn">►</a>
    <a href="?nav=hoy" target="_self" class="today-btn">Hoy</a>
</div>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. GRILLA HTML DEL CALENDARIO (7 COLUMNAS FIJAS)
# -------------------------------------------------------------
html_grid = ['<div class="calendar-grid">']

# Días de la semana
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
for dia_head in dias_semana:
  html_grid.append(f'<div class="header-day">{dia_head}</div>')

# Matriz del mes
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
hoy_fecha = datetime.date.today()

for semana in matriz:
  for dia in semana:
    if dia == 0:
      html_grid.append('<div class="empty-cell"></div>')
    else:
      clave = fecha_key(st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      clase_css = "state-desc"
      txt_estado = "DESC"
      if estado == "T1":
        clase_css = "state-t1"
        txt_estado = "T1"
      elif estado == "T2":
        clase_css = "state-t2"
        txt_estado = "T2"

      es_hoy = (
          st.session_state.anio == hoy_fecha.year
          and st.session_state.mes == hoy_fecha.month
          and dia == hoy_fecha.day
      )
      clase_hoy = " is-today" if es_hoy else ""

      html_grid.append(f"""
                <a href="?toggle={dia}" target="_self" class="day-card {clase_css}{clase_hoy}">
                    <span class="day-num">{dia}</span>
                    <span class="day-state">{txt_estado}</span>
                </a>
            """)

html_grid.append("</div>")
st.markdown("".join(html_grid), unsafe_allow_html=True)

# -------------------------------------------------------------
# 6. RESUMEN Y MÉTRICAS DE TURNO
# -------------------------------------------------------------
cnt_t1, cnt_t2, cnt_desc = 0, 0, 0
dias_mes = calendar.monthrange(st.session_state.anio, st.session_state.mes)[1]

for d in range(1, dias_mes + 1):
  k = fecha_key(st.session_state.anio, st.session_state.mes, d)
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

col_s1, col_s2 = st.columns(2)
with col_s1:
  st.metric("Total Horas", f"{total_hrs:.1f} hrs")
with col_s2:
  st.metric("Días Trabajados", f"{cnt_t1 + cnt_t2} d", delta=f"{cnt_desc}d desc")

st.caption(
    f"🔵 **T1 ({st.session_state.hrs_t1:g}h):** {cnt_t1} d | 🟠 **T2"
    f" ({st.session_state.hrs_t2:g}h):** {cnt_t2} d | **Descansos:**"
    f" {cnt_desc} d"
)

# -------------------------------------------------------------
# 7. PANEL CONFIGURACIÓN (DESPLEGABLE)
# -------------------------------------------------------------
with st.expander("⚙️ Ajuste de Horas", expanded=False):
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