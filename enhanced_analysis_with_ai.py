"""
Versão aprimorada do enhanced_analysis.py com IA Generativa integrada.
Este arquivo demonstra como integrar a IA Generativa ao código existente.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar a IA Generativa inteligente
from ai_generative_smart_templates import generate_ai_insights_enhanced

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

def calculate_gerencia_kpis(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Calcula KPIs específicos para uma gerência.
    """
    try:
        # Filtrar dados da gerência
        df_gerencia = df[df['Gerência'] == gerencia].copy()
        
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
            # Usar a última coluna de mês como valor atual
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

def generate_enhanced_analysis_with_ai(df: pd.DataFrame, gerencia: str) -> Dict[str, Any]:
    """
    Gera análise completa para uma gerência incluindo IA Generativa.
    
    Esta é a função principal que combina análises tradicionais com IA.
    """
    
    try:
        # 1. Calcular KPIs básicos
        kpis = calculate_gerencia_kpis(df, gerencia)
        
        # 2. Gerar insights de IA Generativa
        ai_insights = generate_ai_insights_enhanced(kpis, gerencia)
        
        # 3. Compilar resultado completo
        analysis_result = {
            "gerencia": gerencia,
            "kpis": kpis,
            "ai_generativa": ai_insights,
            "timestamp": datetime.now().isoformat(),
            "enhanced_with_ai": True,
            "versao": "MVP_com_IA_Generativa_v1.0"
        }
        
        return analysis_result
        
    except Exception as e:
        return {
            "gerencia": gerencia,
            "erro": f"Erro na análise: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "enhanced_with_ai": False
        }

def generate_all_gerencias_analysis_with_ai(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera análise completa para todas as gerências com IA Generativa.
    """
    
    gerencias = get_unique_gerencias(df)
    
    if not gerencias:
        return {
            "erro": "Nenhuma gerência encontrada no dataset",
            "timestamp": datetime.now().isoformat()
        }
    
    results = {}
    
    for gerencia in gerencias:
        print(f"Processando {gerencia} com IA Generativa...")
        results[gerencia] = generate_enhanced_analysis_with_ai(df, gerencia)
    
    # Adicionar resumo geral
    total_valor = sum(r.get('kpis', {}).get('valor_total', 0) for r in results.values())
    total_materiais = sum(r.get('kpis', {}).get('numero_materiais', 0) for r in results.values())
    
    summary = {
        "total_gerencias": len(gerencias),
        "valor_total_organizacao": total_valor,
        "total_materiais_organizacao": total_materiais,
        "gerencias_processadas": list(gerencias),
        "timestamp": datetime.now().isoformat(),
        "ia_generativa_ativa": True
    }
    
    return {
        "summary": summary,
        "gerencias": results
    }

# Exemplo de uso
if __name__ == "__main__":
    # Simular dados para teste
    print("=== TESTE DE ANÁLISE COMPLETA COM IA GENERATIVA ===")
    
    # Dados de exemplo
    sample_data = {
        'Gerência': ['Operações', 'Operações', 'Qualidade', 'Qualidade'],
        'Material': ['M001', 'M002', 'M003', 'M004'],
        'Quantidade': [100, 200, 50, 75],
        'Valor Mês 01': [100000, 200000, 50000, 75000],
        'Valor Mês 12': [80000, 180000, 45000, 70000]
    }
    
    df_test = pd.DataFrame(sample_data)
    
    # Testar análise para uma gerência
    result_operacoes = generate_enhanced_analysis_with_ai(df_test, 'Operações')
    
    print(f"Gerência: {result_operacoes['gerencia']}")
    print(f"Valor Total: R$ {result_operacoes['kpis']['valor_total']:,.2f}")
    print(f"Variação: {result_operacoes['kpis']['variacao_mensal']:.1f}%")
    print(f"IA Status: {result_operacoes['ai_generativa']['status']}")
    print(f"\nResumo IA:")
    print(result_operacoes['ai_generativa']['resumo_executivo'])
    print(f"\nRecomendações IA:")
    for i, rec in enumerate(result_operacoes['ai_generativa']['recomendacoes'], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "="*60)
    print("✅ IA GENERATIVA INTEGRADA COM SUCESSO!")
    print("✅ FUNCIONALIDADE PRONTA PARA DEMONSTRAÇÃO!")
    print("="*60)

