"""
Módulo de geração de gráficos para análise de estoque excedente.
Inclui visualizações específicas para dashboards por gerência.
"""

from typing import Dict, List, Any, Optional, Tuple
import io
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns

# >>> Importa formatações padronizadas dos utils
from utils.formatting import (
    format_currency_compact,  # R$ 1.2K / R$ 3.4M
    safe_format_number,       # 1.234.567
)

warnings.filterwarnings('ignore')

# ----------------------------------------------------------------------
# Configurações globais
# ----------------------------------------------------------------------
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def setup_plot_style():
    """Configura estilo padrão para os gráficos."""
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams.update({
        'font.size': 10,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16
    })

# Alias local para manter o nome curto existente no código
def format_currency(value: float) -> str:
    return format_currency_compact(value)

# ----------------------------------------------------------------------
# Gráfico: KPI Cards
# ----------------------------------------------------------------------
def create_kpi_cards_chart(kpis: Dict[str, Any], gerencia: str) -> Optional[io.BytesIO]:
    """Cria cards com KPIs principais."""
    try:
        setup_plot_style()

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'KPIs Principais - {gerencia}', fontsize=16, fontweight='bold')

        # 1) Valor Total
        ax1 = axes[0, 0]
        ax1.text(0.5, 0.7, 'Valor Total', ha='center', va='center', fontsize=14, fontweight='bold')
        ax1.text(0.5, 0.3, format_currency(kpis.get('valor_total', 0)),
                 ha='center', va='center', fontsize=20, color='#1f77b4', fontweight='bold')
        ax1.set_xlim(0, 1); ax1.set_ylim(0, 1); ax1.axis('off')
        ax1.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2,
                                edgecolor='#1f77b4', facecolor='#e6f3ff', alpha=0.3))

        # 2) Materiais
        ax2 = axes[0, 1]
        ax2.text(0.5, 0.7, 'Materiais', ha='center', va='center', fontsize=14, fontweight='bold')
        ax2.text(0.5, 0.3, safe_format_number(kpis.get('numero_materiais', 0)),
                 ha='center', va='center', fontsize=20, color='#ff7f0e', fontweight='bold')
        ax2.set_xlim(0, 1); ax2.set_ylim(0, 1); ax2.axis('off')
        ax2.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2,
                                edgecolor='#ff7f0e', facecolor='#fff2e6', alpha=0.3))

        # 3) Quantidade
        ax3 = axes[1, 0]
        ax3.text(0.5, 0.7, 'Quantidade', ha='center', va='center', fontsize=14, fontweight='bold')
        ax3.text(0.5, 0.3, safe_format_number(kpis.get('quantidade_total', 0)),
                 ha='center', va='center', fontsize=20, color='#2ca02c', fontweight='bold')
        ax3.set_xlim(0, 1); ax3.set_ylim(0, 1); ax3.axis('off')
        ax3.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2,
                                edgecolor='#2ca02c', facecolor='#e6ffe6', alpha=0.3))

        # 4) Variação Mensal
        ax4 = axes[1, 1]
        variacao = float(kpis.get('variacao_mensal', 0) or 0)
        cor_variacao = '#d62728' if variacao > 0 else '#2ca02c'
        sinal = '+' if variacao > 0 else ''
        ax4.text(0.5, 0.7, 'Variação Mensal', ha='center', va='center', fontsize=14, fontweight='bold')
        ax4.text(0.5, 0.3, f"{sinal}{variacao:.1f}%",
                 ha='center', va='center', fontsize=20, color=cor_variacao, fontweight='bold')
        ax4.set_xlim(0, 1); ax4.set_ylim(0, 1); ax4.axis('off')
        ax4.add_patch(Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2,
                                edgecolor=cor_variacao, facecolor=('#ffe6e6' if variacao > 0 else '#e6ffe6'), alpha=0.3))

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        print(f"Erro ao criar gráfico de KPIs: {e}")
        plt.close('all')
        return None

# ----------------------------------------------------------------------
# Gráfico: Top Materiais
# ----------------------------------------------------------------------
def create_top_materials_chart(top_materiais: List[Tuple[str, float]], gerencia: str) -> Optional[io.BytesIO]:
    """Cria gráfico de barras dos Top Materiais por valor."""
    try:
        setup_plot_style()

        if not top_materiais:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Nenhum material encontrado', ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
            plt.title(f'Top Materiais por Valor - {gerencia}')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0); plt.close(fig)
            return buf

        items = top_materiais[:10]
        materiais = [m for m, _ in items]
        valores = [float(v) for _, v in items]

        fig, ax = plt.subplots(figsize=(12, 8))
        colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(materiais)))
        bars = ax.barh(materiais, valores, color=colors)

        for bar, valor in zip(bars, valores):
            width = bar.get_width()
            ax.text(width + max(valores)*0.01, bar.get_y()+bar.get_height()/2,
                    format_currency(valor), ha='left', va='center', fontweight='bold')

        ax.set_xlabel('Valor (R$)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Material',   fontsize=12, fontweight='bold')
        ax.set_title(f'Top {len(materiais)} Materiais por Valor - {gerencia}', fontsize=14, fontweight='bold', pad=20)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        ax.invert_yaxis()

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        print(f"Erro ao criar gráfico de Top Materiais: {e}")
        plt.close('all')
        return None

