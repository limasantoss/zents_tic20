
def filtrar_por_periodo(df, data_inicio, data_fim, coluna='order_purchase_timestamp'):
    return df[
        (df[coluna].dt.date >= data_inicio) &
        (df[coluna].dt.date <= data_fim)
    ].copy()
