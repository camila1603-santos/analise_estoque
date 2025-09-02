"""
Módulo de geração de PDF aprimorado para relatórios de estoque excedente por gerência.
"""

import pandas as pd
from typing import Any, Callable, Dict, Optional, List
import os
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# Importações locais
from enhanced_charts import generate_all_charts_for_gerencia

# Configuração de fontes
def setup_fonts():
    """Configura as fontes para o PDF."""
    try:
        # Tentar registrar fontes comuns
        font_paths = {
            "DejaVuSans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans-Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        }
        
        font_registered = False
        for name, path in font_paths.items():
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                font_registered = True
        
        if font_registered:
            return "DejaVuSans", "DejaVuSans-Bold"
        else:
            return "Helvetica", "Helvetica-Bold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"

# Formatação segura
def safe_format_currency(value: Any) -> str:
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def safe_format_number(value: Any) -> str:
    try:
        return f"{int(value):,}".replace(",", ".")
    except:
        return "0"

# Função principal de geração de PDF
def generate_pdf_for_gerencia(analysis_data: Dict[str, Any], pdf_path: str):
    """
    Gera um relatório PDF para uma gerência específica.
    
    Args:
        analysis_data: Dicionário com a análise completa da gerência
        pdf_path: Caminho para salvar o PDF
    """
    try:
        # Configurar documento
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Configurar fontes e estilos
        font_name, bold_font_name = setup_fonts()
        styles = getSampleStyleSheet()
        
        h1_style = ParagraphStyle(
            name='h1_custom', parent=styles["Heading1"], fontName=bold_font_name, 
            fontSize=22, alignment=TA_CENTER, spaceAfter=18
        )
        h2_style = ParagraphStyle(
            name='h2_custom', parent=styles["Heading2"], fontName=bold_font_name, 
            fontSize=16, spaceBefore=12, spaceAfter=10
        )
        normal_style = ParagraphStyle(
            name='normal_custom', parent=styles["Normal"], fontName=font_name, 
            fontSize=10, leading=14
        )
        
        gerencia = analysis_data.get("gerencia", "Desconhecida")
        
        # --- Página de Título ---
        story.append(Paragraph(f"Relatório de Estoque Excedente", h1_style))
        story.append(Paragraph(f"Gerência: {gerencia}", styles["h2"]))
        story.append(Spacer(1, 1*inch))
        data_atual = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Data de Geração: {data_atual}", normal_style))
        story.append(PageBreak())
        
        # --- Seção de KPIs e Visão Geral ---
        story.append(Paragraph("1. Visão Geral e KPIs", h2_style))
        
        # Gerar gráficos
        charts = generate_all_charts_for_gerencia(analysis_data)
        
        if 'kpis' in charts:
            story.append(Image(charts['kpis'], width=7*inch, height=4.5*inch))
            story.append(Spacer(1, 0.2*inch))
        
        if 'evolucao_mensal' in charts:
            story.append(Paragraph("Evolução Mensal do Estoque Excedente", styles["h3"]))
            story.append(Image(charts['evolucao_mensal'], width=7*inch, height=3.5*inch))
            story.append(Spacer(1, 0.2*inch))
        
        if 'top_materiais' in charts:
            story.append(Paragraph("Top 10 Materiais por Valor", styles["h3"]))
            story.append(Image(charts['top_materiais'], width=7*inch, height=4*inch))
        
        story.append(PageBreak())
        
        # --- Seção de Análises de IA ---
        story.append(Paragraph("2. Análises de Inteligência Artificial", h2_style))
        
        ai_data = analysis_data.get("analises_ia", {})
        
        # Resumo em Linguagem Natural
        resumo_ia = ai_data.get("resumo_executivo", {})
        if resumo_ia.get("status") == "sucesso":
            story.append(Paragraph("Resumo Executivo (IA)", styles["h3"]))
            resumo_text = resumo_ia.get("resumo", "").replace("\n", "<br/>")
            story.append(Paragraph(resumo_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Análise Preditiva
        if 'previsao' in charts:
            story.append(Paragraph("Análise Preditiva", styles["h3"]))
            story.append(Image(charts['previsao'], width=7*inch, height=3.5*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Detecção de Anomalias
        if 'anomalias' in charts:
            story.append(Paragraph("Detecção de Anomalias", styles["h3"]))
            story.append(Image(charts['anomalias'], width=7*inch, height=3.5*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Análise Prescritiva
        if 'recomendacoes' in charts:
            story.append(Paragraph("Recomendações de Ações (IA)", styles["h3"]))
            story.append(Image(charts['recomendacoes'], width=7*inch, height=4*inch))
        
        story.append(PageBreak())
        
        # --- Seção de Dados Detalhados ---
        story.append(Paragraph("3. Tabela de Dados Detalhados", h2_style))
        
        tabela_dados = analysis_data.get("tabela_dados", [])
        if tabela_dados:
            df_tabela = pd.DataFrame(tabela_dados)
            
            # Formatar colunas de valor
            for col in df_tabela.columns:
                if 'valor' in col.lower():
                    df_tabela[col] = df_tabela[col].apply(safe_format_currency)
            
            # Converter para lista de listas
            data_list = [df_tabela.columns.tolist()] + df_tabela.values.tolist()
            
            # Criar tabela
            table = Table(data_list, repeatRows=1)
            
            # Estilo da tabela
            style = TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), bold_font_name),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ])
            table.setStyle(style)
            
            story.append(table)
        else:
            story.append(Paragraph("Nenhum dado detalhado para exibir.", normal_style))
        
        # Construir o PDF
        doc.build(story)
        
    except Exception as e:
        raise Exception(f"Erro ao gerar PDF para {gerencia}: {e}")

def generate_all_pdfs(all_analysis_data: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Gera PDFs para todas as gerências e os salva em um diretório.
    
    Args:
        all_analysis_data: Dicionário com análises de todas as gerências
        output_dir: Diretório para salvar os PDFs
    
    Returns:
        Lista com os caminhos dos PDFs gerados
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        pdf_paths = []
        
        analises = all_analysis_data.get("analises", {})
        for gerencia, analysis_data in analises.items():
            if analysis_data.get("status") == "sucesso":
                # Sanitize filename
                safe_gerencia_name = "".join(c for c in gerencia if c.isalnum() or c in (".", "-")).rstrip()
                pdf_filename = f"Relatorio_Estoque_{safe_gerencia_name}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                
                generate_pdf_for_gerencia(analysis_data, pdf_path)
                pdf_paths.append(pdf_path)
        
        return pdf_paths
        
    except Exception as e:
        raise Exception(f"Erro ao gerar todos os PDFs: {e}")


