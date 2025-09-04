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

def create_kpi_cards_chart(kpis: Dict[str, Any], gerencia: str) -> io.BytesIO:
    """
    Cria gráfico com cards de KPIs principais.
    
    Args:
        kpis: Dicionário com KPIs calculados
        gerencia: Nome da gerência
    
    Returns:
        BytesIO com imagem do gráfico
    """
    setup_plot_style()
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f'KPIs Principais - {gerencia}', fontsize=16, fontweight='bold')
    
    # Card 1: Valor Total
    ax1 = axes[0, 0]
    ax1.text(0.5, 0.7, 'Valor Total', ha='center', va='center', fontsize=14, fontweight='bold')
    ax1.text(0.5, 0.3, format_currency(kpis.get('valor_total', 0)), 
             ha='center', va='center', fontsize=20, color='#1f77b4', fontweight='bold')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis('off')
    ax1.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                           edgecolor='#1f77b4', facecolor='#e6f3ff', alpha=0.3))
    
    # Card 2: Número de Materiais
    ax2 = axes[0, 1]
    ax2.text(0.5, 0.7, 'Materiais', ha='center', va='center', fontsize=14, fontweight='bold')
    ax2.text(0.5, 0.3, f"{kpis.get('numero_materiais', 0):,}", 
             ha='center', va='center', fontsize=20, color='#ff7f0e', fontweight='bold')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.axis('off')
    ax2.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                           edgecolor='#ff7f0e', facecolor='#fff2e6', alpha=0.3))
    
    # Card 3: Quantidade Total
    ax3 = axes[1, 0]
    ax3.text(0.5, 0.7, 'Quantidade', ha='center', va='center', fontsize=14, fontweight='bold')
    ax3.text(0.5, 0.3, f"{kpis.get('quantidade_total', 0):,.0f}", 
             ha='center', va='center', fontsize=20, color='#2ca02c', fontweight='bold')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    ax3.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                           edgecolor='#2ca02c', facecolor='#e6ffe6', alpha=0.3))
    
    # Card 4: Variação Mensal
    ax4 = axes[1, 1]
    variacao = kpis.get('variacao_mensal', 0)
    cor_variacao = '#d62728' if variacao > 0 else '#2ca02c'
    sinal = '+' if variacao > 0 else ''
    
    ax4.text(0.5, 0.7, 'Variação Mensal', ha='center', va='center', fontsize=14, fontweight='bold')
    ax4.text(0.5, 0.3, f"{sinal}{variacao:.1f}%", 
             ha='center', va='center', fontsize=20, color=cor_variacao, fontweight='bold')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    cor_fundo = '#ffe6e6' if variacao > 0 else '#e6ffe6'
    ax4.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                           edgecolor=cor_variacao, facecolor=cor_fundo, alpha=0.3))
    
    plt.tight_layout()
    
    # Salvar em BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_top_materials_chart(top_materiais: List[Tuple[str, float]], gerencia: str) -> io.BytesIO:
    """
    Cria gráfico de barras com top materiais por valor.
    
    Args:
        top_materiais: Lista de tuplas (material, valor)
        gerencia: Nome da gerência
    
    Returns:
        BytesIO com imagem do gráfico
    """
    setup_plot_style()
    
    if not top_materiais:
        # Criar gráfico vazio se não houver dados
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Nenhum material encontrado', 
                ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        plt.title(f'Top Materiais por Valor - {gerencia}')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    
    # Preparar dados
    materiais = [item[0] for item in top_materiais[:10]]  # Top 10
    valores = [item[1] for item in top_materiais[:10]]
    
    # Criar gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Cores gradientes
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(materiais)))
    
    bars = ax.barh(materiais, valores, color=colors)
    
    # Adicionar valores nas barras
    for i, (bar, valor) in enumerate(zip(bars, valores)):
        width = bar.get_width()
        ax.text(width + max(valores) * 0.01, bar.get_y() + bar.get_height()/2, 
                format_currency(valor), ha='left', va='center', fontweight='bold')
    
    ax.set_xlabel('Valor (R$)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Material', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {len(materiais)} Materiais por Valor - {gerencia}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Formatar eixo X
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
    
    # Inverter ordem para maior valor no topo
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    # Salvar em BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_temporal_evolution_chart(evolucao_temporal: List[Dict[str, Any]], gerencia: str) -> io.BytesIO:
    """
    Cria gráfico de evolução temporal dos valores.
    
    Args:
        evolucao_temporal: Lista com dados de evolução mensal
        gerencia: Nome da gerência
    
    Returns:
        BytesIO com imagem do gráfico
    """
    setup_plot_style()
    
    if not evolucao_temporal:
        # Criar gráfico vazio se não houver dados
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Dados de evolução temporal não disponíveis', 
                ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        plt.title(f'Evolução Temporal - {gerencia}')
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    
    # Preparar dados
    meses = [item['mes'] for item in evolucao_temporal]
    valores = [item['valor'] for item in evolucao_temporal]
    
    # Criar gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Linha principal
    ax.plot(meses, valores, marker='o', linewidth=3, markersize=8, 
            color='#1f77b4', markerfacecolor='white', markeredgewidth=2)
    
    # Área sob a curva
    ax.fill_between(meses, valores, alpha=0.3, color='#1f77b4')
    
    # Adicionar valores nos pontos
    for i, (mes, valor) in enumerate(zip(meses, valores)):
        ax.annotate(format_currency(valor), 
                   (i, valor), 
                   textcoords="offset points", 
                   xytext=(0,10), 
                   ha='center', 
                   fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax.set_xlabel('Período', fontsize=12, fontweight='bold')
    ax.set_ylabel('Valor do Estoque Excedente', fontsize=12, fontweight='bold')
    ax.set_title(f'Evolução Temporal do Estoque Excedente - {gerencia}', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Formatar eixo Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
    
    # Rotacionar labels do eixo X se necessário
    if len(meses) > 6:
        plt.xticks(rotation=45)
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar em BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

def create_summary_dashboard(analysis_data: Dict[str, Any]) -> io.BytesIO:
    """
    Cria dashboard resumo com múltiplas visualizações.
    
    Args:
        analysis_data: Dados completos da análise
    
    Returns:
        BytesIO com imagem do dashboard
    """
    setup_plot_style()
    
    gerencia = analysis_data.get('gerencia', 'N/A')
    kpis = analysis_data.get('kpis', {})
    top_materiais = analysis_data.get('top_materiais', [])
    evolucao = analysis_data.get('evolucao_temporal', [])
    
    # Criar figura com subplots
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.5, 1.5], hspace=0.3, wspace=0.3)
    
    # Título principal
    fig.suptitle(f'Dashboard Completo - {gerencia}', fontsize=20, fontweight='bold', y=0.95)
    
    # 1. KPIs (linha superior, ocupando toda a largura)
    ax_kpis = fig.add_subplot(gs[0, :])
    
    # Criar mini cards de KPIs
    kpi_names = ['Valor Total', 'Materiais', 'Quantidade', 'Variação %']
    kpi_values = [
        format_currency(kpis.get('valor_total', 0)),
        f"{kpis.get('numero_materiais', 0):,}",
        f"{kpis.get('quantidade_total', 0):,.0f}",
        f"{kpis.get('variacao_mensal', 0):+.1f}%"
    ]
    kpi_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728' if kpis.get('variacao_mensal', 0) > 0 else '#2ca02c']
    
    for i, (name, value, color) in enumerate(zip(kpi_names, kpi_values, kpi_colors)):
        x_pos = i * 0.25 + 0.125
        
        # Retângulo do card
        rect = Rectangle((x_pos - 0.1, 0.2), 0.2, 0.6, 
                        linewidth=2, edgecolor=color, facecolor=color, alpha=0.1)
        ax_kpis.add_patch(rect)
        
        # Texto
        ax_kpis.text(x_pos, 0.7, name, ha='center', va='center', 
                    fontsize=10, fontweight='bold')
        ax_kpis.text(x_pos, 0.4, value, ha='center', va='center', 
                    fontsize=14, fontweight='bold', color=color)
    
    ax_kpis.set_xlim(0, 1)
    ax_kpis.set_ylim(0, 1)
    ax_kpis.axis('off')
    
    # 2. Top Materiais (esquerda inferior)
    ax_materials = fig.add_subplot(gs[1, 0])
    
    if top_materiais:
        materiais = [item[0] for item in top_materiais[:8]]  # Top 8 para caber melhor
        valores = [item[1] for item in top_materiais[:8]]
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(materiais)))
        bars = ax_materials.barh(materiais, valores, color=colors)
        
        # Adicionar valores
        for bar, valor in zip(bars, valores):
            width = bar.get_width()
            ax_materials.text(width + max(valores) * 0.02, bar.get_y() + bar.get_height()/2, 
                            format_currency(valor), ha='left', va='center', fontsize=9)
        
        ax_materials.set_xlabel('Valor (R$)', fontsize=10)
        ax_materials.set_title('Top Materiais por Valor', fontsize=12, fontweight='bold')
        ax_materials.invert_yaxis()
        
        # Formatar eixo X
        ax_materials.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
    else:
        ax_materials.text(0.5, 0.5, 'Dados não disponíveis', ha='center', va='center')
        ax_materials.set_xlim(0, 1)
        ax_materials.set_ylim(0, 1)
        ax_materials.axis('off')
    
    # 3. Evolução Temporal (direita inferior)
    ax_evolution = fig.add_subplot(gs[1, 1])
    
    if evolucao and len(evolucao) > 1:
        meses = [item['mes'] for item in evolucao]
        valores = [item['valor'] for item in evolucao]
        
        ax_evolution.plot(meses, valores, marker='o', linewidth=2, markersize=6, color='#1f77b4')
        ax_evolution.fill_between(meses, valores, alpha=0.3, color='#1f77b4')
        
        ax_evolution.set_xlabel('Período', fontsize=10)
        ax_evolution.set_ylabel('Valor (R$)', fontsize=10)
        ax_evolution.set_title('Evolução Temporal', fontsize=12, fontweight='bold')
        
        # Formatar eixo Y
        ax_evolution.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Rotacionar labels se necessário
        if len(meses) > 4:
            plt.setp(ax_evolution.xaxis.get_majorticklabels(), rotation=45)
        
        ax_evolution.grid(True, alpha=0.3)
    else:
        ax_evolution.text(0.5, 0.5, 'Dados insuficientes\npara evolução temporal', 
                         ha='center', va='center', fontsize=12)
        ax_evolution.set_xlim(0, 1)
        ax_evolution.set_ylim(0, 1)
        ax_evolution.axis('off')
    
    # 4. Análise de Distribuição (linha inferior completa)
    ax_dist = fig.add_subplot(gs[2, :])
    
    if top_materiais:
        # Gráfico de pizza com os top materiais
        materiais_pie = [item[0] for item in top_materiais[:6]]  # Top 6
        valores_pie = [item[1] for item in top_materiais[:6]]
        
        # Adicionar "Outros" se houver mais materiais
        if len(top_materiais) > 6:
            outros_valor = sum(item[1] for item in top_materiais[6:])
            materiais_pie.append('Outros')
            valores_pie.append(outros_valor)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(materiais_pie)))
        
        wedges, texts, autotexts = ax_dist.pie(valores_pie, labels=materiais_pie, 
                                              autopct=lambda pct: format_currency(sum(valores_pie) * pct / 100),
                                              colors=colors, startangle=90)
        
        # Melhorar aparência do texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax_dist.set_title('Distribuição de Valor por Material', fontsize=12, fontweight='bold')
    else:
        ax_dist.text(0.5, 0.5, 'Dados não disponíveis para distribuição', 
                    ha='center', va='center', fontsize=12)
        ax_dist.axis('off')
    
    plt.tight_layout()
    
    # Salvar em BytesIO
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer

# Função de teste
def test_enhanced_charts():
    """Testa as funcionalidades do módulo de gráficos."""
    
    # Dados de teste
    test_kpis = {
        'valor_total': 1500000,
        'numero_materiais': 25,
        'quantidade_total': 1200,
        'variacao_mensal': -8.5
    }
    
    test_materiais = [
        ('Material A', 500000),
        ('Material B', 300000),
        ('Material C', 200000),
        ('Material D', 150000),
        ('Material E', 100000)
    ]
    
    test_evolucao = [
        {'mes': 'Jan', 'valor': 1800000},
        {'mes': 'Fev', 'valor': 1650000},
        {'mes': 'Mar', 'valor': 1500000}
    ]
    
    test_analysis = {
        'gerencia': 'Operações',
        'kpis': test_kpis,
        'top_materiais': test_materiais,
        'evolucao_temporal': test_evolucao
    }
    
    print("=== TESTE DO MÓDULO ENHANCED_CHARTS ===")
    
    # Teste 1: KPI Cards
    print("1. Testando KPI Cards...")
    kpi_chart = create_kpi_cards_chart(test_kpis, 'Operações')
    print(f"   ✅ KPI Cards gerado: {len(kpi_chart.getvalue())} bytes")
    
    # Teste 2: Top Materiais
    print("2. Testando Top Materiais...")
    materials_chart = create_top_materials_chart(test_materiais, 'Operações')
    print(f"   ✅ Top Materiais gerado: {len(materials_chart.getvalue())} bytes")
    
    # Teste 3: Evolução Temporal
    print("3. Testando Evolução Temporal...")
    evolution_chart = create_temporal_evolution_chart(test_evolucao, 'Operações')
    print(f"   ✅ Evolução Temporal gerado: {len(evolution_chart.getvalue())} bytes")
    
    # Teste 4: Dashboard Completo
    print("4. Testando Dashboard Completo...")
    dashboard = create_summary_dashboard(test_analysis)
    print(f"   ✅ Dashboard Completo gerado: {len(dashboard.getvalue())} bytes")
    
    print("\n✅ Todos os gráficos gerados com sucesso!")
    return True

if __name__ == "__main__":
    # Executar teste
    test_enhanced_charts()
    print("\n" + "="*60)
    print("✅ MÓDULO ENHANCED_CHARTS FUNCIONAL!")
    print("="*60)