import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta, date

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Control de Assets — Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# SERVICENOW COLORS
# =========================
SN_GREEN = "#81B5A1"
SN_DARK_GREEN = "#2E5E4E"
SN_NAVY = "#1F2430"
SN_BLUE = "#4B70F5"
SN_ORANGE = "#F59E0B"
SN_RED = "#D95C5C"
SN_BG = "#F5F7FA"
SN_CARD = "#FFFFFF"
SN_BORDER = "#D9E2EC"
SN_TEXT = "#1F2937"
SN_MUTED = "#6B7280"
SN_LIGHT_GRAY = "#CBD5E1"
SN_PANEL_BG = "#F8FAFC"

# =========================
# STYLES
# =========================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {SN_BG};
        color: {SN_TEXT};
    }}
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 1.5rem;
        max-width: 1400px;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {SN_NAVY} 0%, #262d3c 100%);
        border-right: 1px solid #31384a;
    }}
    section[data-testid="stSidebar"] * {{
        color: #f8fafc !important;
    }}
    .metric-card {{
        background: {SN_CARD};
        border: 1px solid {SN_BORDER};
        border-radius: 18px;
        padding: 18px 20px;
        min-height: 120px;
        box-shadow: 0 8px 24px rgba(31, 36, 48, 0.06);
    }}
    .metric-label {{
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: {SN_MUTED};
        margin-bottom: 10px;
        font-weight: 700;
    }}
    .metric-value {{
        font-size: 34px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 8px;
    }}
    .metric-sub {{
        font-size: 12px;
        color: {SN_MUTED};
    }}
    .panel {{
        background: {SN_CARD};
        border: 1px solid {SN_BORDER};
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(31, 36, 48, 0.05);
    }}
    .section-title {{
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: {SN_DARK_GREEN};
        margin-bottom: 12px;
        font-weight: 800;
    }}
    .small-note {{
        color: {SN_MUTED};
        font-size: 13px;
    }}
    .stDownloadButton > button, .stButton > button {{
        background: {SN_DARK_GREEN};
        color: white;
        border-radius: 12px;
        border: 1px solid {SN_DARK_GREEN};
        font-weight: 700;
    }}
    .stDownloadButton > button:hover, .stButton > button:hover {{
        background: {SN_GREEN};
        border-color: {SN_GREEN};
        color: white;
    }}
    div[data-baseweb="select"] > div {{
        border-radius: 12px;
        border-color: {SN_BORDER};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# DATA
# =========================
PROJECT_START = date(2026, 3, 16)
DEADLINE = date(2026, 6, 12)
WEEKS = 13

PHASES = {
    "disc": {"label": "Descubrimiento", "color": "#2E5E4E"},
    "comm": {"label": "Comunicación",   "color": "#4B70F5"},
    "dis":  {"label": "Diseño",         "color": "#81B5A1"},
    "dev":  {"label": "Desarrollo",     "color": "#334155"},
    "test": {"label": "Pruebas",        "color": "#F59E0B"},
    "dep":  {"label": "Despliegue",     "color": "#D95C5C"},
}

TASKS = [
    {"id": 1,  "name": "Mapeo situación actual",             "phase": "disc", "start": 0,  "end": 2,  "pilot": False},
    {"id": 2,  "name": "Levantamiento de requisitos",        "phase": "disc", "start": 0,  "end": 2,  "pilot": False},
    {"id": 3,  "name": "Plan de comunicación (4 oficinas)",  "phase": "comm", "start": 1,  "end": 3,  "pilot": False},
    {"id": 4,  "name": "Diseño flujo registro (QR)",         "phase": "dis",  "start": 2,  "end": 4,  "pilot": False},
    {"id": 5,  "name": "Diseño roles Colaborador/Vigilante", "phase": "dis",  "start": 2,  "end": 4,  "pilot": False},
    {"id": 6,  "name": "Config. módulo ServiceNow",          "phase": "dev",  "start": 4,  "end": 7,  "pilot": False},
    {"id": 7,  "name": "Registro salida/entrada vía QR",     "phase": "dev",  "start": 5,  "end": 8,  "pilot": False},
    {"id": 8,  "name": "Reporte mensual de salidas",         "phase": "dev",  "start": 6,  "end": 9,  "pilot": False},
    {"id": 9,  "name": "Geolocalización de assets",          "phase": "dev",  "start": 7,  "end": 10, "pilot": False},
    {"id": 10, "name": "Pruebas piloto — Up Now",            "phase": "test", "start": 9,  "end": 11, "pilot": True},
    {"id": 11, "name": "Pruebas Casa Blanca + Rectoría",     "phase": "test", "start": 10, "end": 12, "pilot": False},
    {"id": 12, "name": "Go-live & comunicado final",         "phase": "dep",  "start": 12, "end": 13, "pilot": False},
]

STATUS_LABELS = {
    "pending": "Pendiente",
    "inprogress": "En progreso",
    "done": "Completada"
}

STATUS_EMOJI = {
    "pending": "⬜",
    "inprogress": "🔄",
    "done": "✅"
}

STATUS_COLORS = {
    "pending": SN_BLUE,
    "inprogress": SN_ORANGE,
    "done": SN_GREEN,
}

# =========================
# SESSION STATE
# =========================
if "statuses" not in st.session_state:
    st.session_state.statuses = {t["id"]: "pending" for t in TASKS}

# =========================
# HELPERS
# =========================
def week_start(week_index: int) -> date:
    return PROJECT_START + timedelta(days=week_index * 7)


def week_end_from_index(end_index: int) -> date:
    if end_index >= WEEKS:
        return DEADLINE
    return week_start(end_index)


def week_label(week_index: int) -> str:
    d = week_start(week_index)
    return d.strftime("%d %b")


def weeks_left() -> int:
    today = date.today()
    delta_days = (DEADLINE - today).days
    return max(0, (delta_days + 6) // 7)


def get_stats():
    statuses = st.session_state.statuses
    done = sum(1 for t in TASKS if statuses[t["id"]] == "done")
    prog = sum(1 for t in TASKS if statuses[t["id"]] == "inprogress")
    pend = sum(1 for t in TASKS if statuses[t["id"]] == "pending")
    total = len(TASKS)
    pct = round(done / total * 100) if total else 0
    return done, prog, pend, total, pct


def build_task_df() -> pd.DataFrame:
    rows = []
    for t in TASKS:
        start_date = week_start(t["start"])
        end_date = week_end_from_index(t["end"])
        duration_weeks = t["end"] - t["start"]
        rows.append({
            "ID": t["id"],
            "Tarea": t["name"] + (" [PILOTO]" if t["pilot"] else ""),
            "Fase": PHASES[t["phase"]]["label"],
            "FaseKey": t["phase"],
            "InicioSemana": t["start"] + 1,
            "FinSemana": t["end"],
            "InicioFecha": pd.to_datetime(start_date),
            "FinFecha": pd.to_datetime(end_date),
            "InicioTxt": start_date.strftime("%d %b %Y"),
            "FinTxt": end_date.strftime("%d %b %Y"),
            "RangoCorto": f"{start_date.strftime('%d %b')} → {end_date.strftime('%d %b')}",
            "RangoLargo": f"{start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}",
            "DuracionSemanas": f"{duration_weeks} sem",
            "Estado": STATUS_LABELS[st.session_state.statuses[t["id"]]],
            "EstadoKey": st.session_state.statuses[t["id"]],
            "ColorFase": PHASES[t["phase"]]["color"],
            "Pilot": t["pilot"],
        })
    return pd.DataFrame(rows)


def metric_card(label: str, value: str, sub: str, color: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## Control de Assets")
st.sidebar.caption("ServiceNow Theme")
st.sidebar.markdown(
    f"""
    <div style='background:{SN_DARK_GREEN};padding:10px 12px;border-radius:12px;margin:8px 0 14px 0;color:white;font-weight:700;'>
    ⏱ Deadline: 12 Jun 2026
    </div>
    """,
    unsafe_allow_html=True,
)

view = st.sidebar.radio(
    "Vista",
    ["Overview", "Gantt", "Kanban", "Timeline"],
    index=0
)

st.sidebar.markdown("---")
progress_pct = get_stats()[4]
st.sidebar.write("**Avance**")
st.sidebar.progress(progress_pct / 100)
st.sidebar.caption(f"{progress_pct}% completado")

if st.sidebar.button("↺ Reiniciar estados", use_container_width=True):
    st.session_state.statuses = {t["id"]: "pending" for t in TASKS}
    st.rerun()

# =========================
# HEADER
# =========================
st.title(view)
st.markdown(
    f"<div class='small-note'>Inicio del proyecto: <b>{PROJECT_START.strftime('%d %b %Y')}</b> &nbsp;·&nbsp; Deadline: <b>{DEADLINE.strftime('%d %b %Y')}</b> &nbsp;·&nbsp; <b>{weeks_left()}</b> semanas restantes</div>",
    unsafe_allow_html=True,
)

st.write("")

# =========================
# METRICS
# =========================
done, prog, pend, total, pct = get_stats()
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Completadas", str(done), f"de {total} tareas", SN_DARK_GREEN)
with col2:
    metric_card("En progreso", str(prog), "tareas activas", SN_ORANGE)
with col3:
    metric_card("Pendientes", str(pend), "por iniciar", SN_BLUE)
with col4:
    metric_card("Semanas restantes", str(weeks_left()), f"hasta {DEADLINE.strftime('%d %b %Y')}", SN_RED)

st.write("")
df = build_task_df()

# =========================
# OVERVIEW
# =========================
if view == "Overview":
    left, right = st.columns([1, 1])

    with left:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Avance por fase</div>", unsafe_allow_html=True)

        phase_rows = []
        for phase_key, phase_meta in PHASES.items():
            phase_total = sum(1 for t in TASKS if t["phase"] == phase_key)
            phase_done = sum(
                1 for t in TASKS
                if t["phase"] == phase_key and st.session_state.statuses[t["id"]] == "done"
            )
            phase_pct = round((phase_done / phase_total) * 100) if phase_total else 0
            phase_rows.append({
                "Fase": phase_meta["label"],
                "Avance": phase_pct,
                "Completadas": phase_done,
                "Total": phase_total,
                "Color": phase_meta["color"],
            })

        phase_df = pd.DataFrame(phase_rows)
        fig_phase = go.Figure()
        for _, row in phase_df.iterrows():
            fig_phase.add_trace(
                go.Bar(
                    x=[row["Avance"]],
                    y=[row["Fase"]],
                    orientation="h",
                    marker=dict(color=row["Color"], line=dict(color="#FFFFFF", width=1)),
                    text=[f"{row['Completadas']}/{row['Total']}"],
                    textposition="outside" if row["Avance"] == 0 else "inside",
                    insidetextanchor="middle",
                    textfont=dict(color=SN_TEXT, size=12),
                    hovertemplate="%{y}: %{x}%<extra></extra>",
                )
            )

        fig_phase.update_layout(
            barmode="stack",
            height=320,
            paper_bgcolor=SN_CARD,
            plot_bgcolor=SN_CARD,
            font=dict(color=SN_TEXT),
            xaxis=dict(range=[0, 100], gridcolor="#E5E7EB", title="% avance", zeroline=False),
            yaxis=dict(title="", tickfont=dict(color=SN_TEXT)),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_phase, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Distribución de tareas</div>", unsafe_allow_html=True)

        donut_df = pd.DataFrame(
            {
                "Estado": ["Completadas", "En progreso", "Pendientes"],
                "Valor": [done, prog, pend],
            }
        )

        fig_donut = px.pie(
            donut_df,
            names="Estado",
            values="Valor",
            hole=0.62,
            color="Estado",
            color_discrete_map={
                "Completadas": SN_DARK_GREEN,
                "En progreso": SN_ORANGE,
                "Pendientes": SN_LIGHT_GRAY,
            },
        )
        fig_donut.update_traces(
            textinfo="label+value",
            textfont=dict(color=SN_TEXT, size=12),
            marker=dict(line=dict(color="#FFFFFF", width=2)),
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
        fig_donut.update_layout(
            height=320,
            paper_bgcolor=SN_CARD,
            plot_bgcolor=SN_CARD,
            font=dict(color=SN_TEXT),
            legend=dict(font=dict(color=SN_TEXT)),
            margin=dict(l=10, r=10, t=10, b=10),
            annotations=[
                dict(
                    text=f"{pct}%<br>avance",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=18, color=SN_TEXT),
                )
            ],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Línea de tiempo — resumen</div>", unsafe_allow_html=True)

    timeline_df = df.copy()
    fig_timeline = px.timeline(
        timeline_df,
        x_start="InicioFecha",
        x_end="FinFecha",
        y="Tarea",
        color="Fase",
        color_discrete_map={v["label"]: v["color"] for v in PHASES.values()},
        hover_data={
            "InicioTxt": True,
            "FinTxt": True,
            "InicioSemana": True,
            "FinSemana": True,
            "Estado": True,
            "InicioFecha": False,
            "FinFecha": False,
        },
    )
    fig_timeline.update_yaxes(autorange="reversed", tickfont=dict(color=SN_TEXT))
    fig_timeline.update_traces(
        marker=dict(line=dict(color="#FFFFFF", width=1.5)),
        opacity=0.95,
        text=timeline_df["RangoCorto"],
        textposition="inside",
    )
    fig_timeline.update_layout(
        height=560,
        paper_bgcolor=SN_CARD,
        plot_bgcolor=SN_PANEL_BG,
        font=dict(color=SN_TEXT),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Calendario",
        yaxis_title="",
        legend_title="Fase",
        legend=dict(font=dict(color=SN_TEXT)),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,
            tickfont=dict(color=SN_TEXT),
            tickformat="%d %b %Y",
            dtick=7 * 24 * 60 * 60 * 1000,
        ),
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    overview_table = df[["ID", "Tarea", "Fase", "InicioTxt", "FinTxt", "DuracionSemanas", "Estado"]].copy()
    overview_table.columns = ["#", "Tarea", "Fase", "Inicio", "Fin", "Duración", "Estado"]
    st.dataframe(overview_table, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# GANTT
# =========================
elif view == "Gantt":
    options = ["Todas"] + [meta["label"] for meta in PHASES.values()]
    selected_phase = st.selectbox("Filtrar por fase", options, index=0)

    if selected_phase == "Todas":
        gantt_df = df.copy()
    else:
        gantt_df = df[df["Fase"] == selected_phase].copy()

    fig_gantt = px.timeline(
        gantt_df,
        x_start="InicioFecha",
        x_end="FinFecha",
        y="Tarea",
        color="Fase",
        color_discrete_map={v["label"]: v["color"] for v in PHASES.values()},
        text="RangoCorto",
        hover_data={
            "InicioTxt": True,
            "FinTxt": True,
            "DuracionSemanas": True,
            "Estado": True,
            "InicioFecha": False,
            "FinFecha": False,
        },
    )
    fig_gantt.update_yaxes(autorange="reversed", tickfont=dict(color=SN_TEXT))
    fig_gantt.update_traces(
        textposition="inside",
        marker=dict(line=dict(color="#FFFFFF", width=1.5)),
        opacity=0.96,
    )
    fig_gantt.update_layout(
        height=680,
        paper_bgcolor=SN_CARD,
        plot_bgcolor=SN_PANEL_BG,
        font=dict(color=SN_TEXT),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Fechas",
        yaxis_title="",
        legend_title="Fase",
        xaxis=dict(
            showgrid=True,
            gridcolor="#E5E7EB",
            zeroline=False,
            tickfont=dict(color=SN_TEXT),
            tickformat="%d %b %Y",
            dtick=7 * 24 * 60 * 60 * 1000,
        ),
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.write("")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Actualizar estado de tareas</div>", unsafe_allow_html=True)

    edit_df = df[["ID", "Tarea", "Fase", "Estado", "InicioTxt", "FinTxt"]].copy()
    for _, row in edit_df.iterrows():
        cols = st.columns([0.08, 0.34, 0.16, 0.20, 0.22])
        cols[0].write(f"**{int(row['ID'])}**")
        cols[1].write(row["Tarea"])
        cols[2].write(row["Fase"])
        cols[3].write(f"{row['InicioTxt']} → {row['FinTxt']}")
        current_key = [k for k, v in STATUS_LABELS.items() if v == row["Estado"]][0]
        new_status = cols[4].selectbox(
            f"Estado {int(row['ID'])}",
            options=list(STATUS_LABELS.keys()),
            index=list(STATUS_LABELS.keys()).index(current_key),
            format_func=lambda x: f"{STATUS_EMOJI[x]} {STATUS_LABELS[x]}",
            key=f"status_{int(row['ID'])}",
        )
        st.session_state.statuses[int(row["ID"])] = new_status

    st.markdown("</div>", unsafe_allow_html=True)

    csv_df = df[["ID", "Tarea", "Fase", "InicioTxt", "FinTxt", "DuracionSemanas", "Estado"]].copy()
    csv_df.columns = ["ID", "Tarea", "Fase", "Inicio", "Fin", "Duracion", "Estado"]
    st.download_button(
        "↓ Exportar CSV",
        data=csv_df.to_csv(index=False).encode("utf-8"),
        file_name="control_assets_gantt.csv",
        mime="text/csv",
    )

# =========================
# KANBAN
# =========================
elif view == "Kanban":
    k1, k2, k3 = st.columns(3)
    status_order = ["pending", "inprogress", "done"]
    titles = {
        "pending": "⬜ Pendiente",
        "inprogress": "🔄 En progreso",
        "done": "✅ Completado",
    }
    columns_map = {"pending": k1, "inprogress": k2, "done": k3}

    for status_key in status_order:
        with columns_map[status_key]:
            tasks_filtered = [t for t in TASKS if st.session_state.statuses[t["id"]] == status_key]
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='section-title'>{titles[status_key]} ({len(tasks_filtered)})</div>",
                unsafe_allow_html=True,
            )
            if not tasks_filtered:
                st.caption("Sin tareas")
            else:
                for t in tasks_filtered:
                    phase = PHASES[t["phase"]]
                    start_date = week_start(t["start"])
                    end_date = week_end_from_index(t["end"])
                    date_text = f"{start_date.strftime('%d %b %Y')} → {end_date.strftime('%d %b %Y')}"
                    st.markdown(
                        f"""
                        <div style="background:#F8FAFC;border:1px solid #E5E7EB;border-left:4px solid {phase['color']};
                                    border-radius:12px;padding:12px 14px;margin-bottom:10px;">
                            <div style="font-weight:700;color:#1F2937;margin-bottom:6px;">{t['name']} {'<span style=\"font-size:10px;color:#F59E0B\">[PILOTO]</span>' if t['pilot'] else ''}</div>
                            <div style="font-size:12px;color:{phase['color']};font-weight:600;">{phase['label']}</div>
                            <div style="font-size:12px;color:#6B7280;margin-top:4px;">{date_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("</div>", unsafe_allow_html=True)

# =========================
# TIMELINE
# =========================
elif view == "Timeline":
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Timeline por fases</div>", unsafe_allow_html=True)

    for phase_key, phase_meta in PHASES.items():
        phase_tasks = [t for t in TASKS if t["phase"] == phase_key]
        if not phase_tasks:
            continue

        min_start = min(t["start"] for t in phase_tasks)
        max_end = max(t["end"] for t in phase_tasks)
        done_count = sum(1 for t in phase_tasks if st.session_state.statuses[t["id"]] == "done")
        total_count = len(phase_tasks)
        icon = "✓" if done_count == total_count else "●"

        tasks_html = "".join([
            (
                f"<div style='margin-bottom:8px;color:#1F2937;'>"
                f"{STATUS_EMOJI[st.session_state.statuses[t['id']]]} "
                f"<b>{t['name']}</b>{' <span style=\"font-size:10px;color:#F59E0B\">[PILOTO]</span>' if t['pilot'] else ''}"
                f"<div style='font-size:12px;color:#6B7280;margin-left:20px;'>"
                f"{week_start(t['start']).strftime('%d %b %Y')} → {week_end_from_index(t['end']).strftime('%d %b %Y')}"
                f"</div></div>"
            )
            for t in phase_tasks
        ])

        st.markdown(
            f"""
            <div style="display:flex;gap:14px;margin-bottom:18px;padding:14px;border:1px solid #D9E2EC;border-radius:14px;background:#FFFFFF;">
                <div style="width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;
                            border:2px solid {phase_meta['color']};color:{phase_meta['color']};font-weight:700;flex-shrink:0;">
                    {icon}
                </div>
                <div style="width:100%;">
                    <div style="font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{phase_meta['color']};margin-bottom:8px;">{phase_meta['label']}</div>
                    {tasks_html}
                    <div style="font-size:12px;color:#6B7280;margin-top:8px;">
                        Fase completa: {week_start(min_start).strftime('%d %b %Y')} → {week_end_from_index(max_end).strftime('%d %b %Y')}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    timeline_table = df[["ID", "Tarea", "Fase", "InicioTxt", "FinTxt", "DuracionSemanas", "Estado"]].copy()
    timeline_table.columns = ["#", "Tarea", "Fase", "Inicio", "Fin", "Duración", "Estado"]
    st.dataframe(timeline_table, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
