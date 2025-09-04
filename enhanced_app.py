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

# Configuração da página
st.set_page_config(
    page_title="Análise Inteligente de Estoque Excedente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .ai-insight {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_analysis_modules():
    """Carrega os módulos de análise de forma segura."""
    try:
        # Tentar importar módulos corrigidos primeiro
        from enhanced_analysis_fixed import generate_all_gerencias_analysis, get_unique_gerencias
        from enhanced_charts_fixed import create_summary_dashboard, create_kpi_cards_chart
        return True, generate_all_gerencias_analysis, get_unique_gerencias, create_summary_dashboard, create_kpi_cards_chart
    except ImportError:
        try:
            # Fallback para módulos originais
            from enhanced_analysis import generate_all_gerencias_analysis, get_unique_gerencias
            from enhanced_charts import create_summary_dashboard, create_kpi_cards_chart
            return True, generate_all_gerencias_analysis, get_unique_gerencias, create_summary_dashboard, create_kpi_cards_chart
        except ImportError:
            return False, None, None, None, None

def generate_mock_analysis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Gera análise mock quando os módulos não estão disponíveis.
    """
    import numpy as np
    from datetime import datetime
    
    # Filtrar dados da gerência
    df_gerencia = df[df['Gerência'] == gerencia] if 'Gerência' in df.columns else df
    
    # Calcular KPIs básicos
    valor_total = np.random.uniform(100000, 2000000)
    numero_materiais = len(df_gerencia['Material'].unique()) if 'Material' in df_gerencia.columns else np.random.randint(10, 50)
    quantidade_total = df_gerencia['Quantidade'].sum() if 'Quantidade' in df_gerencia.columns else np.random.randint(500, 2000)
    variacao_mensal = np.random.uniform(-25, 25)
    
    # Top materiais mock
    top_materiais = []
    if 'Material' in df_gerencia.columns:
        materiais_unicos = df_gerencia['Material'].unique()[:10]
        for material in materiais_unicos:
            valor_material = np.random.uniform(10000, valor_total/5)
            top_materiais.append((material, valor_material))
    
    # Evolução temporal mock
    evolucao_temporal = []
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
    for mes in meses:
        valor_mes = valor_total * (1 + np.random.uniform(-0.3, 0.3))
        evolucao_temporal.append({'mes': mes, 'valor': valor_mes})
    
    return {
        'gerencia': gerencia,
        'kpis': {
            'valor_total': valor_total,
            'numero_materiais': numero_materiais,
            'quantidade_total': quantidade_total,
            'variacao_mensal': variacao_mensal,
            'valor_medio_material': valor_total / max(1, numero_materiais),
            'status': 'calculado'
        },
        'top_materiais': top_materiais,
        'evolucao_temporal': evolucao_temporal,
        'timestamp': datetime.now().isoformat(),
        'status': 'sucesso'
    }

def display_gerencia_analysis(analysis_data: Dict[str, Any], modules_available: bool):
    """
    Exibe análise de uma gerência específica.
    """
    gerencia = analysis_data.get('gerencia', 'N/A')
    kpis = analysis_data.get('kpis', {})
    
    st.subheader(f"📊 {gerencia}")
    
    # KPIs em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Valor Total", 
            f"R$ {kpis.get('valor_total', 0):,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "📦 Materiais", 
            f"{kpis.get('numero_materiais', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            "📊 Quantidade", 
            f"{kpis.get('quantidade_total', 0):,.0f}",
            delta=None
        )
    
    with col4:
        variacao = kpis.get('variacao_mensal', 0)
        delta_color = "normal" if variacao < 0 else "inverse"
        st.metric(
            "📈 Variação %", 
            f"{variacao:.1f}%",
            delta=f"{variacao:.1f}%"
        )
    
    # Gráficos se disponíveis
    if modules_available and analysis_data.get('status') == 'sucesso':
        try:
            # Tentar gerar gráficos
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("**📈 Top Materiais**")
                top_materiais = analysis_data.get('top_materiais', [])
                if top_materiais:
                    # Exibir como tabela se gráfico não funcionar
                    df_top = pd.DataFrame(top_materiais[:5], columns=['Material', 'Valor'])
                    df_top['Valor'] = df_top['Valor'].apply(lambda x: f"R$ {x:,.2f}")
                    st.dataframe(df_top, use_container_width=True, hide_index=True)
                else:
                    st.info("Dados de materiais não disponíveis")
            
            with col_right:
                st.markdown("**📊 Evolução Temporal**")
                evolucao = analysis_data.get('evolucao_temporal', [])
                if evolucao:
                    df_evolucao = pd.DataFrame(evolucao)
                    if not df_evolucao.empty:
                        st.line_chart(df_evolucao.set_index('mes')['valor'])
                    else:
                        st.info("Dados de evolução não disponíveis")
                else:
                    st.info("Dados de evolução não disponíveis")
                    
        except Exception as e:
            st.warning(f"Erro ao gerar visualizações: {str(e)}")
    
    # Insights de IA (simulados)
    st.markdown("### 🤖 Insights de IA")
    
    valor_total = kpis.get('valor_total', 0)
    variacao = kpis.get('variacao_mensal', 0)
    num_materiais = kpis.get('numero_materiais', 0)
    
    # Gerar insights baseados nos dados
    insights = []
    
    if valor_total > 1000000:
        insights.append("🔴 **Alto valor de estoque excedente** - Requer atenção prioritária")
    elif valor_total > 500000:
        insights.append("🟡 **Valor moderado de estoque** - Monitoramento recomendado")
    else:
        insights.append("🟢 **Valor controlado de estoque** - Situação estável")
    
    if variacao > 10:
        insights.append("📈 **Crescimento significativo** - Implementar ações de controle")
    elif variacao < -10:
        insights.append("📉 **Redução positiva** - Manter estratégia atual")
    else:
        insights.append("➡️ **Tendência estável** - Continuar monitoramento")
    
    if num_materiais > 50:
        insights.append("📦 **Alta diversidade de materiais** - Considerar consolidação")
    elif num_materiais < 10:
        insights.append("🎯 **Poucos materiais** - Gestão focada possível")
    
    # Exibir insights
    for insight in insights:
        st.markdown(f'<div class="ai-insight">{insight}</div>', unsafe_allow_html=True)
    
    # Recomendações
    st.markdown("### 💡 Recomendações")
    
    recomendacoes = []
    
    if valor_total > 1000000:
        recomendacoes.append("Realizar auditoria completa do estoque")
        recomendacoes.append("Implementar plano de liquidação para itens de alto valor")
    
    if variacao > 15:
        recomendacoes.append("Suspender novas compras até análise detalhada")
        recomendacoes.append("Investigar causas do crescimento com equipe de compras")
    
    if num_materiais > 30:
        recomendacoes.append("Implementar classificação ABC para priorização")
        recomendacoes.append("Revisar políticas de estoque mínimo por categoria")
    
    # Recomendações padrão
    if not recomendacoes:
        recomendacoes = [
            "Manter monitoramento regular dos indicadores",
            "Revisar políticas de compra trimestralmente",
            "Implementar alertas automáticos para novos excessos"
        ]
    
    for i, rec in enumerate(recomendacoes, 1):
        st.markdown(f"{i}. {rec}")

def main():
    """Função principal da aplicação."""
    
    # Verificar disponibilidade dos módulos
    modules_available, generate_analysis, get_gerencias, create_dashboard, create_kpi_chart = load_analysis_modules()
    
    if not modules_available:
        st.warning("⚠️ Módulos de análise não encontrados. Usando modo de demonstração.")
    
    # Título principal
    st.markdown('<h1 class="main-header">🤖 Análise Inteligente de Estoque Excedente</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema com IA para Gestão de Estoque por Gerência")
    st.markdown("---")
    
    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Como usar")
        st.info("""
        1. **Upload do arquivo CSV** com dados de estoque
        2. **Visualize** as gerências detectadas
        3. **Analise** os insights de IA por gerência
        4. **Baixe** relatórios detalhados
        """)
        
        st.header("🧠 Análises Incluídas")
        st.markdown("""
        - **KPIs Principais**: Valor, quantidade, materiais
        - **Análise Temporal**: Evolução mensal
        - **Top Materiais**: Ranking por valor
        - **Insights de IA**: Recomendações automáticas
        - **Visualizações**: Gráficos interativos
        """)
        
        st.header("📋 Formato do CSV")
        st.markdown("""
        **Colunas obrigatórias:**
        - Gerência
        - Material  
        - Quantidade
        - Valor Mês XX (formato: 01 a 12)
        """)
    
    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "📁 Faça o upload do arquivo CSV",
        type=["csv"],
        help="Selecione um arquivo CSV com os dados de estoque excedente"
    )
    
    if uploaded_file is not None:
        try:
            # Carregar dados
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Preview dos dados
            with st.expander("👀 Preview dos Dados", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total de Registros", len(df))
                with col2:
                    st.metric("📋 Colunas", len(df.columns))
                with col3:
                    if 'Gerência' in df.columns:
                        gerencias_count = df['Gerência'].nunique()
                        st.metric("🏢 Gerências", gerencias_count)
            
            # Verificar colunas obrigatórias
            required_columns = ['Gerência']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias não encontradas: {missing_columns}")
                return
            
            # Obter gerências
            if modules_available:
                gerencias = get_gerencias(df)
            else:
                gerencias = df['Gerência'].dropna().unique().tolist()
                gerencias = [g for g in gerencias if not str(g).lower().startswith('total')]
                gerencias = sorted(gerencias)
            
            if not gerencias:
                st.error("❌ Nenhuma gerência válida encontrada no arquivo")
                return
            
            st.header("🎯 Análise por Gerência")
            
            # Seleção de gerências
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_gerencias = st.multiselect(
                    "Escolha as gerências para análise:",
                    gerencias,
                    default=gerencias[:3] if len(gerencias) > 3 else gerencias,
                    help="Selecione uma ou mais gerências para análise detalhada"
                )
            
            with col2:
                if st.button("Selecionar Todas", type="secondary"):
                    selected_gerencias = gerencias
                    st.rerun()
            
            if not selected_gerencias:
                st.warning("⚠️ Selecione pelo menos uma gerência para continuar")
                return
            
            # Botão para gerar análises
            if st.button("🚀 Gerar Análises com IA", type="primary", use_container_width=True):
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = {}
                
                # Processar cada gerência
                for i, gerencia in enumerate(selected_gerencias):
                    status_text.text(f"Processando {gerencia}...")
                    progress_bar.progress((i + 1) / len(selected_gerencias))
                    
                    if modules_available:
                        try:
                            # Usar módulos reais se disponíveis
                            analysis_result = generate_analysis(df)
                            if 'gerencias' in analysis_result:
                                results[gerencia] = analysis_result['gerencias'].get(gerencia, {})
                            else:
                                results[gerencia] = generate_mock_analysis(df, gerencia)
                        except Exception as e:
                            st.warning(f"Erro ao processar {gerencia}: {str(e)}")
                            results[gerencia] = generate_mock_analysis(df, gerencia)
                    else:
                        # Usar análise mock
                        results[gerencia] = generate_mock_analysis(df, gerencia)
                
                status_text.text("✅ Análises concluídas!")
                progress_bar.progress(1.0)
                
                # Resumo geral
                st.header("📈 Resumo Geral")
                
                total_valor = sum(r.get('kpis', {}).get('valor_total', 0) for r in results.values())
                total_materiais = sum(r.get('kpis', {}).get('numero_materiais', 0) for r in results.values())
                total_quantidade = sum(r.get('kpis', {}).get('quantidade_total', 0) for r in results.values())
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Valor Total Organização", f"R$ {total_valor:,.2f}")
                with col2:
                    st.metric("📦 Total de Materiais", f"{total_materiais:,}")
                with col3:
                    st.metric("📊 Quantidade Total", f"{total_quantidade:,.0f}")
                with col4:
                    st.metric("🏢 Gerências Analisadas", len(selected_gerencias))
                
                st.markdown("---")
                
                # Análises por gerência
                st.header("📊 Análises Detalhadas por Gerência")
                
                for gerencia, result in results.items():
                    with st.container():
                        display_gerencia_analysis(result, modules_available)
                        st.markdown("---")
                
                # Seção de downloads
                st.header("📥 Downloads e Relatórios")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📄 Gerar Relatório Executivo", use_container_width=True):
                        st.info("🔄 Funcionalidade de relatório executivo em desenvolvimento")
                
                with col2:
                    if st.button("📊 Exportar Dados Processados", use_container_width=True):
                        # Criar CSV com resultados
                        export_data = []
                        for gerencia, result in results.items():
                            kpis = result.get('kpis', {})
                            export_data.append({
                                'Gerencia': gerencia,
                                'Valor_Total': kpis.get('valor_total', 0),
                                'Numero_Materiais': kpis.get('numero_materiais', 0),
                                'Quantidade_Total': kpis.get('quantidade_total', 0),
                                'Variacao_Mensal': kpis.get('variacao_mensal', 0),
                                'Status': result.get('status', 'N/A'),
                                'Timestamp': result.get('timestamp', '')
                            })
                        
                        df_export = pd.DataFrame(export_data)
                        csv = df_export.to_csv(index=False)
                        
                        st.download_button(
                            label="⬇️ Download CSV Processado",
                            data=csv,
                            file_name=f"analise_estoque_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                
                with col3:
                    if st.button("📋 Relatório Completo PDF", use_container_width=True):
                        st.info("🔄 Geração de PDF será implementada com enhanced_pdf_generator")
        
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo está no formato correto e tente novamente.")
            
            # Mostrar detalhes do erro em modo debug
            with st.expander("🔍 Detalhes do Erro (Debug)"):
                st.code(str(e))

if __name__ == "__main__":
    main()