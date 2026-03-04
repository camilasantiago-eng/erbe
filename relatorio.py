import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(page_title="Report Mensal Erbe - Jurídico", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

LOGO_WIDTH = 500

logo = Image.open("logo.png")

col_logo, col_titulo = st.columns([2,5])

with col_logo:
    st.image(logo, width=LOGO_WIDTH)

with col_titulo:
    st.markdown("""
    <div style='display:flex; align-items:center; height:100%;'>
        <h1 style='margin:0'>Report Mensal Erbe - Jurídico</h1>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================================
# FILTRO DE PERÍODO
# ==========================================================

col1,col2,col3 = st.columns([2,2,1])

with col1:
    data_inicio = st.date_input("Data início", value=datetime.date(2024,1,1))

with col2:
    data_fim = st.date_input("Data fim", value=datetime.date.today())

with col3:
    st.write("")
    st.write("")
    filtrar = st.button("Filtrar",use_container_width=True)

# ==========================================================
# CARREGAR BASES
# ==========================================================

entradas = pd.read_csv("Base_Entradas.csv")
settled = pd.read_csv("Base_Settled.csv")
relatorio = pd.read_csv("relatorio_tratado.csv")

# converter datas
entradas["Data Cálculo"] = pd.to_datetime(entradas["Data Cálculo"])
settled["Data Cálculo"] = pd.to_datetime(settled["Data Cálculo"])

# ==========================================================
# REMOVER DUPLICADOS
# ==========================================================

entradas = entradas.sort_values("Data Cálculo").drop_duplicates("Pasta",keep="last")
settled = settled.sort_values("Data Cálculo").drop_duplicates("Pasta",keep="last")
relatorio = relatorio.drop_duplicates("Pasta")

# ==========================================================
# FILTRO DE DATA
# ==========================================================

entradas_filtrado = entradas[
(entradas["Data Cálculo"]>=pd.to_datetime(data_inicio)) &
(entradas["Data Cálculo"]<=pd.to_datetime(data_fim))
]

settled_filtrado = settled[
(settled["Data Cálculo"]>=pd.to_datetime(data_inicio)) &
(settled["Data Cálculo"]<=pd.to_datetime(data_fim))
]

# ==========================================================
# MÉTRICAS
# ==========================================================

MES_ANTERIOR = "*****"  # preencher manualmente

entradas_total = entradas_filtrado["Pasta"].count()

baixa_prov = settled_filtrado[
settled_filtrado["Status"]=="BAIXA PROVISORIA"
]["Pasta"].count()

encerrados = settled_filtrado[
settled_filtrado["Status"]=="ENCERRADOS"
]["Pasta"].count()

mes_atual = relatorio["Pasta"].nunique()

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Mês Anterior",MES_ANTERIOR)
col2.metric("Entradas",entradas_total)
col3.metric("Baixa Provisória",baixa_prov)
col4.metric("Encerrados",encerrados)
col5.metric("Mês Atual",mes_atual)

st.divider()

# ==========================================================
# GRÁFICO ENTRADAS POR TIPO
# ==========================================================

col_g1,col_g2 = st.columns(2)

with col_g1:

    st.subheader("Entradas do mês")

    graf_entradas = entradas_filtrado.groupby("Macro Assunto")["Pasta"].count().reset_index()

    fig1 = px.bar(
        graf_entradas,
        x="Macro Assunto",
        y="Pasta",
        text="Pasta"
    )

    fig1.update_layout(showlegend=False)

    st.plotly_chart(fig1,use_container_width=True)

# ==========================================================
# GRÁFICO SAÍDAS
# ==========================================================

with col_g2:

    st.subheader("Saídas e Baixas")

    saidas = settled_filtrado.groupby(["Status","Macro Encerramento"])["Pasta"].count().reset_index()

    fig2 = px.bar(
        saidas,
        x="Status",
        y="Pasta",
        color="Macro Encerramento",
        barmode="stack"
    )

    st.plotly_chart(fig2,use_container_width=True)

st.divider()

# ==========================================================
# GRÁFICO ENTRADAS X SAÍDAS
# ==========================================================

st.subheader("Entradas x Saídas")

entradas_filtrado["Mes"] = entradas_filtrado["Data Cálculo"].dt.month
settled_filtrado["Mes"] = settled_filtrado["Data Cálculo"].dt.month

entradas_mes = entradas_filtrado.groupby("Mes")["Pasta"].count()
saidas_mes = settled_filtrado.groupby("Mes")["Pasta"].count()

meses = range(1,13)

entradas_lista = [entradas_mes.get(m,0) for m in meses]
saidas_lista = [saidas_mes.get(m,0) for m in meses]

fig3 = go.Figure()

fig3.add_trace(go.Scatter(
x=list(meses),
y=entradas_lista,
mode="lines+markers",
name="Entradas"
))

fig3.add_trace(go.Scatter(
x=list(meses),
y=saidas_lista,
mode="lines+markers",
name="Saídas"
))

fig3.update_layout(
xaxis_title="Mês",
yaxis_title="Quantidade"
)

st.plotly_chart(fig3,use_container_width=True)

st.divider()

# ==========================================================
# TABELA FINAL EXECUTIVA
# ==========================================================

st.subheader("Baixa provisória e encerrados")

dados = []

for status in ["Won","Settled","Lost"]:

    df = settled_filtrado[
    settled_filtrado["Macro Encerramento"]==status
    ]

    qtd = df["Pasta"].count()

    bp = df["Valor Pedido Objeto Corrigido"].sum()

    fcx = df["Valor integral do Acordo/Condenação"].sum()

    saving = 0
    if bp != 0:
        saving = (bp-fcx)/bp

    dados.append({
        "Status":status,
        "Quantidade de processos":qtd,
        "BP Atualizado":bp,
        "Fcx Real":fcx,
        "Saving":saving
    })

df_tabela = pd.DataFrame(dados)

bp_total = df_tabela["BP Atualizado"].sum()
fcx_total = df_tabela["Fcx Real"].sum()

total = {
"Status":"Total",
"Quantidade de processos":df_tabela["Quantidade de processos"].sum(),
"BP Atualizado":bp_total,
"Fcx Real":fcx_total,
"Saving":(bp_total-fcx_total)/bp_total if bp_total !=0 else 0
}

df_tabela = pd.concat([df_tabela,pd.DataFrame([total])])

def format_moeda(valor):
    return f"R$ {valor/1000000:.2f}M"

def format_percent(v):
    return f"{v*100:.1f}%"

df_tabela["BP Atualizado"] = df_tabela["BP Atualizado"].apply(format_moeda)
df_tabela["Fcx Real"] = df_tabela["Fcx Real"].apply(format_moeda)
df_tabela["Saving"] = df_tabela["Saving"].apply(format_percent)

st.dataframe(df_tabela,use_container_width=True)