# ----------------------------------------------------------------------
# Gráfico: Evolução Mensal (corrigido com eixo numérico)
# ----------------------------------------------------------------------
def create_monthly_evolution_chart(evolucao: List[Dict[str, Any]], gerencia: str) -> Optional[io.BytesIO]:
    """
    Gera o gráfico de evolução mensal. Espera lista de dicts:
    [{"mes":"01","valor":12345.0}, ...]
    """
    try:
        setup_plot_style()
        if not evolucao:
            return None

        meses   = [str(item.get("mes", "")) for item in evolucao]
        valores = [float(item.get("valor", item.get("valor_total", 0.0))) for item in evolucao]

        x = np.arange(len(meses))  # X numérico evita erro do fill_between
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(x, valores, marker='o', linewidth=2.5, markersize=6)
        ax.fill_between(x, valores, alpha=0.25)

        for i, (mes, val) in enumerate(zip(meses, valores)):
            ax.annotate(format_currency(val), (i, val), textcoords="offset points",
                        xytext=(0, 8), ha='center', fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

        ax.set_xlabel('Período')
        ax.set_ylabel('Valor do Estoque Excedente')
        ax.set_title(f'Evolução Mensal - {gerencia}')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: format_currency(v)))

        ax.set_xticks(x)
        ax.set_xticklabels(meses, rotation=45 if len(meses) > 6 else 0)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf
    except Exception as e:
        print(f"Erro ao criar gráfico de evolução mensal: {e}")
        plt.close('all')
        return None

