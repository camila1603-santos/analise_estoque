"""
Aplicação Streamlit aprimorada para análise de estoque excedente com IA.
Gera PDFs individuais por gerência com dashboards completos.
"""

import streamlit as st
import pandas as pd
import os
import tempfile
import zipfile
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# Importar módulos desenvolvidos
from enhanced_analysis import generate_all_gerencias_analysis, get_unique_gerencias
from enhanced_pdf_generator import generate_all_pdfs

# Configuração da página
st.set_page_config(
    page_title="Análise Inteligente de Estoque Excedente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Função principal da aplicação."""
    
    # Título principal
    st.title("🤖 Análise Inteligente de Estoque Excedente")
    st.markdown("### Sistema com IA para Gestão de Estoque por Gerência")
    st.markdown("---")
    
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Como usar")
        st.info("""
        1. **Upload do arquivo CSV** com dados de estoque
        2. **Visualize** as gerências detectadas
        3. **Gere relatórios PDF** individuais por gerência
        4. **Baixe** todos os PDFs em um arquivo ZIP
        """)
        
        st.header("🧠 Análises de IA Incluídas")
        st.markdown("""
        - **Análise Preditiva**: Previsão de tendências
        - **Detecção de Anomalias**: Identificação de padrões atípicos
        - **Análise Prescritiva**: Recomendações de ações
        - **Resumo em Linguagem Natural**: Insights automatizados
        """)
        
        st.header("📊 Visualizações")
        st.markdown("""
        - **KPIs Principais**: Cartões com métricas-chave
        - **Evolução Temporal**: Gráficos de tendência
        - **Top Materiais**: Ranking por valor
        - **Gráficos de IA**: Previsões e anomalias
        """)
        
        st.header("📋 Formato do CSV")
        st.markdown("""
        Colunas obrigatórias:
        - **Gerência**
        - **Material**
        - **Área**
        - **Quantidade**
        - **Valor Mês XX** (01-12)
        """)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📁 Faça o upload do arquivo CSV",
        type=["csv"],
        help="Selecione um arquivo CSV com os dados de estoque excedente"
    )
    
    if uploaded_file is not None:
        try:
            # Ler arquivo
            with st.spinner("📖 Lendo e processando arquivo..."):
                df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Arquivo carregado! Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            # Detectar gerências
            gerencias = get_unique_gerencias(df)
            
            if not gerencias:
                st.error("❌ Nenhuma gerência encontrada no arquivo. Verifique se a coluna 'Gerência' existe.")
                return
            
            st.info(f"🏢 **{len(gerencias)} gerências detectadas:** {', '.join(gerencias)}")
            
            # Preview dos dados
            with st.expander("👀 Visualizar dados do arquivo"):
                st.dataframe(df.head(10), use_container_width=True)
                st.write(f"**Colunas encontradas:** {list(df.columns)}")
            
            # Seção de análise e geração de PDFs
            st.markdown("---")
            st.subheader("🚀 Gerar Relatórios com IA")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                **O que será gerado para cada gerência:**
                - 📊 Dashboard com KPIs principais
                - 📈 Gráficos de evolução temporal
                - 🎯 Top 10 materiais por valor
                - 🤖 Análises preditivas com IA
                - ⚠️ Detecção de anomalias
                - 💡 Recomendações de ações
                - 📝 Resumo executivo automatizado
                - 📋 Tabela detalhada de dados
                """)
            
            with col2:
                if st.button("🎯 Gerar Relatórios PDF", type="primary", use_container_width=True):
                    generate_reports(df, gerencias)
            
            # Seção de análise prévia (opcional)
            st.markdown("---")
            st.subheader("🔍 Análise Prévia (Opcional)")
            
            selected_gerencia = st.selectbox(
                "Selecione uma gerência para análise prévia:",
                ["Selecione..."] + gerencias
            )
            
            if selected_gerencia != "Selecione...":
                show_preview_analysis(df, selected_gerencia)
                
        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato correto e contém as colunas necessárias.")
    
    else:
        # Página inicial sem arquivo
        st.info("👆 Faça upload de um arquivo CSV para começar a análise.")
        
        # Exemplo de estrutura
        with st.expander("📋 Exemplo de estrutura do CSV"):
            example_data = {
                "Gerência": ["Operações", "Logística", "Qualidade"],
                "Área": ["Produção A", "Armazenagem", "Controle"],
                "Material": ["Material A", "Material B", "Material C"],
                "Quantidade": [100, 75, 50],
                "Valor Mês 01": [100000, 75000, 50000],
                "Valor Mês 02": [95000, 70000, 48000],
                "Valor Mês 03": [90000, 68000, 46000]
            }
            st.dataframe(pd.DataFrame(example_data), use_container_width=True)

def generate_reports(df: pd.DataFrame, gerencias: List[str]):
    """Gera relatórios PDF para todas as gerências."""
    try:
        with st.spinner("🧠 Executando análises de IA e gerando relatórios..."):
            # Executar análises completas
            all_analysis = generate_all_gerencias_analysis(df)
            
            if all_analysis.get("status") != "sucesso":
                st.error(f"❌ Erro nas análises: {all_analysis.get('mensagem', 'Erro desconhecido')}")
                return
            
            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                # Gerar PDFs
                pdf_paths = generate_all_pdfs(all_analysis, temp_dir)
                
                if not pdf_paths:
                    st.error("❌ Nenhum PDF foi gerado.")
                    return
                
                st.success(f"✅ {len(pdf_paths)} relatórios PDF gerados com sucesso!")
                
                # Criar arquivo ZIP
                zip_path = os.path.join(temp_dir, "relatorios_estoque_excedente.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for pdf_path in pdf_paths:
                        zipf.write(pdf_path, os.path.basename(pdf_path))
                
                # Botão de download
                with open(zip_path, "rb") as f:
                    zip_bytes = f.read()
                
                st.download_button(
                    label="📥 Baixar Todos os Relatórios (ZIP)",
                    data=zip_bytes,
                    file_name="relatorios_estoque_excedente.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                # Mostrar lista de arquivos gerados
                st.markdown("**📄 Relatórios gerados:**")
                for i, pdf_path in enumerate(pdf_paths, 1):
                    filename = os.path.basename(pdf_path)
                    gerencia_name = filename.replace("Relatorio_Estoque_", "").replace(".pdf", "")
                    st.write(f"{i}. {gerencia_name}")
                
    except Exception as e:
        st.error(f"❌ Erro ao gerar relatórios: {str(e)}")

def show_preview_analysis(df: pd.DataFrame, gerencia: str):
    """Mostra análise prévia para uma gerência selecionada."""
    try:
        with st.spinner(f"🔍 Analisando dados da gerência {gerencia}..."):
            from enhanced_analysis import comprehensive_gerencia_analysis
            
            analysis = comprehensive_gerencia_analysis(df, gerencia)
            
            if analysis.get("status") != "sucesso":
                st.error(f"❌ Erro na análise: {analysis.get('erro', 'Erro desconhecido')}")
                return
            
            # Mostrar KPIs
            st.markdown(f"#### 📊 KPIs - {gerencia}")
            kpis = analysis.get("kpis", {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                valor_total = kpis.get("valor_total", 0)
                st.metric("Valor Total", f"R$ {valor_total:,.2f}")
            
            with col2:
                num_materiais = kpis.get("numero_materiais", 0)
                st.metric("Nº Materiais", f"{num_materiais:,}")
            
            with col3:
                quantidade_total = kpis.get("quantidade_total", 0)
                st.metric("Quantidade Total", f"{quantidade_total:,}")
            
            with col4:
                variacao = kpis.get("variacao_mensal", 0)
                st.metric("Variação Mensal", f"{variacao:+.1f}%")
            
            # Mostrar top materiais
            top_materiais = analysis.get("top_materiais", [])
            if top_materiais:
                st.markdown("#### 🎯 Top 5 Materiais por Valor")
                df_top = pd.DataFrame(top_materiais[:5])
                df_top["valor_total"] = df_top["valor_total"].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(df_top, use_container_width=True, hide_index=True)
            
            # Mostrar resumo de IA
            ai_data = analysis.get("analises_ia", {})
            resumo_ia = ai_data.get("resumo_executivo", {})
            
            if resumo_ia.get("status") == "sucesso":
                st.markdown("#### 🤖 Resumo Executivo (IA)")
                st.text_area("", resumo_ia.get("resumo", ""), height=200, disabled=True)
            
            # Mostrar recomendações
            prescritiva = ai_data.get("analise_prescritiva", {})
            recomendacoes = prescritiva.get("recomendacoes", [])
            
            if recomendacoes:
                st.markdown("#### 💡 Principais Recomendações")
                for i, rec in enumerate(recomendacoes[:3], 1):
                    prioridade = rec.get("prioridade", "baixa")
                    emoji = "🔴" if prioridade == "alta" else "🟡" if prioridade == "média" else "🟢"
                    st.write(f"{emoji} **{rec.get('acao', '')}**")
                    st.write(f"   {rec.get('detalhes', '')}")
            
    except Exception as e:
        st.error(f"❌ Erro na análise prévia: {str(e)}")

if __name__ == "__main__":
    main()

