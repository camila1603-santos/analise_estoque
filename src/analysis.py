"""
Análise unificada de estoque excedente por gerência:
- KPIs por gerência
- Evolução mensal (ordenada)
- Top materiais
- Tabela detalhada
- Integração com IA clássica (ai.classic_ai)
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np  # (pode ser útil em futuras expansões; ok manter)
import pandas as pd

# IA clássica (mantenha esse caminho conforme sua estrutura)
from ai.classic_ai import comprehensive_ai_analysis

# Regex para capturar o número do mês em nomes como "Valor Mês 01", "valor mes 2", etc.
MONTH_RX = re.compile(r"(?:valor\s*m[eê]s|m[eê]s)\s*(\d{1,2})", re.IGNORECASE)


# ---------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------
def _month_columns_sorted(df: pd.DataFrame) -> List[str]:
    """
    Encontra e ordena colunas mensais pelo número do mês.
    Fallback: qualquer coluna contendo 'mês'/'mes' caso regex não encontre números.
    """
    found: List[Tuple[int, str]] = []
    for col in df.columns:
        m = MONTH_RX.search(str(col))
        if m:
            try:
                found.append((int(m.group(1)), col))
            except Exception:
                pass

    if found:
        return [col for _, col in sorted(found, key=lambda x: x[0])]

    # Fallback mais simples (mantém ordem original das colunas no DataFrame)
    return [c for c in df.columns if "mês" in str(c).lower() or "mes" in str(c).lower()]


def get_unique_gerencias(df: pd.DataFrame) -> List[str]:
    """
    Retorna a lista de gerências (exclui linhas agregadas do tipo 'Total ...').
    """
    if "Gerência" not in df.columns:
        return []
    vals = (
        df["Gerência"]
        .dropna()
        .map(str)
        .tolist()
    )
    vals = [g for g in set(vals) if not g.lower().startswith("total")]
    return sorted(vals)


def _filter(df: pd.DataFrame, gerencia: str) -> pd.DataFrame:
    """
    Filtra o DataFrame por gerência, removendo linhas 'Total ...'.
    """
    if "Gerência" not in df.columns:
        return pd.DataFrame()
    out = df[df["Gerência"].astype(str) == str(gerencia)].copy()
    out = out[~out["Gerência"].astype(str).str.lower().str.startswith("total")]
    return out


# ---------------------------------------------------------------------
# Cálculos por gerência
# ---------------------------------------------------------------------
def calculate_gerencia_kpis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    KPIs principais para a gerência:
      - valor_total (último mês)
      - quantidade_total
      - numero_materiais
      - valor_medio_material
      - variacao_mensal (% entre 1º e último mês)
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

    month_cols = _month_columns_sorted(gdf)

    # Valor total = soma no último mês disponível
    valor_total = 0.0
    if month_cols:
        last_col = month_cols[-1]
        valor_total = pd.to_numeric(gdf[last_col], errors="coerce").fillna(0).sum()

    # Quantidade total
    quantidade_total = pd.to_numeric(gdf.get("Quantidade", 0), errors="coerce").fillna(0).sum()

    # Nº materiais e valor médio
    numero_materiais = gdf["Material"].nunique() if "Material" in gdf.columns else 0
    valor_medio_material = float(valor_total) / max(1, int(numero_materiais))

    # Variação mensal: primeiro vs último mês
    variacao_mensal = 0.0
    if len(month_cols) >= 2:
        primeiro = pd.to_numeric(gdf[month_cols[0]], errors="coerce").fillna(0).sum()
        ultimo = pd.to_numeric(gdf[month_cols[-1]], errors="coerce").fillna(0).sum()
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
    """
    Lista de pontos (mês, valor) somados na gerência:
      [{"mes": "01", "valor": 12345.0}, ...]
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return []

    out: List[Dict[str, Any]] = []
    for col in _month_columns_sorted(gdf):
        total = pd.to_numeric(gdf[col], errors="coerce").fillna(0).sum()
        m = MONTH_RX.search(col)
        label = m.group(1).zfill(2) if m else str(col)
        out.append({"mes": label, "valor": float(total)})
    return out


def get_top_materials(df: pd.DataFrame, gerencia: str, n: int = 10) -> List[Tuple[str, float]]:
    """
    Top N materiais por valor somado ao longo das colunas mensais (ordenado desc).
    Retorna lista de tuplas (material, valor_total) — compatível com charts.py.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty or "Material" not in gdf.columns:
        return []

    month_cols = _month_columns_sorted(gdf)
    totals: Dict[str, float] = {}

    for mat in gdf["Material"].dropna().map(str).unique():
        mat_df = gdf[gdf["Material"].astype(str) == mat]
        v = 0.0
        for c in month_cols:
            v += pd.to_numeric(mat_df[c], errors="coerce").fillna(0).sum()
        totals[mat] = float(v)

    top = sorted(totals.items(), key=lambda x: x[1], reverse=True)[: max(1, n)]
    return [(k, float(v)) for k, v in top]


def get_gerencia_data_table(df: pd.DataFrame, gerencia: str) -> List[Dict[str, Any]]:
    """
    Tabela detalhada para a gerência (Material, Área, Quantidade, meses...).
    Valores numéricos convertidos para float/int.
    """
    gdf = _filter(df, gerencia)
    if gdf.empty:
        return []

    base_cols = [c for c in ["Material", "Área", "Quantidade"] if c in gdf.columns]
    month_cols = _month_columns_sorted(gdf)
    cols = base_cols + month_cols

    table = gdf[cols].copy()
    for c in cols:
        if c not in ("Material", "Área"):
            table[c] = pd.to_numeric(table[c], errors="coerce").fillna(0)

    return table.to_dict("records")


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

    return {
        "gerencia": gerencia,
        "timestamp": datetime.now().isoformat(),
        "kpis": kpis,
        "evolucao_mensal": evolucao,
        "top_materiais": top,          # List[Tuple[str, float]] — compatível com charts.py
        "tabela_dados": tabela,
        "analises_ia": ai,
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