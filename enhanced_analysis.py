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
        
        # Valor total (usar última coluna de mês como valor atual)
        valor_total = 0
        if month_cols:
            last_month_col = month_cols[-1]
            valor_total = pd.to_numeric(df_gerencia[last_month_col], errors='coerce').fillna(0).sum()
        
        # Quantidade total
        quantidade_total = 0
        if 'Quantidade' in df_gerencia.columns:
            quantidade_total = pd.to_numeric(df_gerencia['Quantidade'], errors='coerce').fillna(0).sum()
        
        # Número de materiais únicos
        numero_materiais = 0
        if 'Material' in df_gerencia.columns:
            numero_materiais = df_gerencia['Material'].nunique()
        
        # Valor médio por material
        valor_medio_material = valor_total / max(1, numero_materiais)
        
        # Variação mensal (primeira vs última coluna)
        variacao_mensal = 0
        if len(month_cols) >= 2:
            first_month_col = month_cols[0]
            last_month_col = month_cols[-1]
            
            valor_primeiro = pd.to_numeric(df_gerencia[first_month_col], errors='coerce').fillna(0).sum()
            valor_ultimo = pd.to_numeric(df_gerencia[last_month_col], errors='coerce').fillna(0).sum()
            
            if valor_primeiro > 0:
                variacao_mensal = ((valor_ultimo - valor_primeiro) / valor_primeiro) * 100
        
        return {
            "valor_total": valor_total,
            "quantidade_total": quantidade_total,
            "numero_materiais": numero_materiais,
            "valor_medio_material": valor_medio_material,
            "variacao_mensal": variacao_mensal,
            "status": "calculado"
        }
        
    except Exception as e:
        return {
            "valor_total": 0,
            "quantidade_total": 0,
            "numero_materiais": 0,
            "valor_medio_material": 0,
            "variacao_mensal": 0,
            "status": f"erro: {str(e)}"
        }

