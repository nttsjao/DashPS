# 📦 Dependências
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 🎨 Configuração do layout da página
st.set_page_config(
    page_title="📱 Dashboard Phone Store",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎯 Estilização global
st.markdown("""
    <style>
        h1 {
            font-size: 36px !important;
            color: black;
            text-align: center; /* Centraliza o título */
            margin-top: 10px; /* Margem superior para o título após a logo */
            margin-bottom: 0px; /* Reduz a margem inferior do título */
        }
        h2 {
            font-size: 20px !important;
            color: black;
            margin-top: 10px; /* Ajusta a margem superior dos subtítulos */
            margin-bottom: 10px; /* Ajusta a margem inferior dos subtítulos */
        }
        p, label, .stMetric {
            font-size: 16px !important;
            color: #fff;
        }
        /* Centraliza a imagem */
        .stImage {
            display: inline;
            justify-content: center; /* Centraliza a imagem horizontalmente */
            margin-bottom: 0px; /* Remove margem abaixo da imagem para aproximar do título */
        }
        /* Ajusta o espaçamento das divisões */
        hr {
            margin-top: 15px; /* Margem superior da linha divisória */
            margin-bottom: 15px; /* Margem inferior da linha divisória */
        }
        /* Ajusta o espaçamento dos componentes gerais */
        .stBlock {
            margin-bottom: 0px; /* Reduz o espaçamento entre blocos gerais do Streamlit */
        }
    </style>
""", unsafe_allow_html=True)

st.image("Logo phone branca e amarela .png", width=200) # Ajuste a largura conforme necessário
st.markdown("<h1>📱 Dashboard Comercial - Phone Store</h1>", unsafe_allow_html=True)

st.markdown("---") 

# 🧠 Funções auxiliares
def converter_para_float(df, colunas):
    for col in colunas:
        if df[col].dtype == 'object':
            temp = df[col].astype(str).str.replace(r'[R$\s]', '', regex=True)
            temp = temp.apply(lambda x: corrigir_numero_str(x))
            temp = temp.str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(temp, errors='coerce')
    return df

def corrigir_numero_str(valor_str):
    qtd_pontos = valor_str.count('.')
    if qtd_pontos <= 1:
        return valor_str
    partes = valor_str.rsplit('.', 1)
    parte_esquerda = partes[0].replace('.', '')
    parte_direita = partes[1]
    return parte_esquerda + '.' + parte_direita

def tratar_percentual(coluna):
    return (
        coluna.astype(str)
        .str.replace('%', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

def cor_atingimento(porcentagem):
    if porcentagem >= 65:
        return "green"
    elif porcentagem >= 51 and porcentagem <=64:
        return "yellow"
    else:
        return "red"

# 📂 Leitura dos dados
visao_lojas = pd.read_csv("Database Teste PS - VISÃO LOJAS.csv", sep=",")
visao_mensal = pd.read_csv("Database Teste PS - VISÃO MENSAL.csv", sep=",")
vendas_rede = pd.read_csv("Database Teste PS - VENDAS REDE.csv", sep=",")

# 🔍 Limpeza e conversão de dados
for df in [visao_lojas, visao_mensal, vendas_rede]:
    df.columns = df.columns.str.strip()

visao_mensal = converter_para_float(visao_mensal, ["META MENSAL", "ACUMULADO MÊS"])
vendas_rede = converter_para_float(vendas_rede, ["META MENSAL", "ACUMULADO DO MÊS"])
visao_lojas = converter_para_float(visao_lojas, ["VALOR VENDA"])

visao_mensal["% ATINGIMENTO"] = tratar_percentual(visao_mensal["% ATINGIMENTO"])

# ===== Seção 01: Visão Geral =====
st.subheader("📊 Visão Geral da Rede")
periodo = st.radio("Selecione o período:", ["Mensal", "Trimestral"], horizontal=True)

meta_total = vendas_rede["META MENSAL"].sum()
vendas_total = vendas_rede["ACUMULADO DO MÊS"].sum()

if meta_total != 0:
    atingimento = (vendas_total / meta_total) * 100
else:
    atingimento = 0

cor_meta = cor_atingimento(atingimento)

col1, col2, col3 = st.columns(3)
col1.metric("🎯 Meta Consolidada", f"R$ {meta_total:,.2f}")
col2.metric("💰 Faturamento Total", f"R$ {vendas_total:,.2f}")
col3.markdown(f"<h3 style='color:{cor_meta}'>📈 {atingimento:.1f}% de Atingimento</h3>", unsafe_allow_html=True)

# Performance da Rede (usando visao_mensal com coluna LOJA)
st.markdown("<h2>📉 Performance Trimestral</h2>", unsafe_allow_html=True)
cores_lojas= {
    "Terminal":"#FF0000",
    "Patio 1": "#FFFF00",
    "Patio 2": "#00FF00",
    "Castanheira Q": "#0000FF",
    "Castanheira L": "#00FFFF",
    "Metropole Q": "#FF00FF",
    "Metropole L": "#FFA500",
    "Cidade Nova": "#800080",
    "Abaete Q": "#804000",
    "Abaete L": "#ADD8E6",
    "Castanhal": "#FF69B4",
    "Parauapebas": "#008000",
}


fig_trimestre = px.bar( 
    visao_mensal,
    x="MÊS",                  
    y="ACUMULADO MÊS",        
    color="LOJA",             
    title="Variação de Faturamento por Loja (Trimestre)",
    color_discrete_map=cores_lojas,  
    barmode='group',          
    category_orders={"MÊS": ["ABRIL", "MAIO", "JUNHO"]}
)

fig_trimestre.update_layout(
    xaxis_title="Mês",
    yaxis_title="Faturamento",
    title_font_size=16,
    # Adicionais para o tema escuro e clareza
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',  
    font_color="white",            
    showlegend=True,               
    legend_title_text='Loja'       
)

st.plotly_chart(fig_trimestre, use_container_width=True)

# ===== Seção 02: Comparativo por Loja =====
st.markdown("<h2>🏬 Comparativo por Loja</h2>", unsafe_allow_html=True)

tons_amarelos = ['#fff5cc', '#ffe066', '#ffcc00', '#e6b800', '#cca300']

fig_bar = px.bar(
    visao_mensal,
    x="LOJA",
    y="% ATINGIMENTO",
    color="MÊS",
    barmode="group",
    title="% de Atingimento por Loja e Mês",
    text_auto=".1f",
    color_discrete_sequence=tons_amarelos
)

fig_bar.update_layout(
    xaxis_title="Loja",
    yaxis_title="% Atingimento",
    legend_title_text="Período (Mês)",
    title_font_size=16
)
st.plotly_chart(fig_bar, use_container_width=True)

# ===== Seção 03: Detalhamento por Loja =====
st.markdown("<h2>🔍 Detalhamento por Loja</h2>", unsafe_allow_html=True)
loja_escolhida = st.selectbox("Selecione uma loja:", visao_lojas["LOJA"].unique())
dados_loja = visao_lojas[visao_lojas["LOJA"] == loja_escolhida]
dados_mensal_loja = visao_mensal[visao_mensal["LOJA"] == loja_escolhida]

if not dados_loja.empty:

    # ===== Indicadores da Loja =====
    if not dados_mensal_loja.empty:
        st.markdown("<h3>📊 Indicadores da Loja</h3>", unsafe_allow_html=True)

        # Seleciona o último mês disponível para a loja
        info = dados_mensal_loja.sort_values("MÊS").iloc[-1]

        # Constrói DataFrame com tipos numéricos
        indicadores = pd.DataFrame([{
            "MÊS REFERENTE": info["MÊS"],
            "META MENSAL (R$)": pd.to_numeric(info["META MENSAL"], errors="coerce"),
            "TOTAL VENDAS (R$)": pd.to_numeric(info["TOTAL VENDAS"], errors="coerce"),
            "ACUMULADO MÊS (R$)": pd.to_numeric(info["ACUMULADO MÊS"], errors="coerce"),
            "TICKET MÉDIO (R$)": pd.to_numeric(info["TICKET MÉDIO"], errors="coerce"),
            "PERFORMANCE (%)": pd.to_numeric(info["PERFORMANCE"], errors="coerce"),
            "% ATINGIMENTO (%)": pd.to_numeric(info["% ATINGIMENTO"], errors="coerce")
        }])

        # Exibe a tabela formatada
        st.dataframe(indicadores.style.format({
            "META MENSAL (R$)": "R$ {:,.2f}",
            "TOTAL VENDAS (R$)": "R$ {:,.2f}",
            "ACUMULADO MÊS (R$)": "R$ {:,.2f}",
            "TICKET MÉDIO (R$)": "R$ {:,.2f}",
            "PERFORMANCE (%)": "{:.1f}%",
            "% ATINGIMENTO (%)": "{:.1f}%"
        }))

        st.write("")  # Força a renderização

    # ===== Gráfico de Mix Vendido =====
    mix = dados_loja.groupby("CATEGORIA")["VALOR VENDA"].sum().reset_index()
    fig_mix = px.pie(
        mix,
        names="CATEGORIA",
        values="VALOR VENDA",
        title="Mix Vendido: Smartphones x Acessórios",
        hole=0.3,
        color_discrete_sequence=["gold", "orange", "brown"]
    )
    fig_mix.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_mix, use_container_width=True)

    # ===== Rankings =====
    st.markdown("<h3>🏆 Top 3 Consultores</h3>", unsafe_allow_html=True)
    top_vend = dados_loja.groupby("CONSULTOR")["VALOR VENDA"].sum().nlargest(3).reset_index()
    st.dataframe(top_vend)

    st.markdown("<h3>📦 Top 3 Produtos</h3>", unsafe_allow_html=True)
    top_prod = dados_loja.groupby("PRODUTO")["VALOR VENDA"].sum().nlargest(3).reset_index()
    st.dataframe(top_prod)

    st.markdown("<h3>📚 Top 3 Categorias</h3>", unsafe_allow_html=True)
    top_cat = dados_loja.groupby("CATEGORIA")["VALOR VENDA"].sum().nlargest(3).reset_index()
    st.dataframe(top_cat)

# ===== Seção 04 e 05: Produtos / Vendedores =====
st.markdown("<h2>📊 Rankings</h2>", unsafe_allow_html=True)
opcoes = st.multiselect(
    "Escolha o(s) ranking(s) para exibir:",
    ["Produtos Mais Vendidos", "Ranking de Vendedores"],
    default=["Produtos Mais Vendidos", "Ranking de Vendedores"]
)

if "Produtos Mais Vendidos" in opcoes:
    ranking_produtos = (
        visao_lojas.groupby("PRODUTO")["VALOR VENDA"]
        .sum().reset_index().sort_values(by="VALOR VENDA", ascending=False)
    )
    fig_prod = px.bar(
        ranking_produtos.head(10),
        x="PRODUTO",
        y="VALOR VENDA",
        title="🏆 Produtos Mais Vendidos",
        text_auto=True,
        color_discrete_sequence=["#FDB462"] 
    )
    fig_prod.update_traces(textposition='outside')
    st.plotly_chart(fig_prod, use_container_width=True)

if "Ranking de Vendedores" in opcoes:
    ranking_vendedores = (
        visao_lojas.groupby("CONSULTOR")["VALOR VENDA"]
        .sum().reset_index().sort_values(by="VALOR VENDA", ascending=False)
    )
    fig_vend = px.bar(
        ranking_vendedores.head(10),
        x="CONSULTOR",
        y="VALOR VENDA",
        title="🧑‍💼 Ranking de Vendedores",
        text_auto=True,
        color_discrete_sequence=["#FDB462"]
    )
    fig_vend.update_traces(textposition='outside')
    st.plotly_chart(fig_vend, use_container_width=True)

# Rodapé
st.markdown("""
    ---
    <p style='text-align:center;color:gray'>
        Dashboard gerado como simulação do teste técnico da Phone Store 📱
    </p>
""", unsafe_allow_html=True)