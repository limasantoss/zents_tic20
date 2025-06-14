
import pandas as pd

def carregar_csv(path, parse_dates=None):
    """Carrega um CSV com parseamento de datas."""
    return pd.read_csv(path, parse_dates=parse_dates)

def calcular_tempo_entrega(df, col_entrega='order_delivered_customer_date', col_compra='order_purchase_timestamp'):
    """Cria a coluna tempo de entrega."""
    df['tempo_entrega'] = (df[col_entrega] - df[col_compra]).dt.days
    return df

def identificar_outliers_iqr(serie):
    """Retorna booleano indicando outliers com base no IQR."""
    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1
    return (serie < q1 - 1.5 * iqr) | (serie > q3 + 1.5 * iqr)

def remover_outliers(df, coluna):
    """Remove linhas com outliers na coluna especificada."""
    outliers = identificar_outliers_iqr(df[coluna])
    return df[~outliers]

def salvar_dataset_final(df, caminho='../../data/processed/zents_dashboard_dataset_final.csv'):
    """Salva o dataset final consolidado."""
    df.to_csv(caminho, index=False)

def consolidar_dados(pedidos, itens, pagamentos, clientes, vendedores):
    """Exemplo de consolidação dos dados principais."""
    df = pedidos.merge(itens, on='order_id', how='left') \
                .merge(pagamentos, on='order_id', how='left') \
                .merge(clientes, on='customer_id', how='left') \
                .merge(vendedores, on='seller_id', how='left')
    return df
