"""
Módulo de geração de PDF aprimorado para relatórios de estoque excedente por gerência.
Nome do arquivo: pdf.py
"""

from __future__ import annotations

import os
import io
import tempfile
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Imports locais
from charts import generate_all_charts_for_gerencia
from utils.formatting import safe_format_currency, safe_format_number  # <- usa utils

# ---------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------
def setup_fonts() -> tuple[str, str]:
    """
    Configura as fontes para o PDF.
    Retorna (fonte_normal, fonte_bold).
    """
    try:
        font_paths = {
            "DejaVuSans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans-Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
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


def _image_from_buffer(buf: io.BytesIO, tmp_files: List[str], max_w: float, max_h: float) -> Image:
    """
    Converte um BytesIO de imagem em um PNG temporário e devolve um Flowable Image.
    Registra o caminho para remoção posterior.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    tmp.write(buf.getvalue())
    tmp.flush()
    tmp.close()
    tmp_files.append(tmp.name)

    img = Image(tmp.name)
    img._restrictSize(max_w, max_h)
    return img


def _sanitize_filename(name: str) -> str:
    """
    Remove caracteres problemáticos para nome de arquivo.
    Mantém letras, números, espaços, hífen e ponto.
    """
    safe = "".join(c for c in str(name) if c.isalnum() or c in (" ", "-", "."))
    return safe.strip().replace(" ", "_") or "Relatorio"


# ---------------------------------------------------------------------
# Geração de PDF - por gerência
# ---------------------------------------------------------------------
def generate_pdf_for_gerencia(analysis_data: Dict[str, Any], pdf_path: str) -> None:
    """
    Gera um relatório PDF para uma gerência específica.

    Args:
        analysis_data: Dicionário com a análise completa da gerência.
                       Espera chaves: 'gerencia', 'kpis', 'evolucao_mensal',
                       'top_materiais', 'tabela_dados', 'analises_ia'
        pdf_path: Caminho para salvar o PDF.
    """
    tmp_files: List[str] = []

    try:
        # Documento
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
        )
        story: List[Any] = []

        # Estilos
        font_name, bold_font_name = setup_fonts()
        styles = getSampleStyleSheet()

        h1_style = ParagraphStyle(
            name="h1_custom",
            parent=styles["Heading1"],
            fontName=bold_font_name,
            fontSize=22,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
        h2_style = ParagraphStyle(
            name="h2_custom",
            parent=styles["Heading2"],
            fontName=bold_font_name,
            fontSize=16,
            spaceBefore=12,
            spaceAfter=10,
        )
        h3_style = ParagraphStyle(
            name="h3_custom",
            parent=styles["Heading3"],
            fontName=bold_font_name,
            fontSize=13,
            spaceBefore=8,
            spaceAfter=6,
        )
        normal_style = ParagraphStyle(
            name="normal_custom",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
        )

        gerencia = analysis_data.get("gerencia", "Desconhecida")

        # -----------------------------------------------------------------
        # Capa
        # -----------------------------------------------------------------
        story.append(Paragraph("Relatório de Estoque Excedente", h1_style))
        story.append(Paragraph(f"Gerência: {gerencia}", h2_style))
        story.append(Spacer(1, 0.6 * inch))
        data_atual = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Data de Geração: {data_atual}", normal_style))
        story.append(PageBreak())

        # -----------------------------------------------------------------
        # Seção 1 – Visão Geral e KPIs
        # -----------------------------------------------------------------
        story.append(Paragraph("1. Visão Geral e KPIs", h2_style))

        charts = generate_all_charts_for_gerencia(analysis_data)

        if charts.get("kpis"):
            story.append(_image_from_buffer(charts["kpis"], tmp_files, 7 * inch, 4.5 * inch))
            story.append(Spacer(1, 0.2 * inch))

        if charts.get("evolucao_mensal"):
            story.append(Paragraph("Evolução Mensal do Estoque Excedente", h3_style))
            story.append(_image_from_buffer(charts["evolucao_mensal"], tmp_files, 7 * inch, 3.5 * inch))
            story.append(Spacer(1, 0.2 * inch))

        if charts.get("top_materiais"):
            story.append(Paragraph("Top 10 Materiais por Valor", h3_style))
            story.append(_image_from_buffer(charts["top_materiais"], tmp_files, 7 * inch, 4 * inch))

        story.append(PageBreak())

        # -----------------------------------------------------------------
        # Seção 2 – Análises de IA
        # -----------------------------------------------------------------
        story.append(Paragraph("2. Análises de Inteligência Artificial", h2_style))

        ai_data = analysis_data.get("analises_ia", {}) or {}

        # Resumo Executivo (IA)
        resumo_ia = ai_data.get("resumo_executivo", {})
        if isinstance(resumo_ia, dict) and resumo_ia.get("status") == "sucesso":
            story.append(Paragraph("Resumo Executivo (IA)", h3_style))
            resumo_text = str(resumo_ia.get("resumo", "")).replace("\n", "<br/>")
            story.append(Paragraph(resumo_text, normal_style))
            story.append(Spacer(1, 0.2 * inch))

        # Gráficos gerados de IA (se existirem no dicionário charts)
        if charts.get("previsao"):
            story.append(Paragraph("Análise Preditiva", h3_style))
            story.append(_image_from_buffer(charts["previsao"], tmp_files, 7 * inch, 3.5 * inch))
            story.append(Spacer(1, 0.2 * inch))

        if charts.get("anomalias"):
            story.append(Paragraph("Detecção de Anomalias", h3_style))
            story.append(_image_from_buffer(charts["anomalias"], tmp_files, 7 * inch, 3.5 * inch))
            story.append(Spacer(1, 0.2 * inch))

        if charts.get("recomendacoes"):
            story.append(Paragraph("Recomendações de Ações (IA)", h3_style))
            story.append(_image_from_buffer(charts["recomendacoes"], tmp_files, 7 * inch, 4 * inch))

        story.append(PageBreak())

        # -----------------------------------------------------------------
        # Seção 3 – Dados Detalhados
        # -----------------------------------------------------------------
        story.append(Paragraph("3. Tabela de Dados Detalhados", h2_style))

        tabela_dados = analysis_data.get("tabela_dados", [])
        if tabela_dados:
            df_tabela = pd.DataFrame(tabela_dados).copy()

            # Formatação básica de colunas monetárias
            for col in df_tabela.columns:
                if "valor" in str(col).lower():
                    df_tabela[col] = df_tabela[col].apply(safe_format_currency)

            data_list = [df_tabela.columns.tolist()] + df_tabela.values.tolist()
            table = Table(data_list, repeatRows=1)

            style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), bold_font_name),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F7F7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
            table.setStyle(style)
            story.append(table)
        else:
            story.append(Paragraph("Nenhum dado detalhado para exibir.", normal_style))

        # Constrói o PDF
        doc.build(story)

    except Exception as e:
        raise Exception(f"Erro ao gerar PDF para {analysis_data.get('gerencia', 'Desconhecida')}: {e}")

    finally:
        # Limpeza de arquivos temporários
        for f in tmp_files:
            try:
                os.remove(f)
            except Exception:
                pass


# ---------------------------------------------------------------------
# Geração em lote
# ---------------------------------------------------------------------
def generate_all_pdfs(all_analysis_data: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Gera PDFs para todas as gerências e os salva em um diretório.

    Args:
        all_analysis_data: Dicionário com análises de todas as gerências.
                           Espera um mapeamento em all_analysis_data["analises"].
        output_dir: Diretório para salvar os PDFs.

    Returns:
        Lista com os caminhos dos PDFs gerados.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        pdf_paths: List[str] = []
        analises: Dict[str, Dict[str, Any]] = all_analysis_data.get("analises", {}) or {}

        for gerencia, analysis_data in analises.items():
            if (analysis_data or {}).get("status") == "sucesso":
                safe_name = _sanitize_filename(gerencia)
                pdf_filename = f"Relatorio_Estoque_{safe_name}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                generate_pdf_for_gerencia(analysis_data, pdf_path)
                pdf_paths.append(pdf_path)

        return pdf_paths

    except Exception as e:
        raise Exception(f"Erro ao gerar todos os PDFs: {e}")
