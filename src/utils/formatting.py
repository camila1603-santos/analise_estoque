"""
Funções utilitárias de formatação numérica e monetária.
"""

from typing import Any
import pandas as pd

def safe_format_currency(value: Any) -> str:
    """
    Formata um valor numérico como moeda brasileira.
    """
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def safe_format_number(value: Any) -> str:
    """
    Formata um número inteiro com separador de milhar.
    """
    try:
        return f"{int(value):,}".replace(",", ".")
    except Exception:
        return "0"

def format_currency_compact(value: float) -> str:
    """
    Formata valores em estilo compacto (K, M), útil em gráficos.
    """
    try:
        if pd.isna(value) or value == 0:
            return "R$ 0"
        if value >= 1_000_000:
            return f"R$ {value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"R$ {value/1_000:.1f}K"
        else:
            return f"R$ {value:.0f}"
    except Exception:
        return "R$ 0"
