"""
Módulo de geração de gráficos aprimorados para análise de estoque excedente.
Inclui visualizações específicas para dashboards por gerência.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import io
import warnings
warnings.filterwarnings('ignore')

# Configurar matplotlib para português
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def setup_plot_style():
    """Configura estilo padrão para os gráficos."""
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Configurações de fonte
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16
    })

def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira."""
    try:
        if pd.isna(value) or value == 0:
            return "R$ 0"
        
        if value >= 1_000_000:
            return f"R$ {value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"R$ {value/1_000:.1f}K"
        else:
            return f"R$ {value:.0f}"
    except:
        return "R$ 0"

def create_kpi_cards_chart(kpis: Dict[str, Any], gerencia: str) -> Optional[io.BytesIO]:
    """
    Cria gráfico com cartões de KPIs principais.
    
    Args:
        kpis: Dicionário com KPIs calculados
        gerencia: Nome da gerência
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        setup_plot_style()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'KPIs Principais - {gerencia}', fontsize=16, fontweight='bold')
        
        # Cores para os cartões
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        
        # KPI 1: Valor Total
        valor_total = kpis.get('valor_total', 0)
        ax1.text(0.5, 0.6, format_currency(valor_total), 
                ha='center', va='center', fontsize=24, fontweight='bold', color=colors[0])
        ax1.text(0.5, 0.3, 'Valor Total\nEstoque Excedente', 
                ha='center', va='center', fontsize=12, color='black')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                               edgecolor=colors[0], facecolor='none'))
        
        # KPI 2: Variação Mensal
        variacao = kpis.get('variacao_mensal', 0)
        variacao_text = f"{variacao:+.1f}%"
        variacao_color = colors[2] if variacao < 0 else colors[1]
        ax2.text(0.5, 0.6, variacao_text, 
                ha='center', va='center', fontsize=24, fontweight='bold', color=variacao_color)
        ax2.text(0.5, 0.3, 'Variação Mensal\n(Último vs Primeiro)', 
                ha='center', va='center', fontsize=12, color='black')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                               edgecolor=variacao_color, facecolor='none'))
        
        # KPI 3: Número de Materiais
        num_materiais = kpis.get('numero_materiais', 0)
        ax3.text(0.5, 0.6, f'{num_materiais:,}', 
                ha='center', va='center', fontsize=24, fontweight='bold', color=colors[2])
        ax3.text(0.5, 0.3, 'Materiais\nExcedentes', 
                ha='center', va='center', fontsize=12, color='black')
        ax3.set_xlim(0, 1)
        ax3.set_ylim(0, 1)
        ax3.axis('off')
        ax3.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                               edgecolor=colors[2], facecolor='none'))
        
        # KPI 4: Valor Médio por Material
        valor_medio = kpis.get('valor_medio_material', 0)
        ax4.text(0.5, 0.6, format_currency(valor_medio), 
                ha='center', va='center', fontsize=24, fontweight='bold', color=colors[3])
        ax4.text(0.5, 0.3, 'Valor Médio\npor Material', 
                ha='center', va='center', fontsize=12, color='black')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                               edgecolor=colors[3], facecolor='none'))
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de KPIs: {e}")
        plt.close('all')
        return None

def create_monthly_evolution_chart(monthly_data: List[Dict], gerencia: str) -> Optional[io.BytesIO]:
    """
    Cria gráfico de evolução mensal.
    
    Args:
        monthly_data: Lista com dados mensais
        gerencia: Nome da gerência
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        if not monthly_data:
            return None
            
        setup_plot_style()
        
        df = pd.DataFrame(monthly_data)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Gráfico de linha
        ax.plot(df['mes'], df['valor_total'], marker='o', linewidth=3, markersize=8, color='#3498db')
        
        # Área sob a curva
        ax.fill_between(df['mes'], df['valor_total'], alpha=0.3, color='#3498db')
        
        # Formatação
        ax.set_title(f'Evolução do Estoque Excedente - {gerencia}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontsize=12)
        ax.set_ylabel('Valor Total (R$)', fontsize=12)
        
        # Formatar eixo Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Rotacionar labels do eixo X
        plt.xticks(rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nos pontos
        for i, (mes, valor) in enumerate(zip(df['mes'], df['valor_total'])):
            ax.annotate(format_currency(valor), 
                       (i, valor), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center', fontsize=9)
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de evolução mensal: {e}")
        plt.close('all')
        return None

def create_top_materials_chart(top_materials: List[Dict], gerencia: str, n: int = 10) -> Optional[io.BytesIO]:
    """
    Cria gráfico de barras dos principais materiais.
    
    Args:
        top_materials: Lista com dados dos principais materiais
        gerencia: Nome da gerência
        n: Número de materiais a exibir
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        if not top_materials:
            return None
            
        setup_plot_style()
        
        df = pd.DataFrame(top_materials).head(n)
        
        if df.empty:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Criar gráfico de barras horizontais
        bars = ax.barh(range(len(df)), df['valor_total'], color='#e74c3c', alpha=0.8)
        
        # Formatação
        ax.set_title(f'Top {len(df)} Materiais com Maior Valor - {gerencia}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Valor Total (R$)', fontsize=12)
        ax.set_ylabel('Material', fontsize=12)
        
        # Labels dos materiais (truncar se muito longo)
        material_labels = [str(mat)[:30] + '...' if len(str(mat)) > 30 else str(mat) 
                          for mat in df['material']]
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels(material_labels)
        
        # Formatar eixo X
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Adicionar valores nas barras
        for i, (bar, valor) in enumerate(zip(bars, df['valor_total'])):
            width = bar.get_width()
            ax.text(width + max(df['valor_total']) * 0.01, bar.get_y() + bar.get_height()/2,
                   format_currency(valor), ha='left', va='center', fontsize=9)
        
        # Grid
        ax.grid(True, alpha=0.3, axis='x')
        
        # Inverter ordem para mostrar maior valor no topo
        ax.invert_yaxis()
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de top materiais: {e}")
        plt.close('all')
        return None

def create_prediction_chart(prediction_data: Dict[str, Any], gerencia: str) -> Optional[io.BytesIO]:
    """
    Cria gráfico com previsões de IA.
    
    Args:
        prediction_data: Dados da análise preditiva
        gerencia: Nome da gerência
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        if prediction_data.get('status') != 'sucesso':
            return None
            
        setup_plot_style()
        
        historicos = prediction_data.get('valores_historicos', [])
        previsoes = prediction_data.get('previsoes', [])
        
        if not historicos or not previsoes:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Dados históricos
        meses_hist = [f'Mês {i+1}' for i in range(len(historicos))]
        ax.plot(meses_hist, historicos, marker='o', linewidth=3, markersize=8, 
               color='#3498db', label='Dados Históricos')
        
        # Previsões
        meses_pred = [f'Mês {len(historicos)+i+1}' for i in range(len(previsoes))]
        # Conectar último ponto histórico com primeira previsão
        ax.plot([meses_hist[-1]] + meses_pred, [historicos[-1]] + previsoes, 
               marker='s', linewidth=3, markersize=8, linestyle='--',
               color='#e74c3c', label='Previsões IA')
        
        # Área de confiança (se disponível)
        confianca = prediction_data.get('confianca', 0.7)
        if confianca > 0:
            # Criar banda de confiança
            erro_pct = (1 - confianca) * 0.5  # Converter confiança em margem de erro
            previsoes_upper = [p * (1 + erro_pct) for p in previsoes]
            previsoes_lower = [p * (1 - erro_pct) for p in previsoes]
            
            ax.fill_between([meses_hist[-1]] + meses_pred, 
                           [historicos[-1]] + previsoes_lower,
                           [historicos[-1]] + previsoes_upper,
                           alpha=0.2, color='#e74c3c', label=f'Intervalo de Confiança ({confianca:.0%})')
        
        # Formatação
        tendencia = prediction_data.get('tendencia', 'indefinida')
        ax.set_title(f'Previsão de Estoque Excedente - {gerencia}\nTendência: {tendencia.title()}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontsize=12)
        ax.set_ylabel('Valor Total (R$)', fontsize=12)
        
        # Formatar eixo Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Rotacionar labels do eixo X
        plt.xticks(rotation=45)
        
        # Grid e legenda
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Linha vertical separando histórico de previsão
        ax.axvline(x=len(meses_hist)-0.5, color='gray', linestyle=':', alpha=0.7)
        ax.text(len(meses_hist)-0.5, max(max(historicos), max(previsoes)) * 0.9, 
               'Previsão', rotation=90, ha='right', va='top', alpha=0.7)
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de previsão: {e}")
        plt.close('all')
        return None

def create_anomalies_chart(anomalies_data: Dict[str, Any], gerencia: str) -> Optional[io.BytesIO]:
    """
    Cria gráfico de detecção de anomalias.
    
    Args:
        anomalies_data: Dados da detecção de anomalias
        gerencia: Nome da gerência
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        anomalias = anomalies_data.get('anomalias', [])
        
        if not anomalias:
            return None
            
        setup_plot_style()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Separar anomalias por tipo
        valores_atipicos = [a for a in anomalias if a.get('tipo') == 'valor_atipico']
        crescimentos_subitos = [a for a in anomalias if a.get('tipo') == 'crescimento_subito']
        
        y_pos = 0
        colors = {'alta': '#e74c3c', 'média': '#f39c12', 'baixa': '#3498db'}
        
        # Plotar valores atípicos
        if valores_atipicos:
            for i, anomalia in enumerate(valores_atipicos):
                severidade = anomalia.get('severidade', 'média')
                color = colors.get(severidade, '#3498db')
                
                ax.barh(y_pos, abs(anomalia.get('desvio_percentual', 0)), 
                       color=color, alpha=0.7, height=0.6)
                
                # Label
                material = str(anomalia.get('material', ''))[:20]
                ax.text(-1, y_pos, f"{material}\n({anomalia.get('mes', '')})", 
                       ha='right', va='center', fontsize=9)
                
                y_pos += 1
        
        # Plotar crescimentos súbitos
        if crescimentos_subitos:
            for i, anomalia in enumerate(crescimentos_subitos):
                severidade = anomalia.get('severidade', 'média')
                color = colors.get(severidade, '#3498db')
                
                ax.barh(y_pos, anomalia.get('crescimento_percentual', 0), 
                       color=color, alpha=0.7, height=0.6)
                
                # Label
                periodo = f"{anomalia.get('mes_anterior', '')} → {anomalia.get('mes_atual', '')}"
                ax.text(-1, y_pos, f"Crescimento\n{periodo}", 
                       ha='right', va='center', fontsize=9)
                
                y_pos += 1
        
        # Formatação
        ax.set_title(f'Anomalias Detectadas - {gerencia}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Desvio Percentual (%)', fontsize=12)
        ax.set_ylabel('Anomalias', fontsize=12)
        
        # Remover ticks do eixo Y
        ax.set_yticks([])
        
        # Grid
        ax.grid(True, alpha=0.3, axis='x')
        
        # Legenda de severidade
        legend_elements = [plt.Rectangle((0,0),1,1, facecolor=colors['alta'], alpha=0.7, label='Alta Severidade'),
                          plt.Rectangle((0,0),1,1, facecolor=colors['média'], alpha=0.7, label='Média Severidade')]
        ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de anomalias: {e}")
        plt.close('all')
        return None

def create_recommendations_chart(recommendations_data: Dict[str, Any], gerencia: str) -> Optional[io.BytesIO]:
    """
    Cria gráfico de recomendações de IA.
    
    Args:
        recommendations_data: Dados das recomendações
        gerencia: Nome da gerência
    
    Returns:
        Buffer com imagem do gráfico
    """
    try:
        recomendacoes = recommendations_data.get('recomendacoes', [])
        
        if not recomendacoes:
            return None
            
        setup_plot_style()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Agrupar por prioridade
        prioridades = {}
        for rec in recomendacoes:
            prioridade = rec.get('prioridade', 'baixa')
            if prioridade not in prioridades:
                prioridades[prioridade] = []
            prioridades[prioridade].append(rec)
        
        colors = {'alta': '#e74c3c', 'média': '#f39c12', 'baixa': '#2ecc71'}
        y_pos = 0
        
        for prioridade in ['alta', 'média', 'baixa']:
            if prioridade in prioridades:
                for rec in prioridades[prioridade]:
                    impacto = rec.get('impacto_estimado', 0)
                    
                    # Barra horizontal
                    ax.barh(y_pos, impacto, color=colors[prioridade], alpha=0.7, height=0.6)
                    
                    # Label da ação
                    acao = str(rec.get('acao', ''))[:40] + '...' if len(str(rec.get('acao', ''))) > 40 else str(rec.get('acao', ''))
                    ax.text(-max([r.get('impacto_estimado', 0) for r in recomendacoes]) * 0.05, y_pos, 
                           acao, ha='right', va='center', fontsize=9)
                    
                    # Valor do impacto
                    ax.text(impacto + max([r.get('impacto_estimado', 0) for r in recomendacoes]) * 0.01, y_pos,
                           format_currency(impacto), ha='left', va='center', fontsize=9)
                    
                    y_pos += 1
        
        # Formatação
        ax.set_title(f'Recomendações de IA - {gerencia}', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Impacto Estimado (R$)', fontsize=12)
        ax.set_ylabel('Recomendações', fontsize=12)
        
        # Formatar eixo X
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Remover ticks do eixo Y
        ax.set_yticks([])
        
        # Grid
        ax.grid(True, alpha=0.3, axis='x')
        
        # Legenda de prioridade
        legend_elements = []
        for prioridade in ['alta', 'média', 'baixa']:
            if prioridade in prioridades:
                legend_elements.append(
                    plt.Rectangle((0,0),1,1, facecolor=colors[prioridade], alpha=0.7, 
                                 label=f'Prioridade {prioridade.title()}')
                )
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='lower right')
        
        plt.tight_layout()
        
        # Salvar em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
        
    except Exception as e:
        print(f"Erro ao criar gráfico de recomendações: {e}")
        plt.close('all')
        return None

def generate_all_charts_for_gerencia(analysis_data: Dict[str, Any]) -> Dict[str, io.BytesIO]:
    """
    Gera todos os gráficos para uma gerência.
    
    Args:
        analysis_data: Dados completos da análise da gerência
    
    Returns:
        Dict com todos os gráficos gerados
    """
    try:
        gerencia = analysis_data.get('gerencia', 'Desconhecida')
        charts = {}
        
        # Gráfico de KPIs
        kpis_chart = create_kpi_cards_chart(analysis_data.get('kpis', {}), gerencia)
        if kpis_chart:
            charts['kpis'] = kpis_chart
        
        # Gráfico de evolução mensal
        monthly_chart = create_monthly_evolution_chart(analysis_data.get('evolucao_mensal', []), gerencia)
        if monthly_chart:
            charts['evolucao_mensal'] = monthly_chart
        
        # Gráfico de top materiais
        materials_chart = create_top_materials_chart(analysis_data.get('top_materiais', []), gerencia)
        if materials_chart:
            charts['top_materiais'] = materials_chart
        
        # Gráficos de IA
        ai_data = analysis_data.get('analises_ia', {})
        
        # Gráfico de previsão
        prediction_chart = create_prediction_chart(ai_data.get('analise_preditiva', {}), gerencia)
        if prediction_chart:
            charts['previsao'] = prediction_chart
        
        # Gráfico de anomalias
        anomalies_chart = create_anomalies_chart(ai_data.get('deteccao_anomalias', {}), gerencia)
        if anomalies_chart:
            charts['anomalias'] = anomalies_chart
        
        # Gráfico de recomendações
        recommendations_chart = create_recommendations_chart(ai_data.get('analise_prescritiva', {}), gerencia)
        if recommendations_chart:
            charts['recomendacoes'] = recommendations_chart
        
        return charts
        
    except Exception as e:
        print(f"Erro ao gerar gráficos para gerência: {e}")
        return {}

