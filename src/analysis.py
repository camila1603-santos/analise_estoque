"""
Análise unificada de estoque excedente por gerência:
- KPIs por gerência
- Evolução mensal (ordenada)
- Top materiais
- Tabela detalhada
- Integração com IA clássica (ai.classic_ai)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional

import numpy as np  # (pode ser útil em futuras expansões; ok manter)
import pandas as pd


# IA clássica (mantenha caminho conforme sua estrutura)
# Tenta importar a partir do pacote 'ai.classic_ai'. Caso não exista,
# faz fallback para importar do módulo local 'classic_ai'. Essa abordagem
# evita erros de importação quando o projeto não está estruturado como pacote.
try:
    from ai.classic_ai import comprehensive_ai_analysis  # type: ignore
except ImportError:
    from classic_ai import comprehensive_ai_analysis  # type: ignore

# Utilitários para identificação dinâmica de colunas
from utils.columns import (
    get_col_gerencia,
    get_col_area,
    get_col_material,
    get_col_quantidade,
    get_month_value_columns,
    get_month_quantity_columns,
    PT_INDEX,
    PT_MONTHS,
    MONTH_RX,
)


# ---------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------

# A ordenação e detecção de colunas mensais são delegadas ao módulo
# ``columns.py``, que oferece funções robustas para encontrar colunas de
# valores e quantidades por mês. Assim, não há necessidade de manter
# uma função local `_month_columns_sorted` aqui.


def get_unique_gerencias(df: pd.DataFrame) -> List[str]:
    """Retorna a lista de gerências distintas, excluindo linhas agregadas.

    Esta função utiliza ``get_col_gerencia`` para localizar a coluna que
    representa a gerência. Caso não exista, retorna lista vazia. Linhas cujo
    valor da gerência comece com "total" (case-insensitive) são ignoradas.

    Args:
        df: DataFrame analisado.

    Returns:
        Lista de nomes de gerências ordenada.
    """
    col_g = get_col_gerencia(df)
    if not col_g:
        return []
    vals = df[col_g].dropna().map(str).tolist()
    # Remove valores que parecem ser totais agregados
    vals = [g for g in set(vals) if not g.lower().startswith("total")]
    return sorted(vals)


def _filter(df: pd.DataFrame, gerencia: str) -> pd.DataFrame:
    """Filtra o DataFrame por uma gerência específica, excluindo totais.

    A coluna de gerência é determinada por ``get_col_gerencia``. Caso não
    exista, retorna um DataFrame vazio.

    Args:
        df: DataFrame de origem.
        gerencia: Nome da gerência a filtrar.

    Returns:
        Subconjunto do DataFrame com apenas os registros da gerência, sem
        linhas cujo valor de gerência comece com "total".
    """
    col_g = get_col_gerencia(df)
    if not col_g:
        return pd.DataFrame()
    out = df[df[col_g].astype(str) == str(gerencia)].copy()
    # Remove linhas com 'Total' (acesso case-insensitive)
    out = out[~out[col_g].astype(str).str.lower().str.startswith("total")]
    return out


# ---------------------------------------------------------------------
# Cálculos por gerência
# ---------------------------------------------------------------------
def calculate_gerencia_kpis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """Calcula os principais KPIs para uma gerência específica.

    KPIs calculados:
      - ``valor_total``: soma do último mês disponível nas colunas de valor;
      - ``quantidade_total``: soma da coluna de quantidade consolidada ou
        soma das colunas de quantidade mensais quando a coluna consolidada não existe;
      - ``numero_materiais``: número de materiais distintos;
      - ``valor_medio_material``: ``valor_total`` dividido pelo número de materiais;
      - ``variacao_mensal``: variação percentual entre o primeiro e o último mês.

    Args:
        df: DataFrame de origem.
        gerencia: Gerência para a qual calcular os KPIs.

    Returns:
        Dicionário com os KPIs calculados e um campo ``status`` indicando
        "sucesso" ou "sem_dados" quando a gerência não possui registros.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return {
            "valor_total": 0.0,
            "quantidade_total": 0,
            "numero_materiais": 0,
            "valor_medio_material": 0.0,
            "variacao_mensal": 0.0,
            "status": "sem_dados",
        }

    # Colunas de valor por mês
    month_cols = get_month_value_columns(gdf)

    # Valor total = soma no último mês disponível
    valor_total = 0.0
    if month_cols:
        last_col = month_cols[-1]
        valor_total = pd.to_numeric(gdf[last_col], errors="coerce").fillna(0).sum()

    # Quantidade total (consolidada ou somatório de quantidades mensais)
    col_q = get_col_quantidade(gdf)
    if col_q:
        quantidade_total = pd.to_numeric(gdf[col_q], errors="coerce").fillna(0).sum()
    else:
        quantidade_total = 0
        q_month_cols = get_month_quantity_columns(gdf)
        for qcol in q_month_cols:
            quantidade_total += pd.to_numeric(gdf[qcol], errors="coerce").fillna(0).sum()

    # Número de materiais distintos
    col_m = get_col_material(gdf)
    numero_materiais = gdf[col_m].nunique() if col_m else 0

    # Valor médio por material
    valor_medio_material = float(valor_total) / max(1, int(numero_materiais))

    # Variação mensal: compara primeiro e último mês de valor
    variacao_mensal = 0.0
    if len(month_cols) >= 2:
        primeiro = pd.to_numeric(gdf[month_cols[0]], errors="coerce").fillna(0).sum()
        ultimo   = pd.to_numeric(gdf[month_cols[-1]], errors="coerce").fillna(0).sum()
        if primeiro > 0:
            variacao_mensal = ((ultimo - primeiro) / primeiro) * 100.0

    return {
        "valor_total": float(valor_total),
        "quantidade_total": int(quantidade_total),
        "numero_materiais": int(numero_materiais),
        "valor_medio_material": float(valor_medio_material),
        "variacao_mensal": float(variacao_mensal),
        "status": "sucesso",
    }


