import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# Configuração da página
st.set_page_config(
    page_title="Zents Marketplace - Dashboard Final",
    layout="wide",
    page_icon="📦"
)

# CSS para sidebar 
st.markdown(
    """
    <style>
        /* Sidebar background roxo escuro */
        .css-1d391kg {
            background-color: #350866 !important;
            color: white !important;
        }
        /* Custom scroll bar da sidebar */
        .css-1d391kg::-webkit-scrollbar-thumb {
            background-color: #FF6F17 !important;
        }
        /* Ajustar título no menu */
        .streamlit-expanderHeader {
            color: #FF6F17 !important;
        }

        /* Estilos chatbot customizado */
        .chatbot-container {
            background-color: #F5F0FF;  /* lilás clarinho */
            border: 2px solid #FF6F17;  /* laranja */
            border-radius: 12px;
            padding: 15px 20px;
            margin-bottom: 20px;
            font-family: 'Arial', sans-serif;
            color: #350866;  /* roxo escuro */
        }
        .chatbot-info {
            background-color: #FFF3E0;  /* laranja clarinho */
            border-left: 6px solid #FF6F17;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 14px;
        }
        .chatbot-response {
            background-color: #EDE7F6;  /* lilás médio */
            border-radius: 8px;
            padding: 10px 15px;
            margin-top: 10px;
            font-size: 16px;
        }
    </style>
    """, unsafe_allow_html=True
)

# Logo e título no topo
st.image("../assets/logo_zents.png", width=200)
st.markdown("<h2 style='color:#FF6F17;'>Painel Gerencial Marketplace</h2>", unsafe_allow_html=True)



# Função para carregar dados
@st.cache_data
def carregar_dados():
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(caminho_base, "..", "data", "processed", "zents_dashboard_dataset_final.csv")
    df = pd.read_csv(
        caminho_csv,
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"]
    )
    colunas_necessarias = [
        "order_id", "seller_id", "tempo_entrega", "order_purchase_timestamp",
        "order_delivered_customer_date", "customer_state", "ano_mes"
    ]
    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"❌ A coluna '{col}' não está presente no dataset.")
            st.stop()
    return df

df = carregar_dados()

# Sidebar com menu estilizado
with st.sidebar:
    selected = option_menu(
        menu_title="Seções",
        options=["Visão Geral", "Clientes (Lojas)", "Logística"],
        icons=["bar-chart", "people-fill", "truck"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#350866"},
            "icon": {"color": "#FF6F17", "font-size": "20px"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#FF6F17",
                "color": "white"
            },
            "nav-link-selected": {"background-color": "#FF6F17", "color": "white"},
        }
    )
    st.markdown('<h4 style="color:#FF6F17;">🗓️ Período dos pedidos</h4>', unsafe_allow_html=True)

    data_min = df["order_purchase_timestamp"].min().date()
    data_max = df["order_purchase_timestamp"].max().date()
    intervalo = st.slider("",
                         min_value=data_min,
                         max_value=data_max,
                         value=(data_min, data_max),
                         format="DD/MM/YYYY")

inicio, fim = intervalo
df_filtros = df[
    (df["order_purchase_timestamp"].dt.date >= inicio) &
    (df["order_purchase_timestamp"].dt.date <= fim)
].copy()

if df_filtros.empty:
    st.warning("⚠️ Nenhum pedido encontrado no intervalo selecionado.")
    st.stop()

# Conteúdo das abas com gráficos
st.markdown("---")

