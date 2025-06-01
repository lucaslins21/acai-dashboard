import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Diagnóstico da Loja de Açaí",
    page_icon="💜",
    layout="wide" 
)

#função para Carregar Dados (com cache para performance)
@st.cache_data
def load_data():
    df = pd.read_csv('vendas_acai_dataset_faker_new.csv', decimal=',')
    df['Data'] = pd.to_datetime(df['Data'])
    df['Hora_Pedido'] = pd.to_datetime(df['Hora_Pedido']).dt.time
    df['Ano_Mes'] = df['Data'].dt.to_period('M').astype(str)
    dias_semana_ptbr = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    df['Dia_Semana'] = df['Data'].dt.dayofweek.map(lambda x: dias_semana_ptbr[x])

    df['Mes_Nome'] = df['Data'].dt.month_name(locale='pt_BR')

    df['Lucro_Total'] = pd.to_numeric(df['Lucro_Total'], errors='coerce')
    df['Total_Venda'] = pd.to_numeric(df['Total_Venda'], errors='coerce')

    return df

df = load_data()

#customização de Cores (Açaí Theme)
ACAI_COLORS = {
    'purple': '#6A057F', 
    'dark_purple': '#4A005D',
    'green': '#008000',  
    'brown': '#8B4513',  
    'pink': '#FF69B4',   
    'orange': '#FF8C00',  
    'light_grey': '#F8F9FA', 
    'text_color': '#343A40' 
}

#filtros sidebar
st.sidebar.header("Filtros de Análise")
st.sidebar.markdown("---")

#filtro de loja
lojas = df['Loja'].unique().tolist()
if len(lojas) > 1:
    loja_selecionada = st.sidebar.multiselect(
        "Loja(s):",
        options=sorted(lojas),
        default=sorted(lojas)
    )
    df_filtered = df[df['Loja'].isin(loja_selecionada)]
else:
    df_filtered = df.copy()

#filtro de bairro
bairros = df_filtered['Bairro'].unique().tolist()
bairro_selecionado = st.sidebar.multiselect(
    "Bairro(s):",
    options=sorted(bairros),
    default=sorted(bairros)
)
df_filtered = df_filtered[df_filtered['Bairro'].isin(bairro_selecionado)]

#filtro de data
min_date = df_filtered['Data'].min().date()
max_date = df_filtered['Data'].max().date()
date_range = st.sidebar.slider(
    "Intervalo de Datas:",
    value=(min_date, max_date),
    format="DD/MM/YYYY"
)
df_filtered = df_filtered[df_filtered['Data'].dt.date.between(date_range[0], date_range[1])]

#filtro de dia de semana
dias_semana_ordem = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
dias_semana_disponiveis = [d for d in dias_semana_ordem if d in df_filtered['Dia_Semana'].unique()]

dia_semana_selecionado = st.sidebar.multiselect(
    "Dia(s) da Semana:",
    options=dias_semana_disponiveis,
    default=dias_semana_disponiveis
)
df_filtered = df_filtered[df_filtered['Dia_Semana'].isin(dia_semana_selecionado)]

#filtro de horario
horas_unicas = sorted(list(set(df_filtered['Hora_Pedido'].astype(str).tolist())))
if horas_unicas:
    min_hora_str = min(horas_unicas)
    max_hora_str = max(horas_unicas)

    hora_range_selecionada = st.sidebar.slider(
        "Intervalo de Horas:",
        min_value=pd.to_datetime(min_hora_str).time(),
        max_value=pd.to_datetime(max_hora_str).time(),
        value=(pd.to_datetime(min_hora_str).time(), pd.to_datetime(max_hora_str).time()),
        format="HH:00"
    )
    df_filtered = df_filtered[
        (df_filtered['Hora_Pedido'] >= hora_range_selecionada[0]) &
        (df_filtered['Hora_Pedido'] <= hora_range_selecionada[1])
    ]

