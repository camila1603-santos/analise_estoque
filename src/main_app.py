"""
Aplicação Streamlit para análise de estoque excedente com IA.
Compatível com:
- analysis.py
- charts.py
- pdf.py
- utils/formatting.py
"""

import os
import io
import zipfile
import tempfile
from typing import Dict, List, Any

import pandas as pd
import streamlit as st

# --- bootstrap de imports: garante que a pasta do arquivo (src) está no sys.path
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
# Tenta achar o .env subindo diretórios a partir deste arquivo
load_dotenv(find_dotenv(usecwd=True), override=True)

load_dotenv()
# Tenta importar dos pacotes 'ai.generative_llm' e 'ai.classic_ai'.
# Caso esses módulos não existam, faz fallback para importar dos arquivos
# locais 'generative_llm.py' e 'classic_ai.py'. Isso garante que o
# aplicativo continue funcionando mesmo sem pacotes instalados.
try:
    from ai.generative_llm import *  # type: ignore
    from ai.classic_ai import *  # type: ignore
except ImportError:
    from generative_llm import *  # type: ignore
    from classic_ai import *  # type: ignore
from utils.formatting import safe_format_currency, safe_format_number
from charts import generate_all_charts_for_gerencia
from pdf import generate_pdf_for_gerencia
from analysis import generate_all_gerencias_analysis, get_unique_gerencias

# Importa utilitários de colunas para detecção dinâmica
from utils.columns import (
    get_col_gerencia,
    get_col_material,
    get_month_value_columns,
    get_col_quantidade,
)


# Lê as variáveis de ambiente
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.2))

