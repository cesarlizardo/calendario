import calendar
import datetime
import json
import os
import streamlit as st

# -------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS ADAPTATIVOS (MOBILE-FIRST)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Calendario Turnos ARAMARK",
    page_icon="📅",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* Reset de contenedor principal para móviles */
    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 480px !important;
        margin: auto;
    }
    
    /* Ocultar elementos nativos de barra superior y footer */
    header[data-testid="stHeader"], footer, #MainMenu {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* FORZAR 7 COLUMNAS EN UNA FILA HORIZONTAL (Evita apilamiento en smartphones) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 3px !important;
        margin-bottom: 3px !important;
    }

    [data-testid="column"] {
        flex: 1 1 0% !important;
        width: 14.28% !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    /* Estilo base de los botones-tarjeta del calendario */
    [data-testid="stColumn"] button {
        width: 100% !important;
        min-height: 48px !important;
        height: 48px !important;
        padding: 2px 0px !important;
        margin: 0 !important;
        border-radius: 8px !important;
        font-size: 11px !important;
        line-height: 1.15 !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        text-align: center !important;
        white-space: pre-wrap !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
        transition: transform 0.1s ease, background-color 0.15s ease !important;
        -webkit-tap-highlight-color: transparent !important;
    }

    /* Feedback táctil al presionar en la pantalla del celular */
    [data-testid="stColumn"] button:active {
        transform: scale(0.91) !important;
    }

    [data-testid="stColumn"] button p {
        font-size: 11px !important;
        line-height: 1.15 !important;
        margin: 0 !important;
        font-weight: 700 !important;
    }

    /* ESQUEMA DE COLORES DINÁMICOS POR ESTADO DE TURNO */
    /* Descanso (Gris Slated) */
    [data-testid="stColumn"] button[aria-label*="DESC"] {
        background-color: #f1f5f9 !important;
        color: #475569 !important;
        border: 1.5px solid #cbd5e1 !important;
    }

    /* Turno 1 (Azul Celeste) */
    [data-testid="stColumn"] button[aria-label*="T1"] {
        background-color: #e0f2fe !important;
        color: #0369a1 !important;
        border: 1.5px solid #7dd3fc !important;
    }

    /* Turno 2 (Naranja Cálido) */
    [data-testid="stColumn"] button[aria-label*="T2"] {
        background-color: #ffedd5 !important;
        color: #c2410c !important;
        border: 1.5px solid #fdba74 !important;
    }

    /* Resaltado del Día Actual (Anillo Verde Esmeralda) */
    [data-testid="stColumn"] button[aria-label*="★"] {
        box-shadow: 0 0 0 2.5px #10b981, 0 2px 4px rgba(16, 185, 129, 0.25) !important;
    }

    /* Encabezados de días de la semana */
    .day-header {
        text-align: center;
        font-weight: 800;
        font-size: 11px;
        color: #64748b;
        padding: 4px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Celda vacía de alineación */
    .empty-day {
        height: 48px;
        width: 100%;
        background: transparent;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. PERSISTENCIA DE DATOS Y FUNCIONES AUXILIARES
# -------------------------------------------------------------
ARCHIVO_DATOS = "turnos.json"


def fecha_key(anio: int, mes: int, dia: int) -> str:
  """Genera una clave ISO unificada 'YYYY-MM-DD'."""
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
  try:
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
      json.dump(datos, f, ensure_ascii=False, indent=2)
  except Exception as e:
    st.error(f"Error al guardar datos: {e}")


# Inicialización de estado en Session State
if "cargado" not in st.session_state:
  turnos, h1, h2 = cargar_datos()
  st.session_state.turnos = turnos
  st.session_state.hrs_t1 = h1
  st.session_state.hrs_t2 = h2
  st.session_state.mes = datetime.date.today().month
  st.session_state.anio = datetime.date.today().year
  st.session_state.cargado = True


# Callback para alternar el turno instantáneamente sin recargar la URL
def toggle_turno(fecha_str: str):
  ciclo = ["DESCANSO", "T1", "T2"]
  actual = st.session_state.turnos.get(fecha_str, "DESCANSO")
  siguiente = ciclo[(ciclo.index(actual) + 1) % len(ciclo)]
  st.session_state.turnos[fecha_str] = siguiente
  guardar_datos()


# Callbacks de navegación de meses
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
  st.session_state.mes = hoy.month
  st.session_state.anio = hoy.year


# -------------------------------------------------------------
# 3. ENCABEZADO Y NAVEGACIÓN
# -------------------------------------------------------------
st.markdown(
    "<h3 style='text-align: center; margin: 0 0 2px 0;'>📅 Turnos ARAMARK</h3>",
    unsafe_allow_html=True,
)
st.caption(
    "<p style='text-align: center; margin-bottom: 8px;'>Toca cualquier día para"
    " cambiar: <b>DESC ➔ T1 ➔ T2</b></p>",
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

col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 3, 1, 1])

with col_nav1:
  st.button("◄", on_click=prev_mes, key="btn_prev", use_container_width=True)

with col_nav2:
  nombre_mes = meses_nombres[st.session_state.mes]
  st.markdown(
      f"<h4 style='text-align: center; margin: 4px 0;'>"
      f"{nombre_mes} {st.session_state.anio}</h4>",
      unsafe_allow_html=True,
  )

with col_nav3:
  st.button("►", on_click=next_mes, key="btn_next", use_container_width=True)

with col_nav4:
  st.button("Hoy", on_click=ir_hoy, key="btn_today", use_container_width=True)

# -------------------------------------------------------------
# 4. MATRIZ DEL CALENDARIO (7 COLUMNAS)
# -------------------------------------------------------------
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

# Fila de nombres de días
cols_header = st.columns(7)
for idx, dia_head in enumerate(dias_semana):
  cols_header[idx].markdown(
      f'<div class="day-header">{dia_head}</div>', unsafe_allow_html=True
  )

# Generación del mes
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
hoy_fecha = datetime.date.today()

for semana in matriz:
  cols = st.columns(7)
  for idx, dia in enumerate(semana):
    if dia == 0:
      cols[idx].markdown('<div class="empty-day"></div>', unsafe_allow_html=True)
    else:
      fecha_str = fecha_key(st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(fecha_str, "DESCANSO")

      txt_estado = "DESC"
      if estado == "T1":
        txt_estado = "T1"
      elif estado == "T2":
        txt_estado = "T2"

      # Resaltado si el día es hoy
      es_hoy = (
          st.session_state.anio == hoy_fecha.year
          and st.session_state.mes == hoy_fecha.month
          and dia == hoy_fecha.day
      )
      marker = "★" if es_hoy else ""

      label_button = f"{dia}{marker}\n{txt_estado}"

      cols[idx].button(
          label_button,
          key=f"day_{fecha_str}",
          on_click=toggle_turno,
          args=(fecha_str,),
      )

# -------------------------------------------------------------
# 5. RESUMEN DE HORAS Y DÍAS TRABAJADOS
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

total_hrs_t1 = cnt_t1 * st.session_state.hrs_t1
total_hrs_t2 = cnt_t2 * st.session_state.hrs_t2
total_hrs = total_hrs_t1 + total_hrs_t2

st.divider()

col_m1, col_m2 = st.columns(2)
with col_m1:
  st.metric("Total Horas", f"{total_hrs:.1f} hrs")
with col_m2:
  st.metric(
      "Días Trabajados",
      f"{cnt_t1 + cnt_t2} d",
      delta=f"Descansos: {cnt_desc}d",
      delta_color="normal",
  )

st.caption(
    f"🔵 **T1 ({st.session_state.hrs_t1:g}h):** {cnt_t1} d ({total_hrs_t1:.1f}h)"
    f" | 🟠 **T2 ({st.session_state.hrs_t2:g}h):** {cnt_t2} d"
    f" ({total_hrs_t2:.1f}h)"
)

# -------------------------------------------------------------
# 6. HERRAMIENTAS Y CONFIGURACIÓN (HERRAMIENTAS RÁPIDAS)
# -------------------------------------------------------------
with st.expander("⚙️ Configuración de Horas y Rota Rápida", expanded=False):
  st.markdown("##### ⏱️ Horas por Turno")
  c_h1, c_h2 = st.columns(2)
  with c_h1:
    h1_val = st.number_input(
        "Hrs T1",
        value=st.session_state.hrs_t1,
        step=0.5,
        min_value=0.0,
        key="input_h1",
    )
    if h1_val != st.session_state.hrs_t1:
      st.session_state.hrs_t1 = h1_val
      guardar_datos()

  with c_h2:
    h2_val = st.number_input(
        "Hrs T2",
        value=st.session_state.hrs_t2,
        step=0.5,
        min_value=0.0,
        key="input_h2",
    )
    if h2_val != st.session_state.hrs_t2:
      st.session_state.hrs_t2 = h2_val
      guardar_datos()

  st.divider()
  st.markdown("##### 🔄 Llenado Automático de Rota")
  st.caption("Aplica una secuencia periódica para todo este mes:")

  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    dias_t1 = st.number_input("Días T1", min_value=0, value=4, step=1)
  with col_p2:
    dias_t2 = st.number_input("Días T2", min_value=0, value=0, step=1)
  with col_p3:
    dias_desc = st.number_input("Días Desc", min_value=0, value=2, step=1)

  if st.button("Aplicar Patrón al Mes", use_container_width=True):
    patron = []
    patron.extend(["T1"] * int(dias_t1))
    patron.extend(["T2"] * int(dias_t2))
    patron.extend(["DESCANSO"] * int(dias_desc))

    if patron:
      for d in range(1, dias_mes + 1):
        k = fecha_key(st.session_state.anio, st.session_state.mes, d)
        idx_patron = (d - 1) % len(patron)
        st.session_state.turnos[k] = patron[idx_patron]
      guardar_datos()
      st.rerun()

  st.divider()
  if st.button("🗑️ Resetear Mes a Descanso", use_container_width=True):
    for d in range(1, dias_mes + 1):
      k = fecha_key(st.session_state.anio, st.session_state.mes, d)
      st.session_state.turnos[k] = "DESCANSO"
    guardar_datos()
    st.rerun()