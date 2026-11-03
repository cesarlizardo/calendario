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
# 2. PERSISTENCIA DE DATOS (JSON)
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
# 3. INTERACCIÓN POR QUERY PARAMS (CLICS RÁPIDOS)
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
    siguiente = ciclo[(ciclo.index(estado_actual) + 1) % len(ciclo)]
    st.session_state.turnos[clave] = siguiente
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
# 4. RENDERIZADO DEL CALENDARIO (UN SOLO BLOQUE HTML/CSS)
# -------------------------------------------------------------
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
hoy_fecha = datetime.date.today()

matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]

html_content = [f"""
<style>
/* Forzar ajuste responsivo en smartphones */
.block-container {{
    padding-top: 0.6rem !important;
    padding-bottom: 1rem !important;
    padding-left: 0.3rem !important;
    padding-right: 0.3rem !important;
    max-width: 440px !important;
    margin: auto;
}}

/* Ocultar barra de Streamlit */
header, footer, #MainMenu {{
    display: none !important;
}}

/* Encabezado */
.app-title {{
    text-align: center;
    font-size: 18px;
    font-weight: 800;
    margin: 0 0 2px 0;
}}
.app-subtitle {{
    text-align: center;
    font-size: 11px;
    color: #94a3b8;
    margin-bottom: 8px;
}}

/* Barra de navegación de meses */
.cal-nav {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 8px !important;
    gap: 4px;
}}

.cal-nav-btn {{
    background-color: #334155;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
    text-align: center;
    -webkit-tap-highlight-color: transparent;
}}

.cal-today-btn {{
    background-color: #10b981;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 6px 10px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11px;
    text-align: center;
    -webkit-tap-highlight-color: transparent;
}}

.cal-nav-title {{
    font-size: 15px;
    font-weight: 800;
    text-align: center;
    flex-grow: 1;
}}

/* GRILLA HTML INDESTRUCTIBLE DE 7 COLUMNAS EN MÓVIL */
.cal-grid {{
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 3px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}}

.cal-head-day {{
    text-align: center;
    font-weight: 800;
    font-size: 11px;
    color: #94a3b8;
    padding: 4px 0;
    text-transform: uppercase;
}}

.cal-empty {{
    width: 100%;
    height: 46px;
    background: transparent;
}}

.cal-card {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    height: 46px !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    box-sizing: border-box !important;
    -webkit-tap-highlight-color: transparent !important;
    transition: transform 0.08s ease;
    user-select: none;
}}

.cal-card:active {{
    transform: scale(0.92);
}}

.cal-num {{
    font-size: 12px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 2px;
}}

.cal-state {{
    font-size: 8px;
    font-weight: 800;
    text-transform: uppercase;
    line-height: 1;
}}

/* ESTADOS DE COLORES (Alta Visibilidad) */
.st-desc {{
    background-color: #1e293b;
    color: #cbd5e1 !important;
    border: 1px solid #334155;
}}

.st-t1 {{
    background-color: #0284c7;
    color: #ffffff !important;
    border: 1px solid #38bdf8;
    box-shadow: 0 1px 3px rgba(2, 132, 199, 0.4);
}}

.st-t2 {{
    background-color: #ea580c;
    color: #ffffff !important;
    border: 1px solid #fb923c;
    box-shadow: 0 1px 3px rgba(234, 88, 12, 0.4);
}}

.is-today {{
    box-shadow: 0 0 0 2px #10b981 !important;
}}
</style>

<div class="app-title">📅 Turnos ARAMARK</div>
<div class="app-subtitle">Toca cualquier día para alternar: <b>DESC ➔ T1 ➔ T2</b></div>

<div class="cal-nav">
    <a href="?nav=prev" target="_self" class="cal-nav-btn">◄</a>
    <div class="cal-nav-title">{nombre_mes} {st.session_state.anio}</div>
    <a href="?nav=next" target="_self" class="cal-nav-btn">►</a>
    <a href="?nav=hoy" target="_self" class="cal-today-btn">Hoy</a>
</div>

<div class="cal-grid">
"""]

# Encabezado días de la semana
for d in dias_semana:
  html_content.append(f'<div class="cal-head-day">{d}</div>')

# Días del mes
for semana in matriz:
  for dia in semana:
    if dia == 0:
      html_content.append('<div class="cal-empty"></div>')
    else:
      clave = fecha_key(st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      clase_css = "st-desc"
      txt_estado = "DESC"
      if estado == "T1":
        clase_css = "st-t1"
        txt_estado = "T1"
      elif estado == "T2":
        clase_css = "st-t2"
        txt_estado = "T2"

      es_hoy = (
          st.session_state.anio == hoy_fecha.year
          and st.session_state.mes == hoy_fecha.month
          and dia == hoy_fecha.day
      )
      clase_hoy = " is-today" if es_hoy else ""

      html_content.append(f"""
                <a href="?toggle={dia}" target="_self" class="cal-card {clase_css}{clase_hoy}">
                    <span class="cal-num">{dia}</span>
                    <span class="cal-state">{txt_estado}</span>
                </a>
            """)

html_content.append("</div>")

# Renderizar TODO en un único bloque de HTML
st.markdown("".join(html_content), unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. RESUMEN Y MÉTRICAS DE HORAS
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
    f" ({st.session_state.hrs_t2:g}h):** {cnt_t2} d | ⚪ **Desc:** {cnt_desc} d"
)

# -------------------------------------------------------------
# 6. CONFIGURACIÓN Y ROTAS AUTOMÁTICAS
# -------------------------------------------------------------
with st.expander("⚙️ Ajustes de Horas y Llenado Rápido", expanded=False):
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

  st.markdown("---")
  st.markdown("**Generar Rota Automática:**")
  cp1, cp2, cp3 = st.columns(3)
  dt1 = cp1.number_input("Días T1", min_value=0, value=4, step=1, key="rot_t1")
  dt2 = cp2.number_input("Días T2", min_value=0, value=0, step=1, key="rot_t2")
  ddesc = cp3.number_input(
      "Días Desc", min_value=0, value=2, step=1, key="rot_desc"
  )

  if st.button("Aplicar Rota al Mes", use_container_width=True):
    patron = []
    patron.extend(["T1"] * int(dt1))
    patron.extend(["T2"] * int(dt2))
    patron.extend(["DESCANSO"] * int(ddesc))
    if patron:
      for d in range(1, dias_mes + 1):
        k = fecha_key(st.session_state.anio, st.session_state.mes, d)
        st.session_state.turnos[k] = patron[(d - 1) % len(patron)]
      guardar_datos()
      st.rerun()