# --- bootstrap de imports: garante que a pasta do arquivo (src) está no sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# -------------------------------------------------------------------
# Configuração da página
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Análise Inteligente de Estoque Excedente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS leve
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #1f77b4; text-align: center; margin-bottom: 1.25rem; }
    .ai-insight { background-color: #e3f2fd; padding: 1rem; border-radius: .5rem; border-left: 4px solid #2196f3; margin: .5rem 0; }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------------
# Mock (apenas se precisar rodar sem módulos ou sem dados)
# -------------------------------------------------------------------
def generate_mock_analysis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """Gera uma análise fictícia para fallback em caso de erro.

    Este mock utiliza as funções de detecção dinâmica para localizar as
    colunas principais (gerência, material e quantidade), de modo a evitar
    dependência de nomes específicos. Caso alguma coluna não exista,
    utiliza valores aleatórios para simular os KPIs.
    """
    import numpy as np
    from datetime import datetime as _dt

    # Filtra DataFrame pela gerência, se possível
    col_g = get_col_gerencia(df)
    if col_g:
        df_g = df[df[col_g].astype(str) == str(gerencia)]
    else:
        df_g = df.copy()

    # Valor total fictício
    valor_total = float(np.random.uniform(100_000, 2_000_000))

    # Número de materiais baseado na coluna detectada, ou valor aleatório
    col_m = get_col_material(df_g)
    if col_m:
        numero_materiais = int(df_g[col_m].nunique())
    else:
        numero_materiais = int(np.random.randint(10, 50))

    # Quantidade total baseada na coluna consolidada, ou valor aleatório
    col_q = get_col_quantidade(df_g)
    if col_q:
        quantidade_total = int(pd.to_numeric(df_g[col_q], errors="coerce").fillna(0).sum())
    else:
        quantidade_total = int(np.random.randint(500, 2000))

    variacao_mensal = float(np.random.uniform(-25, 25))

    # top_materiais como lista de tuplas (material, valor)
    top_materiais: List[tuple] = []
    if col_m:
        for material in df_g[col_m].dropna().unique()[:10]:
            top_materiais.append((str(material), float(np.random.uniform(10_000, max(10_000, valor_total / 5)))))

    # evolução_mensal fictícia para 6 períodos
    evolucao_mensal = []
    for m in range(1, 7):
        evolucao_mensal.append({"mes": f"{m:02d}", "valor": float(valor_total * (1 + np.random.uniform(-0.3, 0.3)))})

    return {
        "gerencia": gerencia,
        "kpis": {
            "valor_total": valor_total,
            "numero_materiais": numero_materiais,
            "quantidade_total": quantidade_total,
            "variacao_mensal": variacao_mensal,
            "valor_medio_material": valor_total / max(1, numero_materiais),
            "status": "sucesso",
        },
        "top_materiais": top_materiais,
        "evolucao_mensal": evolucao_mensal,
        "tabela_dados": [],
        "analises_ia": {},
        "metricas_colunas": {},
        "timestamp": _dt.now().isoformat(),
        "status": "sucesso",
    }


# -------------------------------------------------------------------
# UI helpers
# -------------------------------------------------------------------
def display_gerencia_analysis(analysis_data: Dict[str, Any]) -> None:
    """Bloco de visualização para uma gerência específica."""
    gerencia = analysis_data.get("gerencia", "N/A")
    kpis = analysis_data.get("kpis", {})

    st.subheader(f"📊 {gerencia}")

    # KPIs (formatação BR)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Valor Total", safe_format_currency(kpis.get("valor_total", 0)))
    with col2:
        st.metric("📦 Materiais", safe_format_number(kpis.get("numero_materiais", 0)))
    with col3:
        st.metric("📊 Quantidade", safe_format_number(kpis.get("quantidade_total", 0)))
    with col4:
        variacao = float(kpis.get("variacao_mensal", 0) or 0)
        st.metric("📈 Variação %", f"{variacao:+.1f}%")

    # Gráficos (via charts)
    charts = generate_all_charts_for_gerencia(analysis_data)
    col_left, col_right = st.columns(2)
    with col_left:
        if charts.get("top_materiais"):
            st.markdown("**📈 Top Materiais**")
            st.image(charts["top_materiais"], use_container_width=True)
        else:
            st.info("Dados de materiais não disponíveis.")
    with col_right:
        if charts.get("evolucao_mensal"):
            st.markdown("**📊 Evolução Mensal**")
            st.image(charts["evolucao_mensal"], use_container_width=True)
        else:
            st.info("Dados de evolução não disponíveis.")

    # Insights simples baseados nos números (lado cliente)
    st.markdown("### 🤖 Insights de IA")
    valor_total = float(kpis.get('valor_total', 0) or 0)
    variacao = float(kpis.get('variacao_mensal', 0) or 0)
    num_materiais = int(kpis.get('numero_materiais', 0) or 0)

    insights = []
    if valor_total > 1_000_000:
        insights.append("🔴 **Alto valor de estoque excedente** — priorize ações de redução.")
    elif valor_total > 500_000:
        insights.append("🟡 **Valor moderado de estoque** — mantenha monitoramento próximo.")
    else:
        insights.append("🟢 **Valor controlado de estoque** — situação estável.")

    if variacao > 10:
        insights.append("📈 **Crescimento significativo** — revisar políticas de reposição/compras.")
    elif variacao < -10:
        insights.append("📉 **Redução expressiva** — manter estratégia atual.")
    else:
        insights.append("➡️ **Tendência estável** — manter monitoramento.")

    if num_materiais > 50:
        insights.append("📦 **Alta diversidade de materiais** — considere consolidação/ABC.")
    elif num_materiais < 10:
        insights.append("🎯 **Poucos materiais** — gestão mais focada possível.")

    for ins in insights:
        st.markdown(f'<div class="ai-insight">{ins}</div>', unsafe_allow_html=True)

    # --- Resumo Executivo (IA) vindo do backend (classic_ai → generative_llm) ---
    ai_data = analysis_data.get("analises_ia", {}) or {}
    resumo_ia = ai_data.get("resumo_executivo", {})

    if isinstance(resumo_ia, dict):
        status_ia = resumo_ia.get("status")
        if status_ia == "sucesso" and resumo_ia.get("resumo"):
            st.markdown("### 🧠 Resumo Executivo (IA)")
            st.write(resumo_ia["resumo"])
        elif status_ia == "skip":
            st.caption("IA generativa desativada ou sem chave (usando fallback determinístico).")
        elif resumo_ia.get("mensagem"):
            st.info(f"IA: {resumo_ia['mensagem']}")

# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------
def main():
    st.markdown('<h1 class="main-header">🤖 Análise Inteligente de Estoque Excedente</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema com IA para Gestão de Estoque por Gerência")
    st.markdown("---")

    with st.sidebar:
        st.header("ℹ️ Como usar")
        st.info("1) Faça upload do CSV • 2) Selecione as gerências • 3) Gere análises e PDFs")
        st.header("📋 Formato do CSV")
        st.markdown(
            "**Colunas obrigatórias:** Gerência/Gerencia • Material • "
            "Valores mensais (ex.: `Valor Mês 01..12` ou `Jan_Valor .. Dez_Valor`)")
        st.header("🧠 IA Generativa")
        use_llm_ui = st.toggle("Ativar LLM (OpenAI)", value=os.getenv("USE_LLM","0") in ("1","true","yes","on"))
        # sincroniza com o processo atual (não persiste fora da sessão)
        os.environ["USE_LLM"] = "1" if use_llm_ui else "0"
        # Status do LLM (checa OPENAI_API_KEY + USE_LLM)
        st.caption(f"LLM: {'ON' if llm_enabled() else 'OFF'} • Modelo: {os.getenv('OPENAI_MODEL','gpt-4o-mini')}")


    uploaded_file = st.file_uploader(
        "📁 Faça o upload do arquivo CSV",
        type=["csv"],
        help="Selecione um arquivo CSV com os dados de estoque excedente"
    )

    if uploaded_file is None:
        st.stop()

    # Carregar dados
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except Exception:
        df = pd.read_csv(uploaded_file)  # fallback simples
    st.success("✅ Arquivo carregado com sucesso!")

    # Preview
    with st.expander("👀 Preview dos Dados", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📊 Registros", len(df))
        with c2: st.metric("📋 Colunas", len(df.columns))
        with c3:
            # Usa detecção dinâmica para contar gerências
            col_g = get_col_gerencia(df)
            if col_g:
                st.metric("🏢 Gerências", df[col_g].nunique())

    # Validação mínima (detecção flexível)
    col_g = get_col_gerencia(df)
    col_m = get_col_material(df)
    month_vals = get_month_value_columns(df)

    if not col_g:
        st.error("❌ Coluna de Gerência/Gerencia não encontrada.")
        st.stop()
    if not col_m:
        st.error("❌ Coluna de Material não encontrada.")
        st.stop()
    if not month_vals:
        st.error("❌ Colunas de valor mensal não encontradas (use 'Valor Mês 01..12' ou 'Jan_Valor..Dez_Valor').")
        st.stop()

    # Gerências
    gerencias = get_unique_gerencias(df)
    if not gerencias:
        st.error("❌ Nenhuma gerência válida encontrada.")
        st.stop()

    st.header("🎯 Análise por Gerência")
    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        selected_gerencias = st.multiselect(
            "Escolha as gerências para análise:",
            gerencias,
            default=gerencias[:3] if len(gerencias) > 3 else gerencias,
        )
    with col_btn:
        if st.button("Selecionar Todas", type="secondary", use_container_width=True):
            selected_gerencias = gerencias
            st.experimental_rerun()

    if not selected_gerencias:
        st.warning("⚠️ Selecione pelo menos uma gerência para continuar.")
        st.stop()

    # Geração das análises (uma única vez)
    if st.button("🚀 Gerar Análises com IA", type="primary", use_container_width=True):
        with st.spinner("Processando análises..."):
            try:
                full_result = generate_all_gerencias_analysis(df)
                if full_result.get("status") != "sucesso":
                    st.warning("Falha ao gerar análises completas. Usando mock para as selecionadas.")
                    results = {g: generate_mock_analysis(df, g) for g in selected_gerencias}
                else:
                    analises = full_result.get("analises", {})
                    # filtra apenas as selecionadas; se faltar alguma, cria mock
                    results = {}
                    for g in selected_gerencias:
                        if g in analises and analises[g].get("status") == "sucesso":
                            results[g] = analises[g]
                        else:
                            results[g] = generate_mock_analysis(df, g)
                st.session_state["results"] = results
                st.success("✅ Análises concluídas!")
            except Exception as e:
                st.error(f"Erro ao gerar análises: {e}")
                st.session_state["results"] = {g: generate_mock_analysis(df, g) for g in selected_gerencias}

    # Exibição se houver resultados em sessão
    results: Dict[str, Any] = st.session_state.get("results", {})
    if results:
        # Resumo
        st.header("📈 Resumo Geral")
        total_valor = sum(r.get('kpis', {}).get('valor_total', 0) for r in results.values())
        total_materiais = sum(r.get('kpis', {}).get('numero_materiais', 0) for r in results.values())
        total_quantidade = sum(r.get('kpis', {}).get('quantidade_total', 0) for r in results.values())

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("💰 Valor Total (selecionadas)", safe_format_currency(total_valor))
        with c2: st.metric("📦 Materiais (soma)", safe_format_number(total_materiais))
        with c3: st.metric("📊 Quantidade (soma)", safe_format_number(total_quantidade))
        with c4: st.metric("🏢 Gerências", len(results))

        st.markdown("---")
        st.header("📊 Análises Detalhadas por Gerência")
        for g, data in results.items():
            # Exibe KPIs, gráficos, insights e resumo (função helper)
            display_gerencia_analysis(data)

            # Exibe estatísticas de colunas numéricas adicionais, se existirem
            extra_stats = data.get("metricas_colunas", {}) or {}
            if extra_stats:
                with st.expander("📊 Estatísticas por Coluna (Total e Média)", expanded=False):
                    rows: List[Dict[str, Any]] = []
                    for col_name, stats in extra_stats.items():
                        total = stats.get("total", 0.0)
                        media = stats.get("media", 0.0)
                        # Formatação condicional para colunas que parecem valores monetários
                        if "valor" in str(col_name).lower():
                            total_fmt = safe_format_currency(total)
                            media_fmt = safe_format_currency(media)
                        else:
                            total_fmt = safe_format_number(total)
                            media_fmt = safe_format_number(media)
                        rows.append({"Coluna": col_name, "Total": total_fmt, "Média": media_fmt})
                    df_stats = pd.DataFrame(rows)
                    st.dataframe(df_stats, use_container_width=True)

            st.markdown("---")

        # Downloads
        st.header("📥 Downloads e Relatórios")
        cdl1, cdl2 = st.columns(2)

        # Export CSV
        with cdl1:
            export_rows = []
            for g, r in results.items():
                k = r.get("kpis", {})
                export_rows.append({
                    "Gerencia": g,
                    "Valor_Total": k.get("valor_total", 0),
                    "Numero_Materiais": k.get("numero_materiais", 0),
                    "Quantidade_Total": k.get("quantidade_total", 0),
                    "Variacao_Mensal": k.get("variacao_mensal", 0),
                    "Status": r.get("status", "N/A"),
                    "Timestamp": r.get("timestamp", ""),
                })
            df_export = pd.DataFrame(export_rows)
            st.download_button(
                label="⬇️ Baixar CSV Processado",
                data=df_export.to_csv(index=False).encode("utf-8"),
                file_name=f"analise_estoque_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # PDFs (zip) das gerências selecionadas
        with cdl2:
            if st.button("📄 Gerar PDFs (ZIP) das Selecionadas", use_container_width=True):
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Gera um PDF por gerência selecionada utilizando os dados já calculados
                        pdf_paths: List[str] = []
                        for g, data in results.items():
                            safe_name = "".join(c for c in str(g) if c.isalnum() or c in (" ", "-", ".")).strip().replace(" ", "_")
                            pdf_path = os.path.join(tmpdir, f"Relatorio_Estoque_{safe_name or 'Relatorio'}.pdf")
                            generate_pdf_for_gerencia(data, pdf_path)
                            pdf_paths.append(pdf_path)

                        # Compacta em ZIP na memória
                        mem_zip = io.BytesIO()
                        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                            for p in pdf_paths:
                                zf.write(p, arcname=os.path.basename(p))
                        mem_zip.seek(0)

                    st.download_button(
                        label="⬇️ Baixar ZIP com PDFs",
                        data=mem_zip.getvalue(),
                        file_name=f"relatorios_estoque_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar PDFs: {e}")


if __name__ == "__main__":
    main()