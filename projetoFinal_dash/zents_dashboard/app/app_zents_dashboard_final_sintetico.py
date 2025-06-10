
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Zents Marketplace - Dashboard Final",
    layout="wide",
    page_icon="📦"
)

# Logo e título
st.image("logo_zents.png", width=150)
st.markdown("<h2 style='color:#ff6600;'>Painel Gerencial da Zents Marketplace</h2>", unsafe_allow_html=True)
st.caption("Dashboard baseado em dataset otimizado para desempenho.")

# Carregar dataset consolidado
@st.cache_data
def carregar_dados():
    df = pd.read_csv("zents_dashboard_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"])
    return df

df = carregar_dados()

# Filtro de período
with st.sidebar:
    st.title("🔍 Filtros")
    data_min = df["order_purchase_timestamp"].min().date()
    data_max = df["order_purchase_timestamp"].max().date()
    intervalo = st.slider("🗓️ Período dos pedidos", min_value=data_min, max_value=data_max,
                          value=(data_min, data_max), format="DD/MM/YYYY")

inicio, fim = intervalo
df_filtros = df[
    (df["order_purchase_timestamp"].dt.date >= inicio) &
    (df["order_purchase_timestamp"].dt.date <= fim)
].copy()

if df_filtros.empty:
    st.warning("⚠️ Nenhum pedido encontrado no intervalo selecionado.")
    st.stop()

# Navegação
aba = st.radio("📂 Seções", ["Visão Geral", "Clientes (Lojas)", "Logística"], horizontal=True)
st.markdown("---")

# Visão Geral
if aba == "Visão Geral":
    st.markdown("<h3 style='color:#ff6600;'>📌 Visão Geral</h3>", unsafe_allow_html=True)
    df_validos = df_filtros.dropna(subset=["order_delivered_customer_date"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pedidos", f"{df_filtros['order_id'].nunique():,}")
    col2.metric("Tempo Médio de Entrega", f"{df_validos['tempo_entrega'].mean():.1f} dias")
    col3.metric("Vendedores Ativos", f"{df_filtros['seller_id'].nunique():,}")

    pedidos_mes = df_filtros.groupby("ano_mes")["order_id"].count().reset_index(name="total_pedidos")
    fig1 = px.bar(pedidos_mes, x="ano_mes", y="total_pedidos", text_auto=True,
                  title="Pedidos Realizados por Mês", color_discrete_sequence=["#ff6600"])
    st.plotly_chart(fig1, use_container_width=True)

# Clientes (Lojas)
elif aba == "Clientes (Lojas)":
    st.markdown("<h3 style='color:#ff6600;'>🏬 Clientes da Zents (Lojas)</h3>", unsafe_allow_html=True)
    top_sellers = df_filtros.groupby("seller_id")["order_id"].count().reset_index(name="total")
    top_sellers = top_sellers.sort_values(by="total", ascending=False).head(10)
    fig2 = px.bar(top_sellers, x="seller_id", y="total", text_auto=True,
                  title="Top 10 Lojas com Mais Pedidos", color_discrete_sequence=["#ff6600"])
    st.plotly_chart(fig2, use_container_width=True)

# Logística
elif aba == "Logística":
    st.markdown("<h3 style='color:#ff6600;'>📦 Logística de Entregas</h3>", unsafe_allow_html=True)
    df_validos = df_filtros.dropna(subset=["tempo_entrega"])
    tempo_estado = df_validos.groupby("customer_state")["tempo_entrega"].mean().reset_index()
    fig3 = px.bar(tempo_estado.sort_values(by="tempo_entrega", ascending=False),
                  x="customer_state", y="tempo_entrega", text_auto=".1f",
                  title="Tempo Médio de Entrega por Estado", color_discrete_sequence=["#ff6600"])
    st.plotly_chart(fig3, use_container_width=True)

    atraso = (df_validos["tempo_entrega"] > 10).mean() * 100
    st.metric("🚨 % de Entregas Atrasadas (>10 dias)", f"{atraso:.1f}%")

    top_lentos = df_validos.groupby("seller_id")["tempo_entrega"].mean().reset_index()
    top_lentos = top_lentos.sort_values(by="tempo_entrega", ascending=False).head(10)
    fig4 = px.bar(top_lentos, x="seller_id", y="tempo_entrega", text_auto=".1f",
                  title="Lojas com Maior Tempo Médio de Entrega", color_discrete_sequence=["#ff6600"])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Zents Marketplace - Versão otimizada para desempenho e clareza.")
