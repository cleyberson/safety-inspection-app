# app.py - Inspeção de SST com Dashboard Completo (Versão C)
from PIL import Image
import streamlit as st
from datetime import datetime
import pandas as pd
import os
import matplotlib.pyplot as plt
import io

# ================================
# CONFIG DA PÁGINA + ABAS
# ================================
st.set_page_config(
    page_title="Inspeção de SST - IHM",
    page_icon="🦺",
    layout="wide"
)

# Criar abas da aplicação
aba_form, aba_dash = st.tabs(["📝 Formulário", "📊 Dashboard"])

# ================================
# CSS
# ================================
st.markdown("""
<style>
body { background-color: #F5F7FA; }
.stButton>button {
    background-color: #004AAD;
    color: white;
    font-size: 18px;
    padding: 10px 25px;
    border-radius: 8px;
}
.stButton>button:hover { background-color: #003377; }
.card {
    padding: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}
.title { text-align: center; font-size: 28px; font-weight: bold; color: #004AAD; }
.sub { font-size: 20px; font-weight: 600; color: #004AAD; margin-bottom: 10px; }
.kpi { background: white; padding: 12px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
</style>
""", unsafe_allow_html=True)

# common paths (mantidos por segurança)
REG_FOLDER = "registros"
EXCEL_PATH = os.path.join(REG_FOLDER, "checklist_hse.xlsx")
CHECKLISTS_FOLDER = "checklists"

os.makedirs(REG_FOLDER, exist_ok=True)
os.makedirs(CHECKLISTS_FOLDER, exist_ok=True)
FOTOS_FOLDER = "fotos"
os.makedirs(FOTOS_FOLDER, exist_ok=True)

# ================================
# LISTA DE ÁREAS
# ================================
AREAS = [
    "Caldeiraria",
    "Montagem Elétrica – Painéis",
    "Montagem Mecânica",
    "Testes Elétricos",
    "Corte e Dobra",
    "Pintura",
    "Almoxarifado"
]

# ================================
# LISTA DE EPIs
# ================================
EPIS = [
    "Capacete de Segurança",
    "Óculos de Proteção",
    "Protetor Auricular",
    "Luvas de Segurança",
    "Botina de Segurança",
    "Avental",
    "Respirador",
    "Máscara de Solda",
    "Protetor Facial",
    "Cinto de Segurança (Trabalho em Altura)"
]

