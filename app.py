import streamlit as st
import pandas as pd
import plotly.express as px
import io

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# =========================================
# IMPORTS INTERNOS
# =========================================

from utils.styles import CUSTOM_CSS

from utils.constants import (
    AREAS,
    EPIS
)

from utils.validators import (
    validar_formulario
)

from database.database import (
    create_table
)

from services.inspection_service import (
    salvar_inspecao,
    listar_inspecoes,
    concluir_acao
)

from services.metrics_service import (
    calcular_kpis,
    calcular_sla
)

# =========================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================

st.set_page_config(
    page_title="Checklist HSE",
    page_icon="🦺",
    layout="wide"
)

# =========================================
# CSS
# =========================================

st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True
)

# =========================================
# CRIAR BANCO/TABELA
# =========================================

create_table()

# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.markdown("## 🦺 HSE Analytics")

    st.markdown("---")

    st.markdown(
        """
        ### 📌 Sistema

        Plataforma corporativa de:
        - Inspeções SST
        - Gestão de riscos
        - Ações corretivas
        - SLA operacional
        - Analytics HSE
        """
    )

    st.markdown("---")

    st.info(
        "Sistema corporativo de inspeções."
    )

    st.markdown("---")

    st.caption(
        "Versão Enterprise 2026"
    )

# =========================================
# TÍTULO
# =========================================

st.markdown(
    """
    <div class='title'>
        🦺 Plataforma Inteligente de Inspeções HSE
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================
# FORMULÁRIO
# =========================================

with st.form("form_inspecao"):

    st.markdown("## 📋 Nova Inspeção")

    area = st.selectbox(
        "Área",
        AREAS
    )

    responsavel = st.text_input(
        "Responsável"
    )

    col1, col2 = st.columns(2)

    with col1:

        data = st.date_input(
            "Data",
            datetime.now().date()
        )

    with col2:

        hora = st.time_input(
            "Hora",
            datetime.now().time().replace(
                microsecond=0
            )
        )

    condicoes = st.text_area(
        "Condições observadas"
    )

    risco = st.selectbox(
        "Classificação de Risco",
        ["Baixo", "Médio", "Alto"]
    )

    acao_necessaria = st.selectbox(
        "Necessita ação corretiva?",
        ["Não", "Sim"]
    )

    descricao_acao = ""
    resp_acao = ""

    if acao_necessaria == "Sim":

        descricao_acao = st.text_area(
            "Descrição da ação corretiva"
        )

        resp_acao = st.text_input(
            "Responsável pela ação"
        )

    prazo_acao = st.date_input(
        "Prazo da ação"
    )

    epis = st.multiselect(
        "EPIs ausentes",
        EPIS
    )

    observacoes = st.text_area(
        "Observações"
    )

    salvar = st.form_submit_button(
        "💾 Salvar Inspeção"
    )

# =========================================
# SALVAR
# =========================================

if salvar:

    erros = validar_formulario(
        responsavel,
        condicoes,
        acao_necessaria,
        descricao_acao,
        resp_acao
    )

    if erros:

        for erro in erros:

            st.error(erro)

    else:

        dados = {

            "area": area,
            "responsavel": responsavel,
            "data": data,
            "hora": hora.strftime("%H:%M"),
            "condicoes": condicoes,
            "risco": risco,
            "acao_necessaria": acao_necessaria,
            "descricao_acao": descricao_acao,
            "resp_acao": resp_acao,
            "prazo_acao": prazo_acao,
            "epis": ", ".join(epis),
            "observacoes": observacoes,
            "foto": ""

        }

        salvar_inspecao(dados)

        st.success(
            "✅ Inspeção salva com sucesso!"
        )

# =========================================
# DASHBOARD
# =========================================

st.markdown("---")

st.markdown(
    "## 📊 Dashboard Executivo HSE"
)

# =========================================
# DADOS
# =========================================

dados = listar_inspecoes()

# =========================================
# COLUNAS
# =========================================

colunas = [

    "id",
    "area",
    "responsavel",
    "data_inspecao",
    "hora_inspecao",
    "condicoes",
    "risco",
    "acao_necessaria",
    "descricao_acao",
    "responsavel_acao",
    "prazo_acao",
    "epis_ausentes",
    "observacoes",
    "foto",
    "status",
    "data_conclusao",
    "created_at"
]

# =========================================
# DATAFRAME
# =========================================

df = pd.DataFrame(
    dados,
    columns=colunas
)

# =========================================
# SEM DADOS
# =========================================

if df.empty:

    st.warning(
        "Nenhuma inspeção encontrada."
    )

else:

    # =====================================
    # TRATAMENTO
    # =====================================

    df["data_inspecao"] = pd.to_datetime(
        df["data_inspecao"]
    )

    df["prazo_acao"] = pd.to_datetime(
        df["prazo_acao"],
        errors="coerce"
    )

    df["data_conclusao"] = pd.to_datetime(
        df["data_conclusao"],
        errors="coerce"
    )

    hoje = pd.Timestamp.now()

    df["aging_dias"] = (
        hoje - df["data_inspecao"]
    ).dt.days

    df["acao_vencida"] = (
        (df["prazo_acao"] < hoje)
        &
        (df["status"] != "Concluído")
    )

    df["tempo_resolucao"] = (
        df["data_conclusao"]
        - df["data_inspecao"]
    ).dt.days

    # =====================================
    # FILTROS
    # =====================================

    st.markdown(
        "## 🎯 Filtros Executivos"
    )

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:

        filtro_area = st.multiselect(

            "Área",

            options=df["area"].unique(),

            default=df["area"].unique()

        )

    with col_f2:

        filtro_risco = st.multiselect(

            "Risco",

            options=df["risco"].unique(),

            default=df["risco"].unique()

        )

    with col_f3:

        filtro_status = st.multiselect(

            "Status",

            options=df["status"].unique(),

            default=df["status"].unique()

        )

    with col_f4:

        data_min = df["data_inspecao"].min()

        data_max = df["data_inspecao"].max()

        periodo = st.date_input(

            "Período",

            value=(data_min, data_max)

        )

    data_inicio = pd.to_datetime(
        periodo[0]
    )

    data_fim = pd.to_datetime(
        periodo[1]
    )

    # =====================================
    # FILTRAGEM
    # =====================================

    df = df[

        (df["area"].isin(filtro_area)) &

        (df["risco"].isin(filtro_risco)) &

        (df["status"].isin(filtro_status)) &

        (df["data_inspecao"] >= data_inicio) &

        (df["data_inspecao"] <= data_fim)

    ]

    # =====================================
    # KPIS
    # =====================================

    kpis = calcular_kpis(df)

    total_inspecoes = kpis["total_inspecoes"]

    riscos_altos = kpis["riscos_altos"]

    acoes_corretivas = kpis["acoes_corretivas"]

    acoes_concluidas = kpis["acoes_concluidas"]

    acoes_vencidas = kpis["acoes_vencidas"]

    taxa_risco_alto = kpis["taxa_risco_alto"]

    sla_operacional = calcular_sla(df)

    df_concluidas = df[
        df["status"] == "Concluído"
    ]

    tempo_medio_resolucao = 0

    if not df_concluidas.empty:

        tempo_medio_resolucao = round(

            df_concluidas["tempo_resolucao"]
            .mean(),

            1

        )

    backlog_pendente = len(

        df[df["status"] != "Concluído"]

    )

    # =====================================
    # KPI CARDS
    # =====================================

    c1, c2, c3, c4 = st.columns(4)

    c5, c6, c7, c8 = st.columns(4)

    c1.metric(
        "Total Inspeções",
        total_inspecoes
    )

    c2.metric(
        "Riscos Altos",
        riscos_altos
    )

    c3.metric(
        "Ações Corretivas",
        acoes_corretivas
    )

    c4.metric(
        "% Risco Alto",
        f"{taxa_risco_alto}%"
    )

    c5.metric(
        "Ações Vencidas",
        acoes_vencidas
    )

    c6.metric(
        "Concluídas",
        acoes_concluidas
    )

    c7.metric(
        "📌 Backlog",
        backlog_pendente
    )

    c8.metric(
        "SLA %",
        f"{sla_operacional}%"
    )

    st.markdown("---")

    # =====================================
    # ALERTAS
    # =====================================

    if acoes_vencidas > 0:

        st.error(
            f"🚨 Existem {acoes_vencidas} ações vencidas."
        )

    if riscos_altos > 5:

        st.warning(
            "⚠️ Volume elevado de riscos altos."
        )

    if sla_operacional < 70:

        st.warning(
            "📉 SLA operacional abaixo do esperado."
        )

    if backlog_pendente > 10:

        st.error(
            "📌 Backlog operacional elevado."
        )

    # =====================================
    # GRÁFICO ÁREAS
    # =====================================

    st.markdown(
        "### 📍 Inspeções por Área"
    )

    area_count = (

        df["area"]
        .value_counts()
        .reset_index()

    )

    area_count.columns = [
        "Área",
        "Quantidade"
    ]

    fig_area = px.bar(

        area_count,

        x="Área",

        y="Quantidade",

        text_auto=True

    )

    st.plotly_chart(
        fig_area,
        width="stretch"
    )

    # =====================================
    # GRÁFICO RISCO
    # =====================================

    st.markdown(
        "### ⚠️ Distribuição de Risco"
    )

    risco_count = (

        df["risco"]
        .value_counts()
        .reset_index()

    )

    risco_count.columns = [
        "Risco",
        "Quantidade"
    ]

    fig_risco = px.pie(

        risco_count,

        names="Risco",

        values="Quantidade"

    )

    st.plotly_chart(
        fig_risco,
        width="stretch"
    )

    # =====================================
    # RANKING
    # =====================================

    st.markdown(
        "### 🚨 Ranking de Áreas Críticas"
    )

    ranking = (

        df[df["risco"] == "Alto"]

        ["area"]

        .value_counts()

        .reset_index()

    )

    ranking.columns = [
        "Área",
        "Ocorrências"
    ]

    fig_rank = px.bar(

        ranking,

        x="Área",

        y="Ocorrências",

        text_auto=True

    )

    st.plotly_chart(
        fig_rank,
        width="stretch"
    )

    # =====================================
    # TENDÊNCIA
    # =====================================

    st.markdown(
        "### 📈 Tendência de Inspeções"
    )

    tendencia = (

        df.groupby(
            df["data_inspecao"].dt.date
        )

        .size()

        .reset_index(name="Quantidade")

    )

    fig_tendencia = px.line(

        tendencia,

        x="data_inspecao",

        y="Quantidade",

        markers=True

    )

    st.plotly_chart(
        fig_tendencia,
        width="stretch"
    )

    # =====================================
    # HEATMAP
    # =====================================

    st.markdown(
        "### 🔥 Heatmap de Riscos"
    )

    heatmap_data = (

        df.groupby(
            ["area", "risco"]
        )

        .size()

        .reset_index(name="quantidade")

    )

    if not heatmap_data.empty:

        fig_heatmap = px.density_heatmap(

            heatmap_data,

            x="risco",

            y="area",

            z="quantidade",

            text_auto=True

        )

        st.plotly_chart(
            fig_heatmap,
            width="stretch"
        )

    else:

        st.info(
            "Sem dados para gerar heatmap."
        )

    # =====================================
    # SLA POR ÁREA
    # =====================================

    st.markdown(
        "### ⏱️ SLA Médio por Área"
    )

    sla_area = (

        df_concluidas
        .groupby("area")["tempo_resolucao"]
        .mean()
        .reset_index()

    )

    if not sla_area.empty:

        sla_area["tempo_resolucao"] = (
            sla_area["tempo_resolucao"]
            .round(1)
        )

        fig_sla = px.bar(

            sla_area,

            x="area",

            y="tempo_resolucao",

            text_auto=True

        )

        st.plotly_chart(
            fig_sla,
            width="stretch"
        )

    else:

        st.info(
            "Sem ações concluídas."
        )

    # =====================================
    # AÇÕES VENCIDAS
    # =====================================

    st.markdown(
        "### 🚨 Ações Vencidas"
    )

    df_vencidas = df[
        df["acao_vencida"] == True
    ]

    st.dataframe(

        df_vencidas[[

            "area",
            "responsavel",
            "risco",
            "prazo_acao",
            "aging_dias",
            "status"

        ]],

        width="stretch"
    )

    # =====================================
    # CONCLUIR AÇÃO
    # =====================================

    st.markdown(
        "### ✅ Concluir Ação"
    )

    acoes_pendentes = df[
        df["status"] != "Concluído"
    ]

    if not acoes_pendentes.empty:

        opcoes = {

            f"{row['area']} | {row['responsavel']}":

            row["id"]

            for _, row in acoes_pendentes.iterrows()
        }

        acao_select = st.selectbox(

            "Selecione a ação",

            options=list(opcoes.keys())

        )

        if st.button(
            "Concluir Ação"
        ):

            concluir_acao(
                opcoes[acao_select]
            )

            st.success(
                "Ação concluída com sucesso!"
            )

            st.rerun()

    # =====================================
    # TABELA
    # =====================================

    st.markdown(
        "### 📋 Registros"
    )

    st.dataframe(
        df,
        width="stretch"
    )

    # =====================================
    # EXPORTAÇÃO EXCEL
    # =====================================

    st.markdown(
        "### 📥 Exportação de Dados"
    )

    buffer = io.BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Dashboard_HSE"
        )

    st.download_button(

        label="📊 Exportar Dashboard Excel",

        data=buffer.getvalue(),

        file_name="dashboard_hse.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =====================================
    # EXPORTAÇÃO PDF
    # =====================================

    st.markdown(
        "### 📄 Relatório Executivo PDF"
    )

    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    conteudo = []

    conteudo.append(

        Paragraph(
            "Relatório Executivo HSE",
            styles["Title"]
        )

    )

    conteudo.append(
        Spacer(1, 20)
    )

    conteudo.append(

        Paragraph(

            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",

            styles["Normal"]

        )

    )

    conteudo.append(
        Spacer(1, 20)
    )

    conteudo.append(

        Paragraph(

            f"""
            <b>Total Inspeções:</b> {total_inspecoes}<br/>
            <b>Riscos Altos:</b> {riscos_altos}<br/>
            <b>Ações Corretivas:</b> {acoes_corretivas}<br/>
            <b>Ações Vencidas:</b> {acoes_vencidas}<br/>
            <b>SLA Operacional:</b> {sla_operacional}%<br/>
            """,

            styles["BodyText"]

        )

    )

    conteudo.append(
        Spacer(1, 20)
    )

    conteudo.append(

        Paragraph(

            """
            Este relatório apresenta os indicadores
            executivos das inspeções HSE.
            """,

            styles["BodyText"]

        )

    )

    doc.build(conteudo)

    st.download_button(

        label="📄 Exportar Relatório PDF",

        data=pdf_buffer.getvalue(),

        file_name="relatorio_hse.pdf",

        mime="application/pdf"
    )
