import calendar
import datetime
import json
import streamlit as st
import streamlit.components.v1 as components

# -------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
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
    /* Ajuste de contenedor móvil sin romper el layout nativo */
    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 1rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 480px !important;
        margin: auto;
    }
    header, footer, #MainMenu { display: none !important; }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# 2. COMPONENTE WEB INTERACTIVO (JS + CSS GRID 7 COLUMNAS)
# -------------------------------------------------------------
HTML_CALENDARIO = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
  }
  body {
    margin: 0;
    padding: 0;
    background-color: transparent;
    color: #f8fafc;
  }
  .app-card {
    background: #0f172a;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    border: 1px solid #1e293b;
  }
  .header {
    text-align: center;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 2px;
  }
  .sub-header {
    text-align: center;
    font-size: 11px;
    color: #94a3b8;
    margin-bottom: 12px;
  }
  .nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    gap: 4px;
  }
  .nav-btn {
    background: #334155;
    color: #fff;
    border: none;
    padding: 8px 14px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 13px;
    cursor: pointer;
  }
  .nav-btn:active { transform: scale(0.93); }
  .today-btn {
    background: #10b981;
    color: #fff;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 11px;
    cursor: pointer;
  }
  .title-mes {
    font-size: 15px;
    font-weight: 800;
    text-align: center;
    flex-grow: 1;
  }
  
  /* GRILLA 7 COLUMNAS IMPOSIBLE DE COLAPSAR EN MÓVIL */
  .grid-calendar {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 4px !important;
    width: 100% !important;
  }
  .day-head {
    text-align: center;
    font-size: 11px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    padding: 4px 0;
  }
  .day-cell {
    aspect-ratio: 1 / 1.15;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.05s ease, background 0.15s ease;
  }
  .day-cell:active { transform: scale(0.90); }
  .day-num { font-size: 13px; font-weight: 800; line-height: 1; }
  .day-state { font-size: 8.5px; font-weight: 800; text-transform: uppercase; margin-top: 3px; line-height: 1; }
  .empty-cell { aspect-ratio: 1 / 1.15; }

  /* COLORES DE TURNOS */
  .DESC { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }
  .T1 { background: #0284c7; color: #ffffff; border: 1px solid #38bdf8; box-shadow: 0 2px 4px rgba(2,132,199,0.3); }
  .T2 { background: #ea580c; color: #ffffff; border: 1px solid #fb923c; box-shadow: 0 2px 4px rgba(234,88,12,0.3); }
  .is-today { outline: 2px solid #10b981; outline-offset: -1px; }

  /* MÉTRICAS EN TIEMPO REAL */
  .metrics-box {
    display: flex;
    justify-content: space-around;
    background: #1e293b;
    border-radius: 8px;
    padding: 10px;
    margin-top: 14px;
    border: 1px solid #334155;
  }
  .metric-item { text-align: center; }
  .metric-val { font-size: 18px; font-weight: 800; color: #38bdf8; }
  .metric-lbl { font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
</style>
</head>
<body>

<div class="app-card">
  <div class="header">📅 Turnos ARAMARK</div>
  <div class="sub-header">Toca cualquier día: <b>DESC ➔ T1 ➔ T2</b></div>

  <div class="nav-bar">
    <button class="nav-btn" id="prevBtn">◄</button>
    <div class="title-mes" id="mesTitle"></div>
    <button class="nav-btn" id="nextBtn">►</button>
    <button class="today-btn" id="todayBtn">Hoy</button>
  </div>

  <div class="grid-calendar" id="gridCalendar"></div>

  <div class="metrics-box">
    <div class="metric-item">
      <div class="metric-val" id="totalHrs">0 hrs</div>
      <div class="metric-lbl">Total Horas</div>
    </div>
    <div class="metric-item">
      <div class="metric-val" style="color:#10b981;" id="totalDias">0 d</div>
      <div class="metric-lbl">Trabajados</div>
    </div>
    <div class="metric-item">
      <div class="metric-val" style="color:#94a3b8;" id="totalDesc">0 d</div>
      <div class="metric-lbl">Descansos</div>
    </div>
  </div>
</div>

<script>
  const mesesNombres = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  const diasNombres = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"];
  
  let fechaActual = new Date();
  let mesSel = fechaActual.getMonth() + 1;
  let anioSel = fechaActual.getFullYear();
  let hrsT1 = 8.0;
  let hrsT2 = 8.0;

  // Cargar turnos guardados localmente en el celular
  let turnos = JSON.parse(localStorage.getItem('aramark_turnos') || '{}');

  function guardarTurnos() {
    localStorage.setItem('aramark_turnos', JSON.stringify(turnos));
  }

  function getClave(y, m, d) {
    return `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
  }

  function renderizar() {
    document.getElementById('mesTitle').innerText = `${mesesNombres[mesSel]} ${anioSel}`;
    const grid = document.getElementById('gridCalendar');
    grid.innerHTML = '';

    // Headers días
    diasNombres.forEach(d => {
      const h = document.createElement('div');
      h.className = 'day-head';
      h.innerText = d;
      grid.appendChild(h);
    });

    // Calcular días del mes
    const primerDia = new Date(anioSel, mesSel - 1, 1).getDay();
    // Ajustar domingo=0 a lunes=0
    const offset = (primerDia === 0 ? 6 : primerDia - 1);
    const totalDias = new Date(anioSel, mesSel, 0).getDate();

    for (let i = 0; i < offset; i++) {
      const emp = document.createElement('div');
      emp.className = 'empty-cell';
      grid.appendChild(emp);
    }

    let cntT1 = 0, cntT2 = 0, cntDesc = 0;
    const hoy = new Date();

    for (let d = 1; d <= totalDias; d++) {
      const clave = getClave(anioSel, mesSel, d);
      const estado = turnos[clave] || 'DESCANSO';

      if (estado === 'T1') cntT1++;
      else if (estado === 'T2') cntT2++;
      else cntDesc++;

      const cell = document.createElement('div');
      const esHoy = (hoy.getFullYear() === anioSel && (hoy.getMonth() + 1) === mesSel && hoy.getDate() === d);
      cell.className = `day-cell ${estado} ${esHoy ? 'is-today' : ''}`;

      cell.innerHTML = `
        <span class="day-num">${d}</span>
        <span class="day-state">${estado === 'DESCANSO' ? 'DESC' : estado}</span>
      `;

      // Cambio instantáneo de turno sin reload
      cell.onclick = () => {
        const ciclo = ['DESCANSO', 'T1', 'T2'];
        const actual = turnos[clave] || 'DESCANSO';
        turnos[clave] = ciclo[(ciclo.indexOf(actual) + 1) % ciclo.length];
        guardarTurnos();
        renderizar();
      };

      grid.appendChild(cell);
    }

    // Actualizar métricas
    const totalHoras = (cntT1 * hrsT1) + (cntT2 * hrsT2);
    document.getElementById('totalHrs').innerText = `${totalHoras.toFixed(1)} h`;
    document.getElementById('totalDias').innerText = `${cntT1 + cntT2} d`;
    document.getElementById('totalDesc').innerText = `${cntDesc} d`;
  }

  document.getElementById('prevBtn').onclick = () => {
    if (mesSel === 1) { mesSel = 12; anioSel--; }
    else { mesSel--; }
    renderizar();
  };

  document.getElementById('nextBtn').onclick = () => {
    if (mesSel === 12) { mesSel = 1; anioSel++; }
    else { mesSel++; }
    renderizar();
  };

  document.getElementById('todayBtn').onclick = () => {
    const h = new Date();
    mesSel = h.getMonth() + 1;
    anioSel = h.getFullYear();
    renderizar();
  };

  renderizar();
</script>
</body>
</html>
"""

# Renderizado dentro de Streamlit (sin recargas de pantalla)
components.html(HTML_CALENDARIO, height=520, scrolling=False)