#filtro de produto
produtos = df_filtered['Produto'].unique().tolist()
produto_selecionado = st.sidebar.multiselect(
    "Produto(s):",
    options=sorted(produtos),
    default=sorted(produtos)
)
df_filtered = df_filtered[df_filtered['Produto'].isin(produto_selecionado)]

#filtro de categoria de produto
categorias = df_filtered['Categoria_Produto'].unique().tolist()
categoria_selecionada = st.sidebar.multiselect(
    "Categoria(s) de Produto:",
    options=sorted(categorias),
    default=sorted(categorias)
)
df_filtered = df_filtered[df_filtered['Categoria_Produto'].isin(categoria_selecionada)]

#filtro de canal de vendas
canais = df_filtered['Canal_Venda'].unique().tolist()
canal_selecionado = st.sidebar.multiselect(
    "Canal(is) de Venda:",
    options=sorted(canais),
    default=sorted(canais)
)
df_filtered = df_filtered[df_filtered['Canal_Venda'].isin(canal_selecionado)]

#filtro de forma de pagamento
pagamentos = df_filtered['Forma_Pagamento'].unique().tolist()
pagamento_selecionado = st.sidebar.multiselect(
    "Forma(s) de Pagamento:",
    options=sorted(pagamentos),
    default=sorted(pagamentos)
)
df_filtered = df_filtered[df_filtered['Forma_Pagamento'].isin(pagamento_selecionado)]

#filtro de tipo de cliente
tipos_cliente = df_filtered['Tipo_Cliente'].unique().tolist()
if tipos_cliente:
    tipo_cliente_selecionado = st.sidebar.multiselect(
        "Tipo(s) de Cliente:",
        options=sorted(tipos_cliente),
        default=sorted(tipos_cliente)
    )
    df_filtered = df_filtered[df_filtered['Tipo_Cliente'].isin(tipo_cliente_selecionado)]

#filtro de promocao
promocao_ativa_options = df_filtered['Promocao_Ativa'].unique().tolist()
if True in promocao_ativa_options and False in promocao_ativa_options:
    promocao_ativa_selecionada = st.sidebar.checkbox(
        "Apenas vendas com Promoção Ativa?",
        value=False
    )
    if promocao_ativa_selecionada:
        df_filtered = df_filtered[df_filtered['Promocao_Ativa'] == True]

#filtro de clima
clima_options = df_filtered['Clima'].unique().tolist()
if clima_options:
    clima_selecionado = st.sidebar.multiselect(
        "Condição(ões) do Clima:",
        options=sorted(clima_options),
        default=sorted(clima_options)
    )
    df_filtered = df_filtered[df_filtered['Clima'].isin(clima_selecionado)]

st.sidebar.markdown("---")
st.sidebar.info("Utilize os filtros para explorar os dados de vendas da sua loja de açaí!")

#titulo
st.title("💜 Análise de Desempenho da Loja de Açaí")
st.markdown("Previsão de Vendas por Lucas Lins")
st.markdown(f"**Dados Filtrados:** {len(df_filtered)} vendas exibidas.")


st.subheader("Métricas Chave")


df_filtered['Total_Venda'] = pd.to_numeric(df_filtered['Total_Venda'], errors='coerce').fillna(0)
df_filtered['Lucro_Final'] = pd.to_numeric(df_filtered['Lucro_Final'], errors='coerce').fillna(0)
df_filtered['Margem_Percentual'] = pd.to_numeric(df_filtered['Margem_Percentual'], errors='coerce').fillna(0)
df_filtered['Tempo_Total_Servico'] = pd.to_numeric(df_filtered['Tempo_Total_Servico'], errors='coerce').fillna(0)
df_filtered['Avaliacao_Venda'] = pd.to_numeric(df_filtered['Avaliacao_Venda'], errors='coerce').fillna(0)
df_filtered['Quantidade_Vendida'] = pd.to_numeric(df_filtered['Quantidade_Vendida'], errors='coerce').fillna(0)


col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

