import calendar
import datetime
import streamlit as st

st.set_page_config(
    page_title="Calendario ARAMARK", page_icon="📅", layout="centered"
)

st.title("📅 Gestor de Turnos y Horas")

# Configuración de horas por turno
col_hrs1, col_hrs2 = st.columns(2)
with col_hrs1:
  hrs_t1 = st.number_input("Horas Turno 1 (T1)", value=8.0, step=0.5)
with col_hrs2:
  hrs_t2 = st.number_input("Horas Turno 2 (T2)", value=8.0, step=0.5)

# Inicializar variables de estado
if "mes" not in st.session_state:
  st.session_state.mes = datetime.date.today().month
if "anio" not in st.session_state:
  st.session_state.anio = datetime.date.today().year
if "turnos" not in st.session_state:
  st.session_state.turnos = {}

# Navegación entre meses
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
if col_m1.button("◄ Anterior"):
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
    f"<h3 style='text-align: center;'>{meses[st.session_state.mes]} {st.session_state.anio}</h3>",
    unsafe_allow_html=True,
)

if col_m3.button("Siguiente ►"):
  if st.session_state.mes == 12:
    st.session_state.mes = 1
    st.session_state.anio += 1
  else:
    st.session_state.mes += 1
  st.rerun()

# Cabecera de días
dias_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
cols_head = st.columns(7)
for idx, dia in enumerate(dias_semana):
  cols_head[idx].markdown(f"**{dia}**")

# Matriz del calendario
matriz = calendar.monthcalendar(st.session_state.anio, st.session_state.mes)
ciclo = ["DESCANSO", "T1", "T2"]

for semana in matriz:
  cols = st.columns(7)
  for idx, dia in enumerate(semana):
    if dia != 0:
      clave = (st.session_state.anio, st.session_state.mes, dia)
      estado = st.session_state.turnos.get(clave, "DESCANSO")

      # Etiqueta visible
      txt_btn = f"{dia}\n{estado}"
      if cols[idx].button(
          txt_btn, key=f"btn_{st.session_state.anio}_{st.session_state.mes}_{dia}"
      ):
        next_idx = (ciclo.index(estado) + 1) % len(ciclo)
        st.session_state.turnos[clave] = ciclo[next_idx]
        st.rerun()

# Conteo de horas
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

total_hrs = (cnt_t1 * hrs_t1) + (cnt_t2 * hrs_t2)

st.divider()
st.metric("Total Horas Trabajadas en el Mes", f"{total_hrs:.1f} hrs")
st.info(
    f"**Días T1:** {cnt_t1}  |  **Días T2:** {cnt_t2}  |  **Descansos:**"
    f" {cnt_desc}"
)