if selected == "Visão Geral":
    st.markdown("<h3 style='color:#FF6F17;'>📌 Visão Geral</h3>", unsafe_allow_html=True)
    df_validos = df_filtros.dropna(subset=["order_delivered_customer_date"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pedidos", f"{df_filtros['order_id'].nunique():,}")
    col2.metric("Tempo Médio de Entrega", f"{df_validos['tempo_entrega'].mean():.1f} dias")
    col3.metric("Vendedores Ativos", f"{df_filtros['seller_id'].nunique():,}")

    pedidos_mes = df_filtros.groupby("ano_mes")["order_id"].count().reset_index(name="total_pedidos")
    fig1 = px.bar(
        pedidos_mes,
        x="ano_mes",
        y="total_pedidos",
        text="total_pedidos",
        color="total_pedidos",
        color_continuous_scale=px.colors.sequential.Oranges,
        title="Pedidos Realizados por Mês",
    )
    fig1.update_traces(
        textposition='outside',
        marker_line_color='rgba(255,111,23,0.8)',
        marker_line_width=1.5,
    )
    fig1.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickangle=-45,
            tickfont=dict(size=11, color='#350866'),
        ),
        yaxis=dict(
            gridcolor='rgba(53,8,102,0.1)',
            zeroline=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        title_font=dict(size=24, color='#FF6F17'),
        font=dict(family="Arial", size=12, color="#350866"),
        margin=dict(t=50, b=100),
    )
    st.plotly_chart(fig1, use_container_width=True)

elif selected == "Clientes (Lojas)":
    st.markdown("<h3 style='color:#FF6F17;'>🏬 Clientes da Zents (Lojas)</h3>", unsafe_allow_html=True)
    top_sellers = df_filtros.groupby("seller_id")["order_id"].count().reset_index(name="total")
    top_sellers = top_sellers.sort_values(by="total", ascending=False).head(10)
    fig2 = px.bar(
        top_sellers,
        x="seller_id",
        y="total",
        text="total",
        color="total",
        color_continuous_scale=px.colors.sequential.Oranges,
        title="Top 10 Lojas com Mais Pedidos",
    )
    fig2.update_traces(
        textposition='outside',
        marker_line_color='rgba(255,111,23,0.8)',
        marker_line_width=1.5,
    )
    fig2.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        yaxis=dict(
            gridcolor='rgba(53,8,102,0.1)',
            zeroline=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        title_font=dict(size=24, color='#FF6F17'),
        font=dict(family="Arial", size=12, color="#350866"),
        margin=dict(t=50, b=50),
    )
    st.plotly_chart(fig2, use_container_width=True)

elif selected == "Logística":
    st.markdown("<h3 style='color:#FF6F17;'>📦 Logística de Entregas</h3>", unsafe_allow_html=True)
    df_validos = df_filtros.dropna(subset=["tempo_entrega"])
    tempo_estado = df_validos.groupby("customer_state")["tempo_entrega"].mean().reset_index()
    fig3 = px.bar(
        tempo_estado.sort_values(by="tempo_entrega", ascending=False),
        x="customer_state",
        y="tempo_entrega",
        text="tempo_entrega",
        color="tempo_entrega",
        color_continuous_scale=px.colors.sequential.Oranges,
        title="Tempo Médio de Entrega por Estado *** corrigir ***",
    )
    fig3.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_line_color='rgba(255,111,23,0.8)',
        marker_line_width=1.5,
    )
    fig3.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        yaxis=dict(
            gridcolor='rgba(53,8,102,0.1)',
            zeroline=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        title_font=dict(size=24, color='#FF6F17'),
        font=dict(family="Arial", size=12, color="#350866"),
        margin=dict(t=50, b=50),
    )
    st.plotly_chart(fig3, use_container_width=True)

    atraso = (df_validos["tempo_entrega"] > 10).mean() * 100
    st.metric("🚨 % de Entregas Atrasadas (>10 dias)", f"{atraso:.1f}%")

    top_lentos = df_validos.groupby("seller_id")["tempo_entrega"].mean().reset_index()
    top_lentos = top_lentos.sort_values(by="tempo_entrega", ascending=False).head(10)
    fig4 = px.bar(
        top_lentos,
        x="seller_id",
        y="tempo_entrega",
        text="tempo_entrega",
        color="tempo_entrega",
        color_continuous_scale=px.colors.sequential.Oranges,
        title="Lojas com Maior Tempo Médio de Entrega",
    )
    fig4.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_line_color='rgba(255,111,23,0.8)',
        marker_line_width=1.5,
    )
    fig4.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        yaxis=dict(
            gridcolor='rgba(53,8,102,0.1)',
            zeroline=False,
            tickfont=dict(size=11, color='#350866'),
        ),
        title_font=dict(size=24, color='#FF6F17'),
        font=dict(family="Arial", size=12, color="#350866"),
        margin=dict(t=50, b=50),
    )
    st.plotly_chart(fig4, use_container_width=True)

# --- Chatbot 


#st.markdown("##  Chatbot ")
st.image("../assets/logo_boot.png", width=100   )#largura

with st.expander("Instruções - Exemplos de perguntas que você pode fazer:", expanded=True):
    st.markdown("""
    - Quantos pedidos foram feitos em maio?<br>
    - Qual foi o vendedor com mais vendas?<br>
    - Qual o status de entrega?<br>
    - Explique o gráfico de pedidos ~^ não ta funcionando ainda !!.<br>
    - Como navegar no dashboard?
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

user_input = st.text_input("Faça sua pergunta:")

if user_input:
    pergunta = user_input.lower()

    resposta = ""

    if "quantos pedidos" in pergunta and "feitos" in pergunta:
        meses = {
            "janeiro":1, "fevereiro":2, "março":3, "abril":4, "maio":5,
            "junho":6, "julho":7, "agosto":8, "setembro":9, "outubro":10,
            "novembro":11, "dezembro":12
        }
        mes_encontrado = None
        for m in meses.keys():
            if m in pergunta:
                mes_encontrado = meses[m]
                mes_nome = m.capitalize()
                break
        if mes_encontrado:
            total_pedidos_mes = df[df["order_purchase_timestamp"].dt.month == mes_encontrado]["order_id"].nunique()
            resposta = f"📦 Total de pedidos feitos em <b>{mes_nome}</b>: {total_pedidos_mes}"
        else:
            resposta = "Por favor, especifique o mês na pergunta (ex: 'maio')."

    elif "vendedor" in pergunta and "mais vendas" in pergunta:
        vendedor_top = df.groupby("seller_id")["order_id"].count().idxmax()
        total_vendas = df.groupby("seller_id")["order_id"].count().max()
        resposta = f"🏆 O vendedor com mais vendas é o <b>{vendedor_top}</b>, com <b>{total_vendas}</b> pedidos."

    elif "status de entrega" in pergunta or "atraso" in pergunta:
        df_validos = df.dropna(subset=["tempo_entrega"])
        atraso_pct = (df_validos["tempo_entrega"] > 10).mean() * 100
        resposta = f"🚚 A porcentagem de entregas atrasadas (mais de 10 dias) é de <b>{atraso_pct:.1f}%</b>."

    elif "explicar gráfico" in pergunta or "o que significa" in pergunta:
        resposta = ("📝 Os gráficos mostram o desempenho do marketplace, como o total de pedidos por mês, "
                    "top vendedores e tempo médio de entrega por estado.")

    elif "navegar" in pergunta or "como acessar" in pergunta:
        resposta = "🔍 Use o menu lateral para acessar as seções: Visão Geral, Clientes (Lojas) e Logística."

    else:
        resposta = ("🤖 Desculpe, não entendi a pergunta. Tente algo como:<br>"
                    "- Quantos pedidos foram feitos em maio?<br>"
                    "- Qual foi o vendedor com mais vendas?<br>"
                    "- Qual o status de entrega?<br>"
                    "- Explique o gráfico de pedidos.<br>"
                    "- Como navegar no dashboard?")

    st.markdown(f'<div class="chatbot-response">{resposta}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
