import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, time, timedelta

# Configuração da Página
st.set_page_config(page_title="Dashboard de Tarefas", layout="wide")
st.title("Dashboard de Tarefas")

# Configurações / Constantes
API_URL = "http://localhost:8000"  # Ajuste conforme necessário
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
WORK_START = time(8, 0)  # 08:00
WORK_END = time(17, 0)   # 17:00

# --- Camada de Serviço (Consumo da API) ---
@st.cache_data(ttl=300) # Cache por 5 minutos para não sobrecarregar a API
def fetch_data(start_date, end_date):
    """
    Busca tanto as tarefas quanto os gaps para compor a visão completa.
    """
    s_date_str = start_date.strftime(DATE_FORMAT)
    e_date_str = end_date.strftime(DATE_FORMAT)
    
    try:
        # 1. Buscar os GAPS (Seu endpoint calculado)
        resp_gaps = requests.get(
            f"{API_URL}/gaps",
            params={"start_date": s_date_str, "end_date": e_date_str})
        resp_gaps.raise_for_status()
        gaps_data = resp_gaps.json()
        
        # 2. Buscar as TASKS
        resp_tasks = requests.get(
            f"{API_URL}/tasks/by_start_date",
            params={"start_date": s_date_str, "end_date": e_date_str}
        )
        resp_tasks.raise_for_status()
        tasks_data = resp_tasks.json()
        
        return gaps_data, tasks_data
    except requests.exceptions.ConnectionError:
        st.error(f"Não foi possível conectar na API")
        return [], []
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return [], []
    
def process_timeline_dataframe(gaps, tasks):
    """
    Noramliza os dados de Gaps e Tasks em um único DataFrame para o Plotly
    """
    timeline_rows = []

    # Processar Tarefas (Verde/Azul)
    for t in tasks:
        timeline_rows.append({
            "Start": t["start_date"],
            "Finish": t["end_date"],
            "Resource": "Atividade", # Eixo Y (Agrupamento)
            "Type": "Trabalho",      # Para colorir
            "Description": f"{t['task_code']} - {t['task_name']} ({t['hours_worked']}h)",
            "Duration": t.get("hours_worked", 0)
        })

    # Processar Gaps (Vermelho/Alerta)
    for g in gaps:
        timeline_rows.append({
            "Start": g["start_date"],
            "Finish": g["end_date"],
            "Resource": "Atividade",
            "Type": "GAP (Ociosidade)",
            "Description": f"Gap: {g['duration_hours']}h úteis",
            "Duration": g["duration_hours"]
        })
    
    return pd.DataFrame(timeline_rows)

# --- UI - Interface do Usuário ---

st.title("📊 Análise de Eficiência e Gaps")
st.markdown("Visão unificada de **Trabalho Realizado** vs **Tempo Ocioso (Gaps)** considerando horário comercial e feriados.")

# 1. Filtros na Sidebar
with st.sidebar:
    st.header("Filtros")
    # Padrão: últimos 7 dias
    default_start = datetime.now().date() - timedelta(days=7)
    default_end = datetime.now().date()

    date_range = st.date_input(
        "Selecione o Período",
        value=(default_start, default_end)
    )

    if len(date_range) != 2:
        st.warning("Selecione data de início e fim.")
        st.stop()

    start_date, end_date = date_range

    # Convertendo para datetime completo para enviar a API
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)

    if st.button("Atualizar Dados"):
        st.cache_data.clear()

# 2. Busca e Processamento
gaps_data, tasks_data = fetch_data(start_dt, end_dt)

if not gaps_data and not tasks_data:
    st.info("Nenhum dado encontrado para o período")
else:
    df = process_timeline_dataframe(gaps_data, tasks_data)

    # 3. KPIs (Indicadores)
    col1, col2, col3 = st.columns(3)

    total_gaps_hours = sum(g['duration_hours'] for g in gaps_data)
    total_tasks_hours = sum(t.get('hours_worked', 0) for t in tasks_data)
    efficiency = 0
    if (total_tasks_hours + total_gaps_hours) > 0:
        efficiency = (total_tasks_hours / (total_tasks_hours + total_gaps_hours)) * 100
    
    col1.metric("⚠️ Horas Ociosas (Gaps)", f"{total_gaps_hours:.2f} h")
    col2.metric("⏱️ Horas Trabalhadas", f"{total_tasks_hours:.2f} h")
    col3.metric("✅ Eficiência", f"{efficiency:.2f} %")

    # 4. Visualização Gráfica (Gantt Chart)
    st.subheader("Timeline de Execução")

    if not df.empty:
        # Mapa de Cores Personalizado
        color_map = {
            "Trabalho": "rgb(0, 123, 255)",  # Azul
            "GAP (Ociosidade)": "rgb(220, 53, 69)"  # Vermelho
        }

        fig = px.timeline(
            df,
            x_start="Start",
            x_end="Finish",
            y="Resource",
            color="Type",
            text="Description",
            color_discrete_map=color_map,
            title="Linha do Tempo de Tarefas e Gaps",
            hover_data=["Description", "Duration"],
            height=300
        )

        # Ajustes finos do layout do Plotly
        fig.update_yaxes(autorange="reversed", title="")  # Inverter o eixo Y
        fig.update_layout(
            xaxis_title="Linha do Tempo",
            legend_title="Tipo de Atividade",
            bargap=0.2
        )

        st.plotly_chart(fig, use_container_width=True)

        # 5. Detalhamento em Tabela (Tabs)
        tab1, tab2 = st.tabs(["🔴 Detalhes dos Gaps", "🟢 Detalhes das Tarefas"])

        with tab1:
            if gaps_data:
                df_gaps = pd.DataFrame(gaps_data)
                # Formatar colunas para ficar bonito
                df_gaps['start_date'] = pd.to_datetime(df_gaps['start_date']).dt.strftime('%d/%m/%Y %H:%M')
                df_gaps['end_date'] = pd.to_datetime(df_gaps['end_date']).dt.strftime('%d/%m/%Y %H:%M')
                st.dataframe(
                    df_gaps[['start_date', 'end_date', 'duration_hours', 'message']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("Sem gaps detectados neste período! 🚀")

        with tab2:
            if tasks_data:
                df_tasks = pd.DataFrame(tasks_data)
                st.dataframe(
                    df_tasks[['task_code', 'task_name', 'sprint', 'hours_worked', 'status']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma tarefa registrada.")