def metric_card(label, value, icon_html, help_text=None):
    st.markdown(
        f"""
        <div style="
            background-color: {ACAI_COLORS['light_grey']};
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.05); /* Sombra mais sutil */
            text-align: center;
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 1px solid {ACAI_COLORS['purple']}20; /* Borda sutil na cor principal */
        ">
            <h3 style="color: {ACAI_COLORS['text_color']}; font-size: 1.1em; margin-bottom: 5px;">{label} {icon_html}</h3>
            <p style="color: {ACAI_COLORS['purple']}; font-size: 1.8em; font-weight: bold; margin: 0;">{value}</p>
            {f'<p style="font-size: 0.8em; color: {ACAI_COLORS["text_color"]}; margin-top: 5px;">{help_text}</p>' if help_text else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

with col1:
    total_venda = df_filtered['Total_Venda'].sum()
    metric_card(
        label="Total de Vendas",
        value=f"R$ {total_venda:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
        icon_html="<span style='font-size:1.2em;'>&#x1F4B0;</span>",
        help_text="Receita bruta total das vendas."
    )

with col2:
    total_lucro_final = df_filtered['Lucro_Final'].sum()
    metric_card(
        label="Lucro Líquido",
        value=f"R$ {total_lucro_final:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
        icon_html="<span style='font-size:1.2em;'>&#x1F4B8;</span>",
        help_text="Lucro após todos os custos e despesas."
    )

with col3:
    num_total_vendas = df_filtered['Total_Venda'].count()
    if num_total_vendas > 0:
        ticket_medio_venda = total_venda / num_total_vendas
        metric_card(
            label="Ticket Médio por Transação",
            value=f"R$ {ticket_medio_venda:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
            icon_html="<span style='font-size:1.2em;'>&#x1F6CD;</span>",
            help_text="Valor médio por transação."
        )
    else:
        metric_card(
            label="Ticket Médio por Transação",
            value="R$ 0,00",
            icon_html="<span style='font-size:1.2em;'>&#x1F6CD;</span>",
            help_text="Valor médio por transação."
        )

with col4:
    margem_media_percentual = df_filtered['Margem_Percentual'].mean()
    metric_card(
        label="Margem Média Percentual",
        value=f"{margem_media_percentual:,.2f}%".replace(",", "v").replace(".", ",").replace("v", "."),
        icon_html="<span style='font-size:1.2em;'>&#x1F4C8;</span>",
        help_text="Rentabilidade média de cada venda."
    )

with col5:
    if len(df_filtered) > 0:
        avg_tempo_servico = df_filtered['Tempo_Total_Servico'].mean()
        metric_card(
            label="Tempo Médio de Serviço",
            value=f"{avg_tempo_servico:,.2f} min",
            icon_html="<span style='font-size:1.2em;'>&#x23F1;</span>",
            help_text="Tempo médio para completar um pedido."
        )
    else:
        metric_card(
            label="Tempo Médio de Serviço",
            value="0,00 min",
            icon_html="<span style='font-size:1.2em;'>&#x23F1;</span>",
            help_text="Tempo médio para completar um pedido."
        )

with col6:
    if len(df_filtered) > 0:
        avg_avaliacao = df_filtered['Avaliacao_Venda'].mean()
        metric_card(
            label="Avaliação Média de Venda",
            value=f"{avg_avaliacao:,.2f} ⭐",
            icon_html="<span style='font-size:1.2em;'>&#x2B50;</span>",
            help_text="Satisfação média dos clientes."
        )
    else:
        metric_card(
            label="Avaliação Média de Venda",
            value="0,00 ⭐",
            icon_html="<span style='font-size:1.2em;'>&#x2B50;</span>",
            help_text="Satisfação média dos clientes."
        )

st.markdown("---")

#graficos
st.subheader("Análises Detalhadas")

#Vendas e Lucro ao Longo do Tempo (Linha)
st.markdown("#### Vendas e Lucro por Período")
vendas_por_data = df_filtered.groupby('Data')[['Total_Venda', 'Lucro_Final']].sum().reset_index()
fig1 = px.line(
    vendas_por_data,
    x='Data',
    y=['Total_Venda', 'Lucro_Final'],
    title='Receita e Lucro ao Longo do Tempo',
    labels={'value':'Valor (R$)', 'Data':'Data', 'variable':'Métrica'},
    color_discrete_map={'Total_Venda': ACAI_COLORS['purple'], 'Lucro_Final': ACAI_COLORS['green']}
)
fig1.update_layout(hovermode="x unified", title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig1, use_container_width=True)

#Vendas por Dia da Semana (Barras)
st.markdown("#### Vendas por Dia da Semana")
dias_semana_ordem = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
vendas_por_dia_semana = df_filtered.groupby('Dia_Semana')['Total_Venda'].sum().reindex(dias_semana_ordem, fill_value=0).reset_index()
fig2 = px.bar(
    vendas_por_dia_semana,
    x='Dia_Semana',
    y='Total_Venda',
    title='Receita Total por Dia da Semana',
    labels={'Dia_Semana':'Dia da Semana', 'Total_Venda':'Receita Total (R$)'},
    color_discrete_sequence=[ACAI_COLORS['dark_purple']]
)
fig2.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig2, use_container_width=True)

#Top 10 Produtos por Receita (Barras)
st.markdown("#### Top 10 Produtos por Receita")
top_produtos = df_filtered.groupby('Produto')['Total_Venda'].sum().nlargest(10).reset_index()
fig3 = px.bar(
    top_produtos,
    x='Total_Venda',
    y='Produto',
    orientation='h',
    title='Top 10 Produtos com Maior Receita',
    labels={'Produto':'Produto', 'Total_Venda':'Receita Total (R$)'},
    color_discrete_sequence=[ACAI_COLORS['purple']]
)
fig3.update_layout(yaxis={'categoryorder':'total ascending'}, title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig3, use_container_width=True)

#Distribuição de Vendas por Canal e Forma de Entrega (Pizza ou Barras)
col_g4_1, col_g4_2 = st.columns(2)
with col_g4_1:
    st.markdown("#### Vendas por Canal de Venda")
    vendas_por_canal = df_filtered.groupby('Canal_Venda')['Total_Venda'].sum().reset_index()
    fig4_1 = px.pie(
        vendas_por_canal,
        values='Total_Venda',
        names='Canal_Venda',
        title='Distribuição da Receita por Canal de Venda',
        hole=0.3,
        color_discrete_sequence=[ACAI_COLORS['purple'], ACAI_COLORS['green'], ACAI_COLORS['brown'], ACAI_COLORS['pink']]
    )
    fig4_1.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
    st.plotly_chart(fig4_1, use_container_width=True)

with col_g4_2:
    st.markdown("#### Vendas por Forma de Entrega")
    vendas_por_entrega = df_filtered.groupby('Forma_Entrega')['Total_Venda'].sum().reset_index()
    fig4_2 = px.pie(
        vendas_por_entrega,
        values='Total_Venda',
        names='Forma_Entrega',
        title='Distribuição da Receita por Forma de Entrega',
        hole=0.3,
        color_discrete_sequence=[ACAI_COLORS['dark_purple'], ACAI_COLORS['orange'], ACAI_COLORS['green']]
    )
    fig4_2.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
    st.plotly_chart(fig4_2, use_container_width=True)

#Vendas por Hora do Pedido (Barras)
st.markdown("#### Vendas por Hora do Pedido")
df_filtered['Hora_Pedido_Int'] = df_filtered['Hora_Pedido'].apply(lambda x: x.hour)
vendas_por_hora = df_filtered.groupby('Hora_Pedido_Int')['Total_Venda'].sum().reset_index()
fig5 = px.bar(
    vendas_por_hora,
    x='Hora_Pedido_Int',
    y='Total_Venda',
    title='Receita Total por Hora do Dia',
    labels={'Hora_Pedido_Int':'Hora do Dia (24h)', 'Total_Venda':'Receita Total (R$)'},
    color_discrete_sequence=[ACAI_COLORS['purple']]
)
fig5.update_layout(xaxis_dtick=1, title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig5, use_container_width=True)

#Média de Avaliação por Bairro (Barras)
st.markdown("#### Avaliação Média por Bairro")
avaliacoes_por_bairro = df_filtered[df_filtered['Avaliacao_Venda'] > 0].groupby('Bairro')['Avaliacao_Venda'].mean().reset_index()
if not avaliacoes_por_bairro.empty:
    fig6 = px.bar(
        avaliacoes_por_bairro.sort_values('Avaliacao_Venda', ascending=False),
        x='Bairro',
        y='Avaliacao_Venda',
        title='Avaliação Média de Venda por Bairro',
        labels={'Bairro':'Bairro', 'Avaliacao_Venda':'Avaliação Média (1-5)'},
        color_discrete_sequence=[ACAI_COLORS['green']]
    )
    fig6.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("Nenhum dado de avaliação para o bairro selecionado.")

#Impacto de Promoção Ativa na Venda (Barras Comparativas)
st.markdown("#### Impacto de Promoções nas Vendas")
vendas_por_promocao = df_filtered.groupby('Promocao_Ativa')['Total_Venda'].sum().reset_index()
fig7 = px.bar(
    vendas_por_promocao,
    x='Promocao_Ativa',
    y='Total_Venda',
    title='Receita Total com e sem Promoção Ativa',
    labels={'Promocao_Ativa':'Promoção Ativa', 'Total_Venda':'Receita Total (R$)'},
    color='Promocao_Ativa',
    color_discrete_map={True: ACAI_COLORS['purple'], False: ACAI_COLORS['pink']}
)
fig7.update_xaxes(tickvals=[True, False], ticktext=['Sim', 'Não'])
fig7.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig7, use_container_width=True)

#Lucro por Categoria de Produto (Barras)
st.markdown("#### Lucro por Categoria de Produto")
lucro_por_categoria = df_filtered.groupby('Categoria_Produto')['Lucro_Final'].sum().reset_index()
fig8 = px.bar(
    lucro_por_categoria.sort_values('Lucro_Final', ascending=False),
    x='Categoria_Produto',
    y='Lucro_Final',
    title='Lucro Líquido por Categoria de Produto',
    labels={'Categoria_Produto':'Categoria de Produto', 'Lucro_Final':'Lucro Líquido (R$)'},
    color_discrete_sequence=[ACAI_COLORS['brown']]
)
fig8.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig8, use_container_width=True)

#Vendas por Temperatura do Dia (Dispersão)
st.markdown("#### Vendas vs. Temperatura do Dia")
vendas_por_temperatura = df_filtered.groupby('Temperatura_Dia')['Total_Venda'].sum().reset_index()
fig9 = px.scatter(
    vendas_por_temperatura,
    x='Temperatura_Dia',
    y='Total_Venda',
    size='Total_Venda',
    title='Receita Total por Temperatura do Dia',
    labels={'Temperatura_Dia':'Temperatura (°C)', 'Total_Venda':'Receita Total (R$)'},
    trendline='ols',
    color_discrete_sequence=[ACAI_COLORS['orange']]
)
fig9.update_layout(title_font_size=20, title_font_color=ACAI_COLORS['text_color'])
st.plotly_chart(fig9, use_container_width=True)

#tabela
st.markdown("---")
st.subheader("Dados Detalhados das Vendas (Filtrados)")
st.dataframe(df_filtered)

#rodape
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f2f6;
        color: #888;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
        border-top: 1px solid #e6e6e6;
    }
    </style>
    <div class="footer">
        Desenvolvido com ❤️ para o curso Ciência de Dados Aplicada à Competitividade das Micro e Pequenas Empresas (MPEs) | © 2025
    </div>
    """, unsafe_allow_html=True)