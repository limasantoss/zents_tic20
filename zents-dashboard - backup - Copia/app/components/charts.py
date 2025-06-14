
import plotly.express as px

def grafico_pedidos_por_mes(df, col_x='ano_mes', col_y='order_id', cor='#ff6600'):
    pedidos_mes = df.groupby(col_x)[col_y].count().reset_index(name='total_pedidos')
    fig = px.bar(
        pedidos_mes, x=col_x, y='total_pedidos', text_auto=True,
        title='Pedidos Realizados por Mês',
        color_discrete_sequence=[cor]
    )
    return fig

def grafico_distribuicao_valores(df, coluna, bins=40, cor='green'):
    fig = px.histogram(
        df, x=coluna, nbins=bins,
        title=f'Distribuição de {coluna}', color_discrete_sequence=[cor]
    )
    return fig

def grafico_mapa_calor_correlacao(df):
    import seaborn as sns
    import matplotlib.pyplot as plt

    corr = df.corr(numeric_only=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title('Mapa de Calor de Correlações')
    plt.tight_layout()
    plt.show()
