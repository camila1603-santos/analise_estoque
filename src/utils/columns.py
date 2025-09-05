"""
Utilitários para manipulação e identificação de colunas em DataFrames.

Este módulo foi criado para tornar a análise de estoque excedente mais flexível.
Ele oferece funções para localizar colunas principais (gerência, área, material,
quantidade) por meio de aliases e detectar colunas de valores e quantidades
mensais mesmo quando os nomes diferem do padrão antigo. Evite hardcoding de
nomes de colunas utilizando essas funções.

As funções principais são:
  - `get_col_gerencia`, `get_col_area`, `get_col_material`, `get_col_quantidade`:
    retornam o primeiro nome de coluna que contenha um dos aliases esperados.
  - `get_month_value_columns`:
    retorna uma lista ordenada de colunas que representam o valor monetário por
    mês. Suporta tanto o padrão "Valor Mês 01..12" quanto o padrão
    "Jan_Valor..Dez_Valor". Caso não encontre nenhum desses padrões,
    utiliza heurística para coletar colunas contendo "valor" acompanhadas de
    um número de mês.
  - `get_month_quantity_columns`:
    retorna uma lista ordenada de colunas que representam a quantidade por
    mês, no padrão "Jan_Qtd..Dez_Qtd" ou similar.

Estes utilitários facilitam a adaptação do código às mudanças no layout do CSV,
permitindo processar arquivos com mais ou menos colunas sem alterar a lógica
principal.
"""

from __future__ import annotations

import re
from typing import List, Tuple, Optional

import pandas as pd

# Aliases para colunas principais. São comparados de forma case-insensitive.
GERENCIA_ALIASES = ["gerência", "gerencia"]
AREA_ALIASES     = ["área", "area"]
MATERIAL_ALIASES = ["material"]
QUANTITY_ALIASES = ["quantidade", "qtd"]

# Abreviações dos meses em português (três letras) e seus índices (1‑12).
PT_MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
PT_INDEX  = {m: i + 1 for i, m in enumerate(PT_MONTHS)}

# Expressão regular para capturar números de mês em padrões como "Valor Mês 01"
# ou "mes 2". Ignora diferenças de acentuação.
MONTH_RX = re.compile(r"(?:valor\s*m[eê]s|m[eê]s)\s*(\d{1,2})", re.IGNORECASE)


def _find_first_by_alias(df: pd.DataFrame, aliases: List[str]) -> Optional[str]:
    """Retorna o nome da primeira coluna que contenha algum dos aliases.

    A busca é feita em ordem, retornando a primeira coincidência encontrada.
    Se nenhuma coluna corresponder, retorna ``None``.

    Args:
        df: DataFrame onde procurar as colunas.
        aliases: Lista de aliases (strings) para procurar nas colunas.

    Returns:
        O nome da coluna encontrada ou ``None`` se nenhuma coluna corresponder.
    """
    for col in df.columns:
        lower_name = str(col).strip().lower()
        for alias in aliases:
            if alias.lower() in lower_name:
                return col
    return None


def get_col_gerencia(df: pd.DataFrame) -> Optional[str]:
    """Retorna a coluna de gerência (Gerência/Gerencia), se existir."""
    return _find_first_by_alias(df, GERENCIA_ALIASES)


def get_col_area(df: pd.DataFrame) -> Optional[str]:
    """Retorna a coluna de área (Área/Area), se existir."""
    return _find_first_by_alias(df, AREA_ALIASES)


def get_col_material(df: pd.DataFrame) -> Optional[str]:
    """Retorna a coluna de material, se existir."""
    return _find_first_by_alias(df, MATERIAL_ALIASES)


def get_col_quantidade(df: pd.DataFrame) -> Optional[str]:
    """Retorna a coluna de quantidade consolidada (quando existe)."""
    return _find_first_by_alias(df, QUANTITY_ALIASES)


def get_month_value_columns(df: pd.DataFrame) -> List[str]:
    """Detecta e retorna as colunas de valores mensais ordenadas.

    Esta função reconhece dois padrões principais:
      1. Formato "Valor Mês 01", "Valor Mês 02", ... (ou variações como
         "valor mes 1", "Mes 2", etc.). Usa a regex ``MONTH_RX`` para extrair
         o número do mês e ordenar as colunas.
      2. Formato "Jan_Valor", "Fev_Valor", ..., "Dez_Valor". Identifica o
         prefixo do mês (três letras) antes de ``_Valor`` e utiliza a lista
         ``PT_MONTHS`` para definir a ordem.

    Se nenhum desses padrões for encontrado, a função procura colunas que
    contenham a palavra "valor" e um número de mês em seu nome, ordenando por
    esse número. Caso ainda assim nada seja encontrado, retorna lista vazia.

    Args:
        df: DataFrame analisado.

    Returns:
        Lista de nomes de colunas contendo valores mensais, na ordem cronológica.
    """
    matches: List[Tuple[int, str]] = []

    # Primeiro, tenta o formato com "Valor Mês XX".
    for col in df.columns:
        m = MONTH_RX.search(str(col))
        if m:
            try:
                month_number = int(m.group(1))
                matches.append((month_number, col))
            except Exception:
                pass

    if matches:
        matches.sort(key=lambda x: x[0])
        return [c for _, c in matches]

    # Segundo, tenta o formato "Jan_Valor", "Fev_Valor", etc.
    matches = []
    for col in df.columns:
        name = str(col).strip()
        lower = name.lower()
        if "valor" in lower:
            # procura prefixo com mês PT_MONTHS
            for month in PT_MONTHS:
                # aceita separador "_" ou espaço
                prefix = month.lower()
                if lower.startswith(prefix + "_") or lower.startswith(prefix + " "):
                    matches.append((PT_INDEX[month], col))
                    break

    if matches:
        matches.sort(key=lambda x: x[0])
        return [c for _, c in matches]

    # Por fim, procura colunas que contenham "valor" e número de mês em seu nome.
    # Útil para padrões imprevistos como "valor01", "valor_mes3".
    matches = []
    for col in df.columns:
        lower = str(col).lower()
        if "valor" in lower:
            for mm in range(1, 13):
                # procura por 01..12 ou 1..12 circundado por separadores
                if f"{mm:02d}" in lower or f" {mm} " in lower:
                    matches.append((mm, col))
                    break
    if matches:
        matches.sort(key=lambda x: x[0])
        return [c for _, c in matches]

    return []


def get_month_quantity_columns(df: pd.DataFrame) -> List[str]:
    """Detecta colunas de quantidades mensais no formato "Jan_Qtd..Dez_Qtd".

    Procura colunas com sufixo ``_Qtd`` (ou variações como "quantidade")
    precedido de abreviações de meses em português. Retorna a lista ordenada
    conforme ``PT_MONTHS``. Se nenhuma coluna for encontrada, retorna lista
    vazia.

    Args:
        df: DataFrame analisado.

    Returns:
        Lista de nomes de colunas de quantidades mensais ordenadas.
    """
    matches: List[Tuple[int, str]] = []
    for col in df.columns:
        name = str(col).strip()
        lower = name.lower()
        if any(q in lower for q in ["qtd", "quantidade"]):
            for month in PT_MONTHS:
                prefix = month.lower()
                if lower.startswith(prefix + "_") or lower.startswith(prefix + " "):
                    matches.append((PT_INDEX[month], col))
                    break
    matches.sort(key=lambda x: x[0])
    return [c for _, c in matches]