def get_monthly_evolution(df: pd.DataFrame, gerencia: str) -> List[Dict[str, Any]]:
    """Gera a evolução mensal de valor para uma gerência.

    Para cada coluna de valor mensal detectada pelo utilitário
    ``get_month_value_columns``, soma os valores da coluna e gera um dicionário
    com chave ``mes`` (mês em formato ``00``) e ``valor`` (soma das linhas).

    Args:
        df: DataFrame de origem.
        gerencia: Gerência para a qual calcular a evolução.

    Returns:
        Lista de dicionários no formato ``{"mes": "01", "valor": 123.45}``.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return []

    month_cols = get_month_value_columns(gdf)
    out: List[Dict[str, Any]] = []
    for idx, col in enumerate(month_cols):
        total = pd.to_numeric(gdf[col], errors="coerce").fillna(0).sum()
        # Determina o rótulo do mês (01..12) a partir do nome da coluna
        label: str
        m = MONTH_RX.search(str(col))
        if m:
            # Padrão "Valor Mês 01" → captura número
            label = m.group(1).zfill(2)
        else:
            # Verifica prefixo de mês (Jan, Fev, ...) e usa seu índice
            temp_label: Optional[str] = None
            col_lower = str(col).strip().lower()
            for month in PT_MONTHS:
                pref = month.lower()
                if col_lower.startswith(pref + "_") or col_lower.startswith(pref + " "):
                    temp_label = str(PT_INDEX[month]).zfill(2)
                    break
            if temp_label is not None:
                label = temp_label
            else:
                # Fallback: usa a posição da coluna na lista (1-indexed)
                label = str(idx + 1).zfill(2)
        out.append({"mes": label, "valor": float(total)})
    return out


def get_top_materials(df: pd.DataFrame, gerencia: str, n: int = 10) -> List[Tuple[str, float]]:
    """Retorna os materiais com maiores valores totais em uma gerência.

    Os valores são calculados somando todas as colunas de valor mensal para
    cada material. Se a coluna de material não existir ou o DataFrame da
    gerência estiver vazio, retorna lista vazia.

    Args:
        df: DataFrame de origem.
        gerencia: Gerência para a qual extrair os materiais.
        n: Número máximo de materiais a retornar.

    Returns:
        Lista de tuplas ``(material, valor_total)`` ordenada de forma
        decrescente pelo valor.
    """
    gdf = _filter(df, gerencia)
    col_m = get_col_material(gdf)
    if gdf.empty or not col_m:
        return []

    month_cols = get_month_value_columns(gdf)
    totals: Dict[str, float] = {}

    # Itera sobre materiais únicos, convertendo para string para uniformizar
    for mat in gdf[col_m].dropna().map(str).unique():
        mat_df = gdf[gdf[col_m].astype(str) == mat]
        v = 0.0
        for c in month_cols:
            v += pd.to_numeric(mat_df[c], errors="coerce").fillna(0).sum()
        totals[mat] = float(v)

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[: max(1, n)]
    return [(k, float(v)) for k, v in top]


def get_gerencia_data_table(df: pd.DataFrame, gerencia: str) -> List[Dict[str, Any]]:
    """Retorna uma tabela detalhada para uma gerência.

    A tabela inclui as colunas de material, área, quantidade consolidada (se
    existir), as colunas de quantidades mensais e de valores mensais. Todos
    os valores numéricos são convertidos para tipos numéricos (int/float),
    enquanto colunas categóricas permanecem como string.

    Args:
        df: DataFrame de origem.
        gerencia: Gerência a ser detalhada.

    Returns:
        Lista de dicionários representando cada linha da tabela.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return []

    # Identifica colunas principais
    col_m = get_col_material(gdf)
    col_a = get_col_area(gdf)
    col_q = get_col_quantidade(gdf)
    value_cols = get_month_value_columns(gdf)
    quantity_month_cols = get_month_quantity_columns(gdf)

    base_cols: List[str] = []
    for c in [col_m, col_a, col_q]:
        if c and c in gdf.columns:
            base_cols.append(c)
    # Inclui colunas de quantidade mensais (se existirem) e de valores mensais
    cols = base_cols + quantity_month_cols + value_cols

    # Seleciona e converte tipos
    table = gdf[cols].copy()
    for c in cols:
        # Apenas converte para numérico colunas que não são categóricas
        if c not in (col_m, col_a) and c in table.columns:
            try:
                table[c] = pd.to_numeric(table[c], errors="coerce").fillna(0)
            except Exception:
                # Quando pd.to_numeric não aceita o array diretamente (por exemplo,
                # DataFrame em vez de Series), converte cada elemento individualmente.
                table[c] = table[c].apply(lambda x: pd.to_numeric(x, errors="coerce")).fillna(0)

    return table.to_dict("records")