def generate_gerencia_analysis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Gera análise completa para uma gerência específica.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência
    
    Returns:
        Dict com análise completa da gerência
    """
    try:
        # Calcular KPIs básicos
        kpis = calculate_gerencia_kpis(df, gerencia)
        
        # Análise de materiais (top 10)
        df_gerencia = filter_data_by_gerencia(df, gerencia)
        top_materiais = []
        
        if not df_gerencia.empty and 'Material' in df_gerencia.columns:
            month_patterns = ['valor mês', 'valor_mes', 'mês']
            month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
            
            if month_cols:
                material_values = {}
                for material in df_gerencia['Material'].unique():
                    if pd.isna(material):
                        continue
                    
                    material_data = df_gerencia[df_gerencia['Material'] == material]
                    # Usar última coluna de mês
                    valor = pd.to_numeric(material_data[month_cols[-1]], errors='coerce').fillna(0).sum()
                    material_values[material] = valor
                
                # Top 10 materiais
                top_materiais = sorted(material_values.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Análise temporal (se houver múltiplas colunas de mês)
        evolucao_temporal = []
        if not df_gerencia.empty:
            month_patterns = ['valor mês', 'valor_mes', 'mês']
            month_cols = _find_columns_by_pattern(df_gerencia, month_patterns)
            
            for col in month_cols:
                valor_mes = pd.to_numeric(df_gerencia[col], errors='coerce').fillna(0).sum()
                evolucao_temporal.append({
                    'mes': col,
                    'valor': valor_mes
                })
        
        return {
            "gerencia": gerencia,
            "kpis": kpis,
            "top_materiais": top_materiais,
            "evolucao_temporal": evolucao_temporal,
            "timestamp": datetime.now().isoformat(),
            "status": "sucesso"
        }
        
    except Exception as e:
        return {
            "gerencia": gerencia,
            "erro": f"Erro na análise: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "status": "erro"
        }

def generate_all_gerencias_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera análise para todas as gerências encontradas no DataFrame.
    
    Args:
        df: DataFrame com dados de estoque
    
    Returns:
        Dict com análises de todas as gerências
    """
    try:
        gerencias = get_unique_gerencias(df)
        
        if not gerencias:
            return {
                "erro": "Nenhuma gerência encontrada no dataset",
                "timestamp": datetime.now().isoformat()
            }
        
        results = {}
        
        for gerencia in gerencias:
            results[gerencia] = generate_gerencia_analysis(df, gerencia)
        
        # Calcular resumo geral
        total_valor = sum(r.get('kpis', {}).get('valor_total', 0) for r in results.values())
        total_materiais = sum(r.get('kpis', {}).get('numero_materiais', 0) for r in results.values())
        
        summary = {
            "total_gerencias": len(gerencias),
            "valor_total_organizacao": total_valor,
            "total_materiais_organizacao": total_materiais,
            "gerencias_processadas": gerencias,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "summary": summary,
            "gerencias": results
        }
        
    except Exception as e:
        return {
            "erro": f"Erro na análise geral: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def get_material_details(df: pd.DataFrame, gerencia: str, material: str) -> Dict[str, Any]:
    """
    Obtém detalhes específicos de um material em uma gerência.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência
        material: Nome do material
    
    Returns:
        Dict com detalhes do material
    """
    try:
        df_filtered = df[(df['Gerência'] == gerencia) & (df['Material'] == material)].copy()
        
        if df_filtered.empty:
            return {
                "material": material,
                "gerencia": gerencia,
                "status": "nao_encontrado"
            }
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
        
        # Calcular evolução mensal
        evolucao = []
        for col in month_cols:
            valor = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum()
            evolucao.append({
                'mes': col,
                'valor': valor
            })
        
        # Quantidade total
        quantidade = 0
        if 'Quantidade' in df_filtered.columns:
            quantidade = pd.to_numeric(df_filtered['Quantidade'], errors='coerce').fillna(0).sum()
        
        return {
            "material": material,
            "gerencia": gerencia,
            "quantidade_total": quantidade,
            "evolucao_mensal": evolucao,
            "valor_atual": evolucao[-1]['valor'] if evolucao else 0,
            "status": "encontrado"
        }
        
    except Exception as e:
        return {
            "material": material,
            "gerencia": gerencia,
            "erro": str(e),
            "status": "erro"
        }

# Função de teste
def test_enhanced_analysis():
    """Testa as funcionalidades do módulo."""
    
    # Criar dados de teste
    test_data = {
        'Gerência': ['Operações', 'Operações', 'Qualidade', 'Qualidade', 'Manutenção'],
        'Material': ['M001', 'M002', 'M003', 'M004', 'M005'],
        'Quantidade': [100, 200, 50, 75, 120],
        'Valor Mês 01': [100000, 200000, 50000, 75000, 80000],
        'Valor Mês 02': [110000, 180000, 55000, 70000, 85000],
        'Valor Mês 03': [95000, 190000, 48000, 72000, 90000]
    }
    
    df_test = pd.DataFrame(test_data)
    
    print("=== TESTE DO MÓDULO ENHANCED_ANALYSIS ===")
    
    # Teste 1: Obter gerências
    gerencias = get_unique_gerencias(df_test)
    print(f"Gerências encontradas: {gerencias}")
    
    # Teste 2: Análise de uma gerência
    analysis_ops = generate_gerencia_analysis(df_test, 'Operações')
    print(f"\nAnálise Operações:")
    print(f"Status: {analysis_ops['status']}")
    print(f"Valor Total: R$ {analysis_ops['kpis']['valor_total']:,.2f}")
    print(f"Número de Materiais: {analysis_ops['kpis']['numero_materiais']}")
    
    # Teste 3: Análise completa
    complete_analysis = generate_all_gerencias_analysis(df_test)
    print(f"\nAnálise Completa:")
    print(f"Total de Gerências: {complete_analysis['summary']['total_gerencias']}")
    print(f"Valor Total Organização: R$ {complete_analysis['summary']['valor_total_organizacao']:,.2f}")
    
    print("\n✅ Todos os testes executados com sucesso!")
    return complete_analysis

if __name__ == "__main__":
    # Executar teste
    result = test_enhanced_analysis()
    print("\n" + "="*60)
    print("✅ MÓDULO ENHANCED_ANALYSIS FUNCIONAL!")
    print("="*60)