# ----------------------------------------------------------------------
# Dashboard resumo (opcional; usado na app)
# ----------------------------------------------------------------------
def create_summary_dashboard(analysis_data: Dict[str, Any]) -> Optional[io.BytesIO]:
    """
    Cria um painel resumo em uma única imagem.
    Espera chaves: 'gerencia', 'kpis', 'top_materiais', 'evolucao_mensal'
    """
    try:
        setup_plot_style()

        gerencia = analysis_data.get('gerencia', 'N/A')
        kpis = analysis_data.get('kpis', {})
        top_materiais = analysis_data.get('top_materiais', [])
        evolucao = analysis_data.get('evolucao_mensal', []) or analysis_data.get('evolucao_temporal', [])

        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.5, 1.5], hspace=0.3, wspace=0.3)
        fig.suptitle(f'Dashboard Completo - {gerencia}', fontsize=20, fontweight='bold', y=0.95)

        # 1) KPIs
        ax_kpis = fig.add_subplot(gs[0, :])
        kpi_names = ['Valor Total', 'Materiais', 'Quantidade', 'Variação %']
        kpi_values = [
            format_currency(kpis.get('valor_total', 0)),
            safe_format_number(kpis.get('numero_materiais', 0)),
            safe_format_number(kpis.get('quantidade_total', 0)),
            f"{float(kpis.get('variacao_mensal', 0) or 0):+.1f}%"
        ]
        kpi_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728' if float(kpis.get('variacao_mensal', 0) or 0) > 0 else '#2ca02c']
        for i, (name, value, color) in enumerate(zip(kpi_names, kpi_values, kpi_colors)):
            x_pos = i * 0.25 + 0.125
            rect = Rectangle((x_pos - 0.1, 0.2), 0.2, 0.6, linewidth=2, edgecolor=color, facecolor=color, alpha=0.1)
            ax_kpis.add_patch(rect)
            ax_kpis.text(x_pos, 0.7, name,  ha='center', va='center', fontsize=10, fontweight='bold')
            ax_kpis.text(x_pos, 0.4, value, ha='center', va='center', fontsize=14, fontweight='bold', color=color)
        ax_kpis.set_xlim(0, 1); ax_kpis.set_ylim(0, 1); ax_kpis.axis('off')

        # 2) Top Materiais
        ax_materials = fig.add_subplot(gs[1, 0])
        if top_materiais:
            items = top_materiais[:8]
            materiais = [m for m, _ in items]
            valores = [float(v) for _, v in items]
            colors = plt.cm.Set3(np.linspace(0, 1, len(materiais)))
            bars = ax_materials.barh(materiais, valores, color=colors)
            for bar, valor in zip(bars, valores):
                width = bar.get_width()
                ax_materials.text(width + max(valores) * 0.02, bar.get_y() + bar.get_height()/2,
                                  format_currency(valor), ha='left', va='center', fontsize=9)
            ax_materials.set_xlabel('Valor (R$)', fontsize=10)
            ax_materials.set_title('Top Materiais por Valor', fontsize=12, fontweight='bold')
            ax_materials.invert_yaxis()
            ax_materials.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        else:
            ax_materials.text(0.5, 0.5, 'Dados não disponíveis', ha='center', va='center')
            ax_materials.set_xlim(0, 1); ax_materials.set_ylim(0, 1); ax_materials.axis('off')

        # 3) Evolução Mensal
        ax_evolution = fig.add_subplot(gs[1, 1])
        if evolucao and len(evolucao) > 1:
            meses = [str(item.get('mes', '')) for item in evolucao]
            valores = [float(item.get('valor', item.get('valor_total', 0.0))) for item in evolucao]
            x = np.arange(len(meses))
            ax_evolution.plot(x, valores, marker='o', linewidth=2, markersize=6, color='#1f77b4')
            ax_evolution.fill_between(x, valores, alpha=0.3, color='#1f77b4')
            ax_evolution.set_xlabel('Período', fontsize=10)
            ax_evolution.set_ylabel('Valor (R$)', fontsize=10)
            ax_evolution.set_title('Evolução Mensal', fontsize=12, fontweight='bold')
            ax_evolution.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
            ax_evolution.set_xticks(x); ax_evolution.set_xticklabels(meses, rotation=45 if len(meses) > 6 else 0)
            ax_evolution.grid(True, alpha=0.3)
        else:
            ax_evolution.text(0.5, 0.5, 'Dados insuficientes\npara evolução mensal', ha='center', va='center', fontsize=12)
            ax_evolution.set_xlim(0, 1); ax_evolution.set_ylim(0, 1); ax_evolution.axis('off')

        # 4) Pizza de distribuição (opcional)
        ax_dist = fig.add_subplot(gs[2, :])
        if top_materiais:
            items = top_materiais[:6]
            materiais_pie = [m for m, _ in items]
            valores_pie = [float(v) for _, v in items]
            if len(top_materiais) > 6:
                outros = sum(float(v) for _, v in top_materiais[6:])
                materiais_pie.append('Outros'); valores_pie.append(outros)
            colors = plt.cm.Set3(np.linspace(0, 1, len(materiais_pie)))
            wedges, texts, autotexts = ax_dist.pie(
                valores_pie,
                labels=materiais_pie,
                autopct=lambda pct: format_currency(sum(valores_pie)*pct/100),
                colors=colors,
                startangle=90
            )
            for autotext in autotexts:
                autotext.set_color('white'); autotext.set_fontweight('bold'); autotext.set_fontsize(9)
            ax_dist.set_title('Distribuição de Valor por Material', fontsize=12, fontweight='bold')
        else:
            ax_dist.text(0.5, 0.5, 'Dados não disponíveis para distribuição', ha='center', va='center', fontsize=12)
            ax_dist.axis('off')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf

    except Exception as e:
        print(f"Erro ao criar dashboard resumo: {e}")
        plt.close('all')
        return None

# ----------------------------------------------------------------------
# Fábrica de gráficos por gerência (usada pelo PDF)
# ----------------------------------------------------------------------
def generate_all_charts_for_gerencia(analysis_data: Dict[str, Any]) -> Dict[str, io.BytesIO]:
    """
    Gera todos os gráficos necessários para o PDF de uma gerência.
    Espera as chaves: 'gerencia', 'kpis', 'evolucao_mensal', 'top_materiais'
    Retorna: {'kpis': BytesIO, 'evolucao_mensal': BytesIO, 'top_materiais': BytesIO}
    """
    charts: Dict[str, io.BytesIO] = {}
    gerencia = analysis_data.get('gerencia', 'N/A')

    kpi_chart = create_kpi_cards_chart(analysis_data.get('kpis', {}), gerencia)
    if kpi_chart:
        charts['kpis'] = kpi_chart

    monthly_chart = create_monthly_evolution_chart(analysis_data.get('evolucao_mensal', []), gerencia)
    if monthly_chart:
        charts['evolucao_mensal'] = monthly_chart

    top_chart = create_top_materials_chart(analysis_data.get('top_materiais', []), gerencia)
    if top_chart:
        charts['top_materiais'] = top_chart

    return charts