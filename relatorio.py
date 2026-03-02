import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import datetime

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(page_title="Report Mensal Erbe - Jurídico", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER COM LOGO (HORIZONTAL LONGA)
# =====================================================

LOGO_WIDTH = 500  # ajuste aqui se quiser maior ou menor

logo = Image.open("logo.png")

col_logo, col_titulo = st.columns([4,5])

with col_logo:
    st.image(logo, width=LOGO_WIDTH)

with col_titulo:
    st.markdown(
        """
        <div style='display:flex; align-items:center; height:100%;'>
            <h1 style='font-weight:600; margin:0;'>
                Report Mensal Erbe - Jurídico
            </h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# =====================================================
# FILTRO VISUAL
# =====================================================

col1, col2, col3 = st.columns([2,2,1])

with col1:
    st.date_input("Data Início", value=datetime.date(2024, 4, 1))

with col2:
    st.date_input("Data Fim", value=datetime.date(2024, 4, 30))

with col3:
    st.write("")
    st.write("")
    st.button("Filtrar", use_container_width=True)

st.divider()

# =====================================================
# MÉTRICAS MOCKADAS
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Mês Anterior", "8.450")
col2.metric("Entradas", "1.200")
col3.metric("Baixa Provisória", "950")
col4.metric("Encerrados", "600")
col5.metric("Mês Atual", "8.100")

st.divider()

# =====================================================
# GRÁFICOS SUPERIORES
# =====================================================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Entradas do Mês")

    entradas_tipos = pd.DataFrame({
        "Tipo": ["Cível", "Tax", "Labor", "Property Tax", "FAR", "Construction", "Delay"],
        "Quantidade": [300, 200, 150, 120, 180, 140, 110]
    })

    fig1 = px.bar(entradas_tipos, x="Tipo", y="Quantidade", text="Quantidade")
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.subheader("Saídas e Baixas")

    saidas = pd.DataFrame({
        "Categoria": ["Baixa Provisória"]*3 + ["Encerrados"]*3,
        "Resultado": ["Lost","Settled","Won"]*2,
        "Quantidade": [400,300,250,250,200,150]
    })

    cores = {
        "Lost": "#8B0000",
        "Settled": "#FE8C40",
        "Won": "#E8E118"
    }

    fig2 = go.Figure()

    for r in ["Lost","Settled","Won"]:
        df_temp = saidas[saidas["Resultado"] == r]
        fig2.add_trace(go.Bar(
            x=df_temp["Categoria"],
            y=df_temp["Quantidade"],
            name=r,
            marker_color=cores[r]
        ))

    fig2.update_layout(barmode="stack")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# =====================================================
# GRÁFICO FINAL
# =====================================================

st.subheader("Entradas x Saídas / Baixas")

serie = pd.DataFrame({
    "Mês": ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago"],
    "Entradas": [600,900,1300,1000,500,800,950,1200],
    "Saídas": [1000,700,1000,600,750,1100,850,980]
})

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=serie["Mês"], y=serie["Entradas"], mode="lines+markers", name="Entradas"))
fig3.add_trace(go.Scatter(x=serie["Mês"], y=serie["Saídas"], mode="lines+markers", name="Saídas"))

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# =====================================================
# PAINEL WIN / LOST
# =====================================================

with st.container():

    st.markdown("""
        <div style="
            background-color:#ffffff;
            padding:25px;
            border-radius:12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        ">
    """, unsafe_allow_html=True)

    st.markdown("### Baixa provisória e encerrados")

    dados = pd.DataFrame({
        "Status": ["Won", "Settled", "Lost", "Total"],
        "Quantidade de processos": [250, 260, 90, ""],
        "BP Atualizado": ["R$ 0,55M", "R$ 0,86M", "R$ 0,70M", "R$ 2,13M"],
        "Fcx Real": ["R$ 0", "R$ 0", "R$ 0,70M", "R$ 1,25M"],
        "Saving": ["45%", "0,33%", "0%", "0,83M"]
    })

    def icone(status):
        return {"Won":"✅","Settled":"🤝","Lost":"❌"}.get(status,"")

    dados.insert(0,"",dados["Status"].apply(icone))

    st.markdown("""
        <style>
        table { width:100%; border-collapse:collapse; font-size:15px; }
        thead tr { background:#e7d2c3; font-weight:600; }
        th,td { padding:12px; border:none; }
        tbody tr { border-bottom:1px solid #f0f0f0; }
        .saving-total { background:#c6e6c3; font-weight:600; }
        .total-row { font-weight:600; }
        </style>
    """, unsafe_allow_html=True)

    html = """
    <table>
        <thead>
            <tr>
                <th></th>
                <th>Quantidade de processos</th>
                <th>BP Atualizado</th>
                <th>Fcx Real</th>
                <th>Saving</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in dados.iterrows():
        is_total = row["Status"] == "Total"
        html += f"<tr class='{'total-row' if is_total else ''}'>"

        for col in dados.columns:
            if is_total and col == "Saving":
                html += f"<td class='saving-total'>{row[col]}</td>"
            else:
                html += f"<td>{row[col]}</td>"

        html += "</tr>"

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)