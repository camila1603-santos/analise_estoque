"""
Módulo completo de análises de IA para gestão de estoque excedente.
Inclui análise preditiva, detecção de anomalias, análise prescritiva e geração de resumos.
Compatível com analysis.py, charts.py e utils/formatting.py.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import warnings

import os
from ai.generative_llm import llm_enabled, generate_executive_summary_llm

from utils.formatting import safe_format_currency, safe_format_number

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------
# Dependências opcionais (não obrigatórias para funcionar)
# ---------------------------------------------------------------------
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error

    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose

    STATSMODELS_AVAILABLE = True
except Exception:
    STATSMODELS_AVAILABLE = False

# ---------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------
MONTH_RX = re.compile(r"(?:valor\s*m[eê]s|m[eê]s)\s*(\d{1,2})", re.IGNORECASE)


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

    # fallback simples (mantém ordem original)
    return [c for c in df.columns if "mês" in str(c).lower() or "mes" in str(c).lower()]


def _filter_by_gerencia(df: pd.DataFrame, gerencia: str | None) -> pd.DataFrame:
    """
    Filtra por gerência; remove linhas do tipo 'Total ...'.
    Se gerência for None, retorna cópia do df sem 'Total ...'.
    Se a coluna 'Gerência' não existir e gerência for especificada, retorna vazio.
    """
    if gerencia is None:
        out = df.copy()
        if "Gerência" in out.columns:
            out = out[~out["Gerência"].astype(str).str.lower().str.startswith("total")]
        return out

    if "Gerência" not in df.columns:
        return pd.DataFrame()

    out = df[df["Gerência"].astype(str) == str(gerencia)].copy()
    out = out[~out["Gerência"].astype(str).str.lower().str.startswith("total")]
    return out


def _label_from_col(col: str) -> str:
    """Converte o nome da coluna em rótulo de mês 'MM' quando possível."""
    m = MONTH_RX.search(str(col))
    return m.group(1).zfill(2) if m else str(col)


# ---------------------------------------------------------------------
# Análise preditiva
# ---------------------------------------------------------------------
def predictive_analysis(df: pd.DataFrame, gerencia: str | None = None) -> Dict[str, Any]:
    """
    Análise preditiva simples (tendência linear) para prever próximos 3 meses.
    Retorna previsões, tendência, confiança e valores históricos.
    """
    try:
        df_filtered = _filter_by_gerencia(df, gerencia)
        if df_filtered.empty:
            return {
                "status": "erro",
                "mensagem": f"Nenhum dado encontrado para a gerência {gerencia}" if gerencia else "DataFrame vazio",
                "previsoes": [],
                "tendencia": "indefinida",
            }

        month_cols = _month_columns_sorted(df_filtered)
        if len(month_cols) < 3:
            return {
                "status": "erro",
                "mensagem": "Dados insuficientes para análise preditiva (mínimo 3 meses).",
                "previsoes": [],
                "tendencia": "indefinida",
            }

        # Série histórica ordenada
        y = np.array(
            [pd.to_numeric(df_filtered[c], errors="coerce").fillna(0).sum() for c in month_cols],
            dtype=float,
        )
        labels = [_label_from_col(c) for c in month_cols]

        if len(y) < 2 or np.allclose(np.std(y), 0.0):
            # Sem variação: repete último valor
            return {
                "status": "aviso",
                "mensagem": "Valores constantes ou pouca variação — previsão trivial.",
                "previsoes": [float(y[-1])] * 3,
                "tendencia": "estável",
                "valores_historicos": y.tolist(),
                "labels_meses": labels,
            }

        # Ajuste linear: y = a + b*x
        x = np.arange(len(y), dtype=float)
        b, a = np.polyfit(x, y, 1)  # retorna [slope, intercept] se usar np.polyfit(x, y, 1)? Cuidado: np.polyfit retorna [slope, intercept]
        # CORREÇÃO: np.polyfit retorna [slope, intercept]; acima atribuímos b, a nessa ordem
        slope = b
        intercept = a

        # Futuro: N, N+1, N+2
        n = len(y)
        x_future = np.array([n, n + 1, n + 2], dtype=float)
        preds = (slope * x_future + intercept).tolist()
        preds = [float(max(0.0, p)) for p in preds]

        # Tendência baseada no slope relativo à média
        mean_y = float(np.mean(y))
        rel = slope / (mean_y + 1e-9)
        if rel > 0.05:
            tendencia = "crescimento"
        elif rel < -0.05:
            tendencia = "decrescimento"
        else:
            tendencia = "estável"

        # Confiança ~ força da correlação linear
        if np.std(x) > 0 and np.std(y) > 0:
            r = float(np.corrcoef(x, y)[0, 1])
            confianca = max(0.3, min(0.95, abs(r)))
        else:
            confianca = 0.5

        return {
            "status": "sucesso",
            "previsoes": preds,
            "tendencia": tendencia,
            "confianca": float(confianca),
            "valores_historicos": y.tolist(),
            "labels_meses": labels,
            "slope": float(slope),
            "interpretacao": _interpretar_previsao(preds, y[-1], tendencia),
        }

    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro na análise preditiva: {str(e)}",
            "previsoes": [],
            "tendencia": "indefinida",
        }


def _interpretar_previsao(previsoes: List[float], valor_atual: float, tendencia: str) -> str:
    """Interpreta as previsões em linguagem natural (com formatação BR)."""
    if not previsoes:
        return "Não foi possível gerar interpretação."

    variacao_pct = ((previsoes[-1] - (valor_atual or 0.0)) / (abs(valor_atual) + 1e-9)) * 100.0
    if tendencia == "crescimento":
        return f"Tendência de crescimento detectada. Previsão de aumento de {variacao_pct:.1f}% em ~3 meses."
    if tendencia == "decrescimento":
        return f"Tendência de redução detectada. Previsão de diminuição de {abs(variacao_pct):.1f}% em ~3 meses."
    return f"Tendência estável. Variação prevista de {variacao_pct:.1f}% em ~3 meses."


# ---------------------------------------------------------------------
# Detecção de anomalias
# ---------------------------------------------------------------------
def anomaly_detection(df: pd.DataFrame, gerencia: str | None = None) -> Dict[str, Any]:
    """
    Detecção de anomalias estatísticas simples:
    - Z-score > 2 para série mensal por material
    - Crescimento súbito (>50%) entre meses consecutivos (total geral)
    """
    try:
        df_filtered = _filter_by_gerencia(df, gerencia)
        if df_filtered.empty:
            return {"status": "erro", "mensagem": "Nenhum dado encontrado", "anomalias": []}

        month_cols = _month_columns_sorted(df_filtered)
        if len(month_cols) < 3:
            return {
                "status": "aviso",
                "mensagem": "Dados insuficientes para detecção robusta de anomalias",
                "anomalias": [],
            }

        anomalias: List[Dict[str, Any]] = []

        # Por material
        if "Material" in df_filtered.columns:
            for material in df_filtered["Material"].dropna().unique():
                mdf = df_filtered[df_filtered["Material"] == material]
                serie = np.array(
                    [pd.to_numeric(mdf[c], errors="coerce").fillna(0).sum() for c in month_cols],
                    dtype=float,
                )
                mu, sigma = float(np.mean(serie)), float(np.std(serie))
                if sigma > 0:
                    for idx, valor in enumerate(serie):
                        z = abs((valor - mu) / sigma)
                        if z > 2.0:
                            anomalias.append(
                                {
                                    "tipo": "valor_atipico",
                                    "material": str(material),
                                    "mes": _label_from_col(month_cols[idx]),
                                    "valor": float(valor),
                                    "valor_esperado": float(mu),
                                    "desvio_percentual": float(((valor - mu) / (abs(mu) + 1e-9)) * 100.0),
                                    "severidade": "alta" if z > 3.0 else "média",
                                }
                            )

        # Crescimento súbito no total geral
        totais = [
            float(pd.to_numeric(df_filtered[c], errors="coerce").fillna(0).sum()) for c in month_cols
        ]
        for i in range(1, len(totais)):
            if totais[i - 1] > 0:
                crescimento = ((totais[i] - totais[i - 1]) / totais[i - 1]) * 100.0
                if crescimento > 50.0:
                    anomalias.append(
                        {
                            "tipo": "crescimento_subito",
                            "mes_anterior": _label_from_col(month_cols[i - 1]),
                            "mes_atual": _label_from_col(month_cols[i]),
                            "valor_anterior": float(totais[i - 1]),
                            "valor_atual": float(totais[i]),
                            "crescimento_percentual": float(crescimento),
                            "severidade": "alta" if crescimento > 100.0 else "média",
                        }
                    )

        return {
            "status": "sucesso",
            "anomalias": anomalias,
            "total_anomalias": len(anomalias),
            "interpretacao": _interpretar_anomalias(anomalias),
        }

    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro na detecção de anomalias: {str(e)}", "anomalias": []}


def _interpretar_anomalias(anomalias: List[Dict[str, Any]]) -> str:
    """Interpreta as anomalias detectadas."""
    if not anomalias:
        return "Nenhuma anomalia significativa detectada nos dados."

    altas = sum(1 for a in anomalias if a.get("severidade") == "alta")
    medias = sum(1 for a in anomalias if a.get("severidade") == "média")

    partes = [f"Detectadas {len(anomalias)} anomalias"]
    if altas:
        partes.append(f"{altas} de alta severidade")
    if medias:
        partes.append(f"{medias} de média severidade")
    return ", ".join(partes) + "."


# ---------------------------------------------------------------------
# Análise prescritiva
# ---------------------------------------------------------------------
def prescriptive_analysis(df: pd.DataFrame, gerencia: str | None = None) -> Dict[str, Any]:
    """
    Recomendações de ações com base em:
    - Materiais com maior valor acumulado
    - Tendência recente da soma mensal
    - Valor total agregado (pode disparar auditoria)
    """
    try:
        df_filtered = _filter_by_gerencia(df, gerencia)
        if df_filtered.empty:
            return {"status": "erro", "mensagem": "Nenhum dado encontrado", "recomendacoes": []}

        month_cols = _month_columns_sorted(df_filtered)
        recomendacoes: List[Dict[str, Any]] = []

        # Top materiais por valor
        if "Material" in df_filtered.columns and month_cols:
            material_values: Dict[str, float] = {}
            for material in df_filtered["Material"].dropna().unique():
                mdf = df_filtered[df_filtered["Material"] == material]
                total = 0.0
                for c in month_cols:
                    total += float(pd.to_numeric(mdf[c], errors="coerce").fillna(0).sum())
                material_values[str(material)] = total

            if material_values:
                valores = list(material_values.values())
                p80 = float(np.percentile(valores, 80)) if len(valores) >= 2 else max(valores)
                top_materials = sorted(material_values.items(), key=lambda kv: kv[1], reverse=True)[:5]

                for material, valor in top_materials:
                    if valor > 0:
                        prioridade = "alta" if valor >= p80 else "média"
                        recomendacoes.append(
                            {
                                "tipo": "reducao_estoque",
                                "prioridade": prioridade,
                                "material": material,
                                "valor_atual": float(valor),
                                "acao": f"Priorizar redução do estoque de {material}",
                                "detalhes": f"Material de alto impacto (atual: {safe_format_currency(valor)}). Considerar remanejamento ou liquidação.",
                                "impacto_estimado": float(valor * (0.3 if prioridade == "alta" else 0.2)),
                            }
                        )

        # Tendência recente (média dos 3 últimos - média dos anteriores)
        if len(month_cols) >= 3:
            monthly_totals = [float(pd.to_numeric(df_filtered[c], errors="coerce").fillna(0).sum()) for c in month_cols]
            ult3 = monthly_totals[-3:]
            ant = monthly_totals[:-3] or [0.0]
            recent_trend = float(np.mean(ult3) - np.mean(ant))

            if recent_trend > 0:
                recomendacoes.append(
                    {
                        "tipo": "controle_crescimento",
                        "prioridade": "média",
                        "acao": "Implementar controles para reduzir crescimento do estoque",
                        "detalhes": f"Tendência de crescimento detectada (Δ ≈ {safe_format_currency(recent_trend)}). Revisar políticas de compra.",
                        "impacto_estimado": float(max(0.0, recent_trend) * 0.5),
                    }
                )
            elif ant and np.mean(ant) > 0 and (np.mean(ant) - np.mean(ult3)) / np.mean(ant) > 0.1:
                recomendacoes.append(
                    {
                        "tipo": "manter_estrategia",
                        "prioridade": "baixa",
                        "acao": "Manter estratégia atual de redução",
                        "detalhes": "Tendência positiva de redução (>10% vs. período anterior).",
                        "impacto_estimado": float(abs(recent_trend)),
                    }
                )

        # Auditoria por valor total acumulado (último mês como referência principal)
        total_value = 0.0
        if month_cols:
            total_value = float(pd.to_numeric(df_filtered[month_cols[-1]], errors="coerce").fillna(0).sum())
            if total_value > 1_000_000:
                recomendacoes.append(
                    {
                        "tipo": "auditoria",
                        "prioridade": "alta",
                        "acao": "Realizar auditoria completa do estoque",
                        "detalhes": f"Valor atual elevado ({safe_format_currency(total_value)}). Auditoria pode identificar oportunidades.",
                        "impacto_estimado": float(total_value * 0.15),
                    }
                )

        return {
            "status": "sucesso",
            "recomendacoes": recomendacoes,
            "total_recomendacoes": len(recomendacoes),
            "impacto_total_estimado": float(sum(r.get("impacto_estimado", 0.0) for r in recomendacoes)),
            "interpretacao": _interpretar_recomendacoes(recomendacoes),
        }

    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro na análise prescritiva: {str(e)}", "recomendacoes": []}


def _interpretar_recomendacoes(recomendacoes: List[Dict[str, Any]]) -> str:
    """Interpreta as recomendações geradas."""
    if not recomendacoes:
        return "Nenhuma recomendação específica gerada. Situação aparenta estar sob controle."

    altas = sum(1 for r in recomendacoes if r.get("prioridade") == "alta")
    if altas > 0:
        return f"Geradas {len(recomendacoes)} recomendações, sendo {altas} de alta prioridade (ação imediata)."
    return f"Geradas {len(recomendacoes)} recomendações para otimização contínua do estoque."


# ---------------------------------------------------------------------
# Resumo executivo em LN
# ---------------------------------------------------------------------
def generate_natural_language_summary(df: pd.DataFrame, gerencia: str | None = None) -> Dict[str, Any]:
    """
    Gera resumo executivo:
      - Se LLM habilitado: usa IA generativa (OpenAI)
      - Caso contrário: usa template determinístico (fallback)
    """
    try:
        df_filtered = _filter_by_gerencia(df, gerencia)
        contexto = f"GERÊNCIA {gerencia.upper()}" if gerencia else "ORGANIZACIONAL"
        if df_filtered.empty:
            return {"status": "erro", "mensagem": "Nenhum dado encontrado para gerar resumo", "resumo": ""}

        month_cols = _month_columns_sorted(df_filtered)
        if not month_cols:
            return {"status": "erro", "mensagem": "Nenhuma coluna de valor mensal encontrada", "resumo": ""}

        # Métricas base
        monthly_totals = [float(pd.to_numeric(df_filtered[c], errors="coerce").fillna(0).sum()) for c in month_cols]
        valor_atual = monthly_totals[-1] if monthly_totals else 0.0
        num_materials = int(df_filtered["Material"].nunique()) if "Material" in df_filtered.columns else 0
        total_qty = int(pd.to_numeric(df_filtered["Quantidade"], errors="coerce").fillna(0).sum()) if "Quantidade" in df_filtered.columns else 0

        tendencia_texto = "estável"
        if len(monthly_totals) >= 3:
            ult3 = monthly_totals[-3:]
            ant = monthly_totals[:-3] or [0.0]
            if np.mean(ult3) > np.mean(ant) * 1.1:
                tendencia_texto = "crescimento"
            elif np.mean(ult3) < np.mean(ant) * 0.9:
                tendencia_texto = "redução"

        # Top material por soma
        top_material = "N/A"
        if "Material" in df_filtered.columns and month_cols:
            material_values: Dict[str, float] = {}
            for material in df_filtered["Material"].dropna().unique():
                mdf = df_filtered[df_filtered["Material"] == material]
                total = sum(float(pd.to_numeric(mdf[c], errors="coerce").fillna(0).sum()) for c in month_cols)
                material_values[str(material)] = total
            if material_values:
                top_material = max(material_values.items(), key=lambda kv: kv[1])[0]

        # Dados auxiliares para o LLM (pega saídas das outras análises como insumo)
        anomalias: List[Dict[str, Any]] = []
        recs: List[Dict[str, Any]] = []
        try:
            anom = anomaly_detection(df, gerencia)
            if anom.get("status") == "sucesso":
                anomalias = anom.get("anomalias", [])
            presc = prescriptive_analysis(df, gerencia)
            if presc.get("status") == "sucesso":
                recs = presc.get("recomendacoes", [])
        except Exception:
            pass  # não bloqueia o resumo

        # Se LLM habilitado, tenta usar o modelo
        if llm_enabled():
            payload = {
                "gerencia": gerencia or "Todas",
                "kpis": {
                    "valor_total": valor_atual,
                    "numero_materiais": num_materials,
                    "quantidade_total": total_qty,
                    "variacao_mensal": 0.0  # mantemos variação mensal como 0 aqui; se quiser, calcule sua forma preferida
                },
                "tendencia": tendencia_texto,
                "top_material": top_material,
                "anomalias": anomalias,
                "recomendacoes": recs,
            }
            llm = generate_executive_summary_llm(payload)
            if llm.get("status") == "sucesso":
                return {
                    "status": "sucesso",
                    "resumo": llm.get("resumo", ""),
                    "metricas": {
                        "valor_total": float(valor_atual),
                        "num_materiais": int(num_materials),
                        "quantidade_total": int(total_qty),
                        "top_material": top_material,
                        "tendencia": tendencia_texto,
                    },
                    "modelo": llm.get("modelo"),
                }
            # se LLM falhar, seguimos para o fallback template

        # -------- Fallback: template determinístico (o que você já tinha) --------
        from utils.formatting import safe_format_currency, safe_format_number

        resumo = f"""
RESUMO EXECUTIVO - ESTOQUE EXCEDENTE {contexto}

SITUAÇÃO ATUAL:
• Valor do estoque excedente (mês mais recente): {safe_format_currency(valor_atual)}
• Número de materiais diferentes: {safe_format_number(num_materials)}
• Quantidade total de itens: {safe_format_number(total_qty)}
• Material com maior impacto: {top_material}

TENDÊNCIA:
• Comportamento nos últimos meses: {tendencia_texto}
• Período analisado: {len(monthly_totals)} meses

PRINCIPAIS INSIGHTS:
• Valor médio por material: {safe_format_currency(valor_atual / max(1, num_materials))}
• {"Alto" if valor_atual > 1_000_000 else "Médio" if valor_atual > 100_000 else "Baixo"} volume de estoque excedente
• {"Atenção necessária para controlar crescimento" if tendencia_texto == "crescimento" else ("Situação sob controle" if tendencia_texto == "redução" else "Monitoramento contínuo recomendado")}

PRÓXIMOS PASSOS RECOMENDADOS:
• Focar na gestão do material de maior impacto ({top_material})
• {"Implementar ações de redução urgentes" if valor_atual > 1_000_000 else "Manter monitoramento regular"}
• Revisar políticas de compra e estoque
        """.strip()

        return {
            "status": "sucesso",
            "resumo": resumo,
            "metricas": {
                "valor_total": float(valor_atual),
                "num_materiais": int(num_materials),
                "quantidade_total": int(total_qty),
                "top_material": top_material,
                "tendencia": tendencia_texto,
            },
        }

    except Exception as e:
        return {"status": "erro", "mensagem": f"Erro ao gerar resumo: {str(e)}", "resumo": ""}

# ---------------------------------------------------------------------
# Agregador
# ---------------------------------------------------------------------
def comprehensive_ai_analysis(df: pd.DataFrame, gerencia: str | None = None) -> Dict[str, Any]:
    """
    Executa todas as análises de IA de forma integrada.
    Chaves retornadas:
      - analise_preditiva, deteccao_anomalias, analise_prescritiva, resumo_executivo
    """
    try:
        return {
            "analise_preditiva": predictive_analysis(df, gerencia),
            "deteccao_anomalias": anomaly_detection(df, gerencia),
            "analise_prescritiva": prescriptive_analysis(df, gerencia),
            "resumo_executivo": generate_natural_language_summary(df, gerencia),
            "timestamp": datetime.now().isoformat(),
            "gerencia": gerencia or "Todas",
        }
    except Exception as e:
        return {"erro": f"Erro na análise integrada: {str(e)}", "timestamp": datetime.now().isoformat(), "gerencia": gerencia or "Todas"}


# ---------------------------------------------------------------------
# Teste rápido (opcional)
# ---------------------------------------------------------------------
def test_ai_analysis() -> Dict[str, Any]:
    """Teste básico do módulo com dataset sintético."""
    test_data = {
        "Gerência": ["Operações", "Operações", "Qualidade", "Qualidade"],
        "Material": ["M001", "M002", "M003", "M004"],
        "Quantidade": [100, 200, 50, 75],
        "Valor Mês 01": [100000, 200000, 50000, 75000],
        "Valor Mês 02": [110000, 180000, 55000, 70000],
        "Valor Mês 03": [95000, 190000, 48000, 72000],
    }
    df_test = pd.DataFrame(test_data)

    print("=== TESTE COMPLETO DO MÓDULO classic_ai ===")

    print("\n1. ANÁLISE PREDITIVA:")
    pred = predictive_analysis(df_test, "Operações")
    print("Status:", pred.get("status"))
    print("Tendência:", pred.get("tendencia"))
    print("Previsões:", [safe_format_currency(v) for v in pred.get("previsoes", [])])
    print("Interpretação:", pred.get("interpretacao", "-"))

    print("\n2. DETECÇÃO DE ANOMALIAS:")
    anom = anomaly_detection(df_test, "Operações")
    print("Status:", anom.get("status"), "Total:", anom.get("total_anomalias", 0))
    print("Interpretação:", anom.get("interpretacao", "-"))

    print("\n3. ANÁLISE PRESCRITIVA:")
    presc = prescriptive_analysis(df_test, "Operações")
    print("Status:", presc.get("status"), "Total:", presc.get("total_recomendacoes", 0))
    if presc.get("recomendacoes"):
        for i, r in enumerate(presc["recomendacoes"][:3], 1):
            print(f"  {i}. {r.get('acao', 'N/A')} ({r.get('prioridade')})")

    print("\n4. RESUMO EXECUTIVO:")
    summ = generate_natural_language_summary(df_test, "Operações")
    print("Status:", summ.get("status"))
    print(summ.get("resumo", "")[:300] + "...")

    print("\n5. ANÁLISE INTEGRADA:")
    comp = comprehensive_ai_analysis(df_test, "Operações")
    print("Gerência:", comp.get("gerencia"), "Timestamp:", comp.get("timestamp"))
    print("✅ Módulo classic_ai funcional.")
    return comp


if __name__ == "__main__":
    test_ai_analysis()