# ================================
# ============== FORMULÁRIO ======
# ================================
with aba_form:

    st.markdown("<div class='title'>Inspeção de SST - IHM</div>", unsafe_allow_html=True)

    # 1️⃣ Dados da Avaliação
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>1️⃣ Dados da Avaliação</div>", unsafe_allow_html=True)

        area = st.selectbox("Área", AREAS)
        responsavel = st.text_input("Responsável")

        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", datetime.now().date())
        with col2:
            hora = st.time_input("Hora", datetime.now().time().replace(microsecond=0))

        st.markdown("</div>", unsafe_allow_html=True)

    # 2️⃣ Condições
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>2️⃣ Condições de Segurança</div>", unsafe_allow_html=True)
        condicoes = st.text_area("Descreva as condições observadas")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 📸 Registro Fotográfico (opcional)
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>📸 Registro Fotográfico (opcional)</div>", unsafe_allow_html=True)
        foto = st.file_uploader(
        "Envie uma imagem do local ou condição observada",
        type=["jpg", "jpeg", "png"]
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 3️⃣ Class de Risco
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>⚠️ Class de Risco e Ação</div>", unsafe_allow_html=True)

        risco = st.selectbox("Class do Risco", ["Baixo", "Médio", "Alto"])
        acao_necessaria = st.selectbox("Necessita ação corretiva?", ["Não", "Sim"])

        descricao_acao = ""
        if acao_necessaria == "Sim":
            descricao_acao = st.text_area("Descreva a ação corretiva")

        col_a, col_b = st.columns(2)
        with col_a:
            resp_acao = st.text_input("Responsável pela ação")
        with col_b:
            prazo_acao = st.date_input("Prazo para conclusão")

        st.markdown("</div>", unsafe_allow_html=True)

    # 4️⃣ Ausência de EPI
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>4️⃣ Ausência de EPI Obrigatório</div>", unsafe_allow_html=True)
        epi = st.multiselect("Selecione o EPI", EPIS)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5️⃣ Observações
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='sub'>5️⃣ Observações</div>", unsafe_allow_html=True)
        observacoes = st.text_area("Observações gerais")
        st.markdown("</div>", unsafe_allow_html=True)

    # 💾 SALVAR
if st.button("💾 Salvar no Excel"):

    if acao_necessaria == "Sim" and not descricao_acao.strip():
        st.error("⚠️ Descreva a ação corretiva antes de salvar.")

    else:

        nome_foto = ""

        if foto is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extensao = foto.name.split(".")[-1]
            nome_foto = f"{timestamp}.{extensao}"

            caminho_foto = os.path.join(FOTOS_FOLDER, nome_foto)

            with open(caminho_foto, "wb") as f:
                f.write(foto.getbuffer())

        dados = {
            "Área": area,
            "Responsável": responsavel,
            "Data": data,
            "Hora": hora.strftime("%H:%M"),
            "Condições": condicoes,
            "Risco": risco,
            "Ação Necessária": acao_necessaria,
            "Descrição da Ação": descricao_acao,
            "Responsável Ação": resp_acao,
            "Prazo Ação": prazo_acao,
            "Ausência de EPI": ", ".join(epi),
            "Observações": observacoes,
            "Foto": nome_foto
        }

        df_new = pd.DataFrame([dados])

        if os.path.exists(EXCEL_PATH):
            df_old = pd.read_excel(EXCEL_PATH)
            df_new = pd.concat([df_old, df_new], ignore_index=True)

        df_new.to_excel(EXCEL_PATH, index=False)

        st.success("✅ Registro salvo com sucesso!")

# ================================
# ============== DASHBOARD =======
# ================================
with aba_dash:

    st.markdown("## 📊 Painel de Controle – Inspeções de SST")
    st.write("Acompanhamento gerencial das inspeções realizadas.")

    if not os.path.exists(EXCEL_PATH):
        st.warning("Nenhum registro encontrado.")
        st.stop()

    df = pd.read_excel(EXCEL_PATH)

    # ================================
    # TRATAMENTO DE DADOS
    # ================================
    df = df.fillna("Não informado")

    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"])

    df_filtrado = df
    # Limpeza e padronização de dados
    df_filtrado["Risco"] = df_filtrado["Risco"].astype(str).str.strip()
    df_filtrado["Ação Necessária"] = df_filtrado["Ação Necessária"].astype(str).str.strip()

    # ================================
    # KPIs
    # ================================
    st.markdown("### 📌 Indicadores-Chave")

    total_inspecoes = df_filtrado.shape[0]
    risco_alto = df_filtrado[df_filtrado["Risco"].str.lower() == "alto"].shape[0]
    acoes_corretivas = df_filtrado[df_filtrado["Ação Necessária"].str.lower() == "sim"].shape[0]
    sem_acao = df_filtrado[df_filtrado["Ação Necessária"].str.lower() == "não"].shape[0]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total de Inspeções", total_inspecoes)
    c2.metric("Risco Alto", risco_alto)
    c3.metric("Ações Corretivas", acoes_corretivas)
    c4.metric("Sem Ação Necessária", sem_acao)

    # ================================
    # GRÁFICOS
    # ================================
    st.markdown("### 📈 Análises Gráficas")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Inspeções por Área")

        area_count = df_filtrado["Área"].value_counts()

        fig1, ax1 = plt.subplots()
        ax1.bar(area_count.index, area_count.values)

        ax1.set_xlabel("Área")
        ax1.set_ylabel("Quantidade")

        plt.xticks(rotation=45)

        st.pyplot(fig1)
        plt.close(fig1)

    with col2:
        st.subheader("Classificação de Risco")

        risco_count = df_filtrado["Risco"].value_counts()

        fig2, ax2 = plt.subplots()

        ax2.pie(
            risco_count.values,
            labels=risco_count.index,
            autopct="%1.0f%%",
            startangle=90
        )

        ax2.axis("equal")

        st.pyplot(fig2)
        plt.close(fig2)

    # ================================
    # TABELA
    # ================================
    st.markdown("### 📋 Registros Detalhados")

    st.dataframe(df_filtrado, use_container_width=True)

# ================================
# EXPORTAÇÃO
# ================================
st.markdown("### ⬇️ Exportação de Dados")

buffer = io.BytesIO()

with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name="Inspeções_SST")

st.download_button(
    label="📥 Exportar dados do painel (Excel)",
    data=buffer.getvalue(),
    file_name="dashboard_inspecoes_sst.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)