# ---------------------------------------------------------------------
# Estatísticas genéricas para todas as colunas numéricas
# ---------------------------------------------------------------------
def get_numeric_column_stats(df: pd.DataFrame, gerencia: str) -> Dict[str, Dict[str, float]]:
    """Calcula estatísticas básicas para cada coluna numérica de uma gerência.

    Identifica dinamicamente colunas com valores numéricos (incluindo
    quantidades e valores mensais, bem como outras colunas numéricas que
    possam existir). Para cada coluna encontrada, calcula o total (soma)
    e a média.

    Args:
        df: DataFrame de origem.
        gerencia: Gerência a ser filtrada.

    Returns:
        Um dicionário mapeando o nome de cada coluna numérica para outro
        dicionário com as chaves ``total`` e ``media``.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return {}

    numeric_stats: Dict[str, Dict[str, float]] = {}
    for col in gdf.columns:
        try:
            # Exclui colunas claramente categóricas (material, área, gerência)
            # e tenta converter para numérico para identificar se há valores.
            if col == get_col_material(gdf) or col == get_col_area(gdf) or col == get_col_gerencia(gdf):
                continue
            series = pd.to_numeric(gdf[col], errors="coerce")
            # Considere coluna numérica se houver pelo menos um valor numérico
            if series.notna().any():
                total = float(series.fillna(0).sum())
                media = float(series.fillna(0).mean())
                numeric_stats[str(col)] = {
                    "total": total,
                    "media": media,
                }
        except Exception:
            # Se a conversão falhar, ignora a coluna
            continue
    return numeric_stats


# ---------------------------------------------------------------------
# Análise completa por gerência e para todas as gerências
# ---------------------------------------------------------------------
def comprehensive_gerencia_analysis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Pacote completo por gerência (KPIs, evolução, top materiais, tabela, IA).
    """
    kpis = calculate_gerencia_kpis(df, gerencia)
    evolucao = get_monthly_evolution(df, gerencia)
    top = get_top_materials(df, gerencia, 10)
    tabela = get_gerencia_data_table(df, gerencia)
    ai = comprehensive_ai_analysis(df, gerencia)

    # Estatísticas adicionais para todas as colunas numéricas
    numeric_stats = get_numeric_column_stats(df, gerencia)

    return {
        "gerencia": gerencia,
        "timestamp": datetime.now().isoformat(),
        "kpis": kpis,
        "evolucao_mensal": evolucao,
        "top_materiais": top,          # List[Tuple[str, float]] — compatível com charts.py
        "tabela_dados": tabela,
        "analises_ia": ai,
        "metricas_colunas": numeric_stats,
        "status": "sucesso" if kpis.get("status") == "sucesso" else "erro",
    }


def generate_all_gerencias_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Retorna o pacote de análises para TODAS as gerências, no formato
    esperado pela app e pelo gerador de PDF.
    """
    gerencias = get_unique_gerencias(df)
    if not gerencias:
        return {
            "status": "erro",
            "mensagem": "Nenhuma gerência encontrada nos dados",
            "gerencias": [],
            "analises": {},
        }

    analises = {g: comprehensive_gerencia_analysis(df, g) for g in gerencias}

    return {
        "status": "sucesso",
        "total_gerencias": len(gerencias),
        "gerencias": gerencias,
        "analises": analises,
        "timestamp": datetime.now().isoformat(),
    }