"""
Módulo de análise aprimorada para gestão de estoque excedente por gerência.
Integra análises tradicionais com funcionalidades de IA.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar módulos existentes
from ai_analysis import comprehensive_ai_analysis

def _find_columns_by_pattern(df: pd.DataFrame, patterns: List[str]) -> List[str]:
    """Encontra colunas que contêm qualquer um dos padrões fornecidos."""
    found_columns = []
    for col in df.columns:
        for pattern in patterns:
            if pattern.lower() in col.lower():
                found_columns.append(col)
                break
    return found_columns

def get_unique_gerencias(df: pd.DataFrame) -> List[str]:
    """
    Obtém lista de gerências únicas no DataFrame.
    
    Args:
        df: DataFrame com dados de estoque
    
    Returns:
        Lista de nomes de gerências
    """
    try:
        if 'Gerência' not in df.columns:
            return []
        
        gerencias = df['Gerência'].dropna().unique().tolist()
        # Filtrar linhas de total se existirem
        gerencias = [g for g in gerencias if not str(g).lower().startswith('total')]
        return sorted(gerencias)
    except Exception:
        return []

def filter_data_by_gerencia(df: pd.DataFrame, gerencia: str) -> pd.DataFrame:
    """
    Filtra dados por gerência específica.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
    
    Returns:
        DataFrame filtrado
    """
    try:
        if 'Gerência' not in df.columns:
            return pd.DataFrame()
        
        filtered_df = df[df['Gerência'] == gerencia].copy()
        # Remover linhas de total se existirem
        filtered_df = filtered_df[~filtered_df['Gerência'].str.lower().str.startswith('total', na=False)]
        return filtered_df
    except Exception:
        return pd.DataFrame()

def calculate_gerencia_kpis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Calcula KPIs específicos para uma gerência.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
    
    Returns:
        Dict com KPIs da gerência
    """
    try:
        # Filtrar dados da gerência
        df_gerencia = filter_data_by_gerencia(df, gerencia)
        
        if df_gerencia.empty:
            return {
                "valor_total": 0,
                "quantidade_total": 0,
                "numero_materiais": 0,
                "valor_medio_material": 0,
                "variacao_mensal": 0,
                "status": "sem_dados"
            }
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
        
        # Valor total
        valor_total = 0
        if month_cols:
            for col in month_cols:
                valor_total += pd.to_numeric(df_gerencia[col], errors='coerce').fillna(0).sum()
        
        # Quantidade total
        qty_patterns = ['quantidade', 'qtd']
        qty_cols = _find_columns_by_pattern(df_gerencia, qty_patterns)
        quantidade_total = 0
        if qty_cols:
            quantidade_total = pd.to_numeric(df_gerencia[qty_cols[0]], errors='coerce').fillna(0).sum()
        
        # Número de materiais únicos
        numero_materiais = 0
        if 'Material' in df_gerencia.columns:
            numero_materiais = df_gerencia['Material'].nunique()
        
        # Valor médio por material
        valor_medio_material = valor_total / max(1, numero_materiais)
        
        # Variação mensal (último vs primeiro mês)
        variacao_mensal = 0
        if len(month_cols) >= 2:
            primeiro_mes = pd.to_numeric(df_gerencia[month_cols[0]], errors='coerce').fillna(0).sum()
            ultimo_mes = pd.to_numeric(df_gerencia[month_cols[-1]], errors='coerce').fillna(0).sum()
            
            if primeiro_mes > 0:
                variacao_mensal = ((ultimo_mes - primeiro_mes) / primeiro_mes) * 100
        
        return {
            "valor_total": valor_total,
            "quantidade_total": int(quantidade_total),
            "numero_materiais": numero_materiais,
            "valor_medio_material": valor_medio_material,
            "variacao_mensal": variacao_mensal,
            "status": "sucesso"
        }
        
    except Exception as e:
        return {
            "valor_total": 0,
            "quantidade_total": 0,
            "numero_materiais": 0,
            "valor_medio_material": 0,
            "variacao_mensal": 0,
            "status": "erro",
            "erro": str(e)
        }

def get_monthly_evolution(df: pd.DataFrame, gerencia: str) -> pd.DataFrame:
    """
    Obtém evolução mensal dos valores para uma gerência.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
    
    Returns:
        DataFrame com evolução mensal
    """
    try:
        df_gerencia = filter_data_by_gerencia(df, gerencia)
        
        if df_gerencia.empty:
            return pd.DataFrame(columns=['mes', 'valor_total'])
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
        
        if not month_cols:
            return pd.DataFrame(columns=['mes', 'valor_total'])
        
        # Calcular totais mensais
        monthly_data = []
        for i, col in enumerate(month_cols, 1):
            total = pd.to_numeric(df_gerencia[col], errors='coerce').fillna(0).sum()
            monthly_data.append({
                'mes': f'Mês {i:02d}',
                'valor_total': total
            })
        
        return pd.DataFrame(monthly_data)
        
    except Exception:
        return pd.DataFrame(columns=['mes', 'valor_total'])

def get_top_materials(df: pd.DataFrame, gerencia: str, n: int = 10) -> pd.DataFrame:
    """
    Obtém os N materiais com maior valor para uma gerência.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
        n: Número de materiais a retornar
    
    Returns:
        DataFrame com top materiais
    """
    try:
        df_gerencia = filter_data_by_gerencia(df, gerencia)
        
        if df_gerencia.empty or 'Material' not in df_gerencia.columns:
            return pd.DataFrame(columns=['material', 'valor_total'])
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
        
        if not month_cols:
            return pd.DataFrame(columns=['material', 'valor_total'])
        
        # Calcular valor total por material
        material_values = {}
        for material in df_gerencia['Material'].unique():
            if pd.isna(material):
                continue
            
            material_data = df_gerencia[df_gerencia['Material'] == material]
            total_value = 0
            for col in month_cols:
                total_value += pd.to_numeric(material_data[col], errors='coerce').fillna(0).sum()
            
            material_values[material] = total_value
        
        # Ordenar e pegar top N
        top_materials = sorted(material_values.items(), key=lambda x: x[1], reverse=True)[:n]
        
        return pd.DataFrame(top_materials, columns=['material', 'valor_total'])
        
    except Exception:
        return pd.DataFrame(columns=['material', 'valor_total'])

def get_gerencia_data_table(df: pd.DataFrame, gerencia: str) -> pd.DataFrame:
    """
    Obtém tabela de dados formatada para uma gerência.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
    
    Returns:
        DataFrame formatado para exibição
    """
    try:
        df_gerencia = filter_data_by_gerencia(df, gerencia)
        
        if df_gerencia.empty:
            return pd.DataFrame()
        
        # Selecionar colunas relevantes
        display_cols = []
        
        # Colunas básicas
        basic_cols = ['Material', 'Área', 'Quantidade']
        for col in basic_cols:
            if col in df_gerencia.columns:
                display_cols.append(col)
        
        # Colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
        display_cols.extend(month_cols)
        
        # Filtrar apenas colunas que existem
        display_cols = [col for col in display_cols if col in df_gerencia.columns]
        
        if not display_cols:
            return df_gerencia
        
        # Criar DataFrame de exibição
        display_df = df_gerencia[display_cols].copy()
        
        # Formatar valores numéricos
        for col in month_cols:
            if col in display_df.columns:
                display_df[col] = pd.to_numeric(display_df[col], errors='coerce').fillna(0)
        
        return display_df
        
    except Exception:
        return pd.DataFrame()

def comprehensive_gerencia_analysis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Executa análise completa para uma gerência específica.
    
    Args:
        df: DataFrame completo
        gerencia: Nome da gerência
    
    Returns:
        Dict com análise completa da gerência
    """
    try:
        # Análises básicas
        kpis = calculate_gerencia_kpis(df, gerencia)
        monthly_evolution = get_monthly_evolution(df, gerencia)
        top_materials = get_top_materials(df, gerencia, 10)
        data_table = get_gerencia_data_table(df, gerencia)
        
        # Análises de IA
        ai_analysis = comprehensive_ai_analysis(df, gerencia)
        
        # Compilar resultado
        result = {
            "gerencia": gerencia,
            "timestamp": datetime.now().isoformat(),
            "kpis": kpis,
            "evolucao_mensal": monthly_evolution.to_dict('records') if not monthly_evolution.empty else [],
            "top_materiais": top_materials.to_dict('records') if not top_materials.empty else [],
            "tabela_dados": data_table.to_dict('records') if not data_table.empty else [],
            "analises_ia": ai_analysis,
            "status": "sucesso" if kpis.get("status") == "sucesso" else "erro"
        }
        
        return result
        
    except Exception as e:
        return {
            "gerencia": gerencia,
            "timestamp": datetime.now().isoformat(),
            "status": "erro",
            "erro": str(e),
            "kpis": {},
            "evolucao_mensal": [],
            "top_materiais": [],
            "tabela_dados": [],
            "analises_ia": {}
        }

def generate_all_gerencias_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera análise para todas as gerências encontradas no DataFrame.
    
    Args:
        df: DataFrame completo
    
    Returns:
        Dict com análises de todas as gerências
    """
    try:
        gerencias = get_unique_gerencias(df)
        
        if not gerencias:
            return {
                "status": "erro",
                "mensagem": "Nenhuma gerência encontrada nos dados",
                "gerencias": [],
                "analises": {}
            }
        
        analises = {}
        for gerencia in gerencias:
            analises[gerencia] = comprehensive_gerencia_analysis(df, gerencia)
        
        return {
            "status": "sucesso",
            "total_gerencias": len(gerencias),
            "gerencias": gerencias,
            "analises": analises,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao gerar análises: {str(e)}",
            "gerencias": [],
            "analises": {}
        }

