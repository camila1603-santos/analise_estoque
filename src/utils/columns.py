"""
Utilitários para manipulação e identificação de colunas em DataFrames.
"""

import pandas as pd
from typing import List

# Padrões comuns para nomes de colunas
MONTH_PATTERNS = ['valor mês', 'valor_mes', 'mês']
QUANTITY_PATTERNS = ['quantidade', 'qtd']

def find_columns_by_pattern(df: pd.DataFrame, patterns: List[str]) -> List[str]:
    """
    Retorna colunas do DataFrame que contenham algum dos padrões informados.

    Args:
        df: DataFrame de entrada
        patterns: Lista de substrings a procurar

    Returns:
        Lista de colunas correspondentes
    """
    found_columns = []
    for col in df.columns:
        for pattern in patterns:
            if pattern.lower() in col.lower():
                found_columns.append(col)
                break
    return found_columns