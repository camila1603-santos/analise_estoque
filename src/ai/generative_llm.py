# src/ai/generative_llm.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional, List

# Cliente oficial OpenAI (pip install openai)
# Doc Chat Completions: https://platform.openai.com/docs/api-reference/chat
from openai import OpenAI

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# temperature baixa p/ resumo executivo mais estável
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))


def llm_enabled() -> bool:
    """
    Habilita LLM se:
      - OPENAI_API_KEY estiver definido
      - USE_LLM em (1,true,yes,on)
    """
    key = os.getenv("OPENAI_API_KEY")
    flag = os.getenv("USE_LLM", "0").strip().lower() in ("1", "true", "yes", "on")
    return bool(key) and flag


def _fmt_currency_br(x: float) -> str:
    try:
        return ("R$ {:,.2f}".format(float(x))).replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _build_summary_prompt(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Monta o prompt para o LLM a partir de métricas consolidadas.
    Espera chaves:
      payload = {
        "gerencia": str,
        "kpis": {"valor_total","numero_materiais","quantidade_total","variacao_mensal"},
        "tendencia": str,
        "top_material": str,
        "anomalias": List[Dict],
        "recomendacoes": List[Dict]
      }
    """
    gerencia = payload.get("gerencia", "N/A")
    kpis = payload.get("kpis", {}) or {}
    tendencia = payload.get("tendencia", "estável")
    top_material = payload.get("top_material", "N/A")

    # Resumo curto das anomalias e recomendações
    anom = payload.get("anomalias") or []
    recs = payload.get("recomendacoes") or []
    anom_txt = "; ".join(
        f"- {a.get('tipo','anomalia')} ({a.get('severidade','n/a')}) em {a.get('mes','?')}"
        for a in anom[:6]
    ) or "nenhuma relevante"
    recs_txt = "; ".join(
        f"- {r.get('acao','(ação)')} [{r.get('prioridade','média')}]"
        for r in recs[:6]
    ) or "recomendações operacionais padrão"

    system = (
        "Você é um analista sênior de Supply Chain. Escreva em PT-BR, tom executivo, "
        "parágrafos curtos e bullets quando ajudarem. Seja específico, cite números e percentuais."
    )
    user = f"""
Contexto do negócio — GERÊNCIA: {gerencia}

KPIs:
• Valor total (mês atual ou mais recente): {_fmt_currency_br(kpis.get('valor_total', 0))}
• Materiais: {kpis.get('numero_materiais', 0)}
• Quantidade total: {int(kpis.get('quantidade_total', 0))}
• Variação mensal: {kpis.get('variacao_mensal', 0):+.1f}%
• Tendência recente: {tendencia}
• Material de maior impacto: {top_material}

Anomalias (resumo):
{anom_txt}

Recomendações (resumo):
{recs_txt}

Tarefa:
1) Produza um RESUMO EXECUTIVO objetivo (5–8 linhas).
2) Liste 3–5 AÇÕES PRIORITÁRIAS (bullets), cada uma com racional curto e potencial impacto estimado.
3) Se houver crescimento indesejado, reforce medidas de controle; se houver redução, aponte como sustentar.
Respeite o dado: não invente números novos; use apenas os acima.
"""
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user.strip()},
    ]


def generate_executive_summary_llm(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gera texto executivo com LLM. Retorna {status, resumo, modelo, usage?}
    Se LLM estiver desabilitado/sem chave, retorna {"status":"skip"}.
    """
    if not llm_enabled():
        return {"status": "skip", "mensagem": "LLM desabilitado ou sem OPENAI_API_KEY."}

    client = OpenAI()  # usa OPENAI_API_KEY do ambiente
    messages = _build_summary_prompt(payload)

    # === Opção A: Chat Completions (estável e simples) ===
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=700,
    )
    text = (resp.choices[0].message.content or "").strip()

    return {
        "status": "sucesso",
        "resumo": text,
        "modelo": DEFAULT_MODEL,
        "tokens": getattr(resp, "usage", None).model_dump() if hasattr(resp, "usage") else None,
    }

    # === Opção B: Responses API (alternativa moderna) ===
    # from openai import OpenAI
    # r = client.responses.create(
    #     model=DEFAULT_MODEL,
    #     input=messages,  # mesmo formato role/content é aceito
    #     temperature=DEFAULT_TEMPERATURE,
    #     max_output_tokens=700,
    # )
    # text = (r.output_text or "").strip()
    # return {"status": "sucesso", "resumo": text, "modelo": DEFAULT_MODEL}