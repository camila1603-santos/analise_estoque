"""
Módulo de análises de IA para gestão de estoque excedente.
Inclui análise preditiva, detecção de anomalias, análise prescritiva e geração de resumos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

def _find_columns_by_pattern(df: pd.DataFrame, patterns: List[str]) -> List[str]:
    """Encontra colunas que contêm qualquer um dos padrões fornecidos."""
    found_columns = []
    for col in df.columns:
        for pattern in patterns:
            if pattern.lower() in col.lower():
                found_columns.append(col)
                break
    return found_columns

def predictive_analysis(df: pd.DataFrame, gerencia: str = None) -> Dict[str, Any]:
    """
    Análise preditiva para prever valores de estoque excedente.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência específica (opcional)
    
    Returns:
        Dict com previsões e métricas
    """
    try:
        # Filtrar por gerência se especificado
        if gerencia:
            df_filtered = df[df['Gerência'] == gerencia].copy()
        else:
            df_filtered = df.copy()
        
        if df_filtered.empty:
            return {
                "status": "erro",
                "mensagem": f"Nenhum dado encontrado para a gerência {gerencia}" if gerencia else "DataFrame vazio",
                "previsoes": [],
                "tendencia": "indefinida"
            }
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
        
        if len(month_cols) < 3:
            return {
                "status": "erro",
                "mensagem": "Dados insuficientes para análise preditiva (mínimo 3 meses)",
                "previsoes": [],
                "tendencia": "indefinida"
            }
        
        # Calcular valores totais mensais
        monthly_values = []
        for col in month_cols:
            total = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum()
            monthly_values.append(total)
        
        # Análise de tendência simples
        if len(monthly_values) >= 2:
            # Calcular tendência linear
            x = np.arange(len(monthly_values))
            y = np.array(monthly_values)
            
            if np.std(y) > 0:  # Verificar se há variação nos dados
                # Regressão linear simples
                slope = np.polyfit(x, y, 1)[0]
                
                # Previsões para próximos 3 meses
                next_months = 3
                predictions = []
                for i in range(1, next_months + 1):
                    pred_value = monthly_values[-1] + (slope * i)
                    predictions.append(max(0, pred_value))  # Não permitir valores negativos
                
                # Determinar tendência
                if slope > monthly_values[-1] * 0.05:  # Crescimento > 5%
                    tendencia = "crescimento"
                elif slope < -monthly_values[-1] * 0.05:  # Decrescimento > 5%
                    tendencia = "decrescimento"
                else:
                    tendencia = "estável"
                
                # Calcular confiança baseada na variabilidade
                variabilidade = np.std(monthly_values) / (np.mean(monthly_values) + 1)
                confianca = max(0.3, min(0.9, 1 - variabilidade))
                
                return {
                    "status": "sucesso",
                    "previsoes": predictions,
                    "tendencia": tendencia,
                    "confianca": confianca,
                    "valores_historicos": monthly_values,
                    "slope": slope,
                    "interpretacao": _interpretar_previsao(predictions, monthly_values[-1], tendencia)
                }
            else:
                return {
                    "status": "aviso",
                    "mensagem": "Valores constantes detectados - sem variação para análise",
                    "previsoes": [monthly_values[-1]] * 3,
                    "tendencia": "estável"
                }
        
        return {
            "status": "erro",
            "mensagem": "Dados insuficientes para análise preditiva",
            "previsoes": [],
            "tendencia": "indefinida"
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro na análise preditiva: {str(e)}",
            "previsoes": [],
            "tendencia": "indefinida"
        }

def _interpretar_previsao(previsoes: List[float], valor_atual: float, tendencia: str) -> str:
    """Interpreta as previsões em linguagem natural."""
    if not previsoes:
        return "Não foi possível gerar interpretação."
    
    variacao_pct = ((previsoes[-1] - valor_atual) / (valor_atual + 1)) * 100
    
    if tendencia == "crescimento":
        return f"Tendência de crescimento detectada. Previsão de aumento de {variacao_pct:.1f}% nos próximos 3 meses."
    elif tendencia == "decrescimento":
        return f"Tendência de redução detectada. Previsão de diminuição de {abs(variacao_pct):.1f}% nos próximos 3 meses."
    else:
        return f"Tendência estável. Variação prevista de {variacao_pct:.1f}% nos próximos 3 meses."

def anomaly_detection(df: pd.DataFrame, gerencia: str = None) -> Dict[str, Any]:
    """
    Detecção de anomalias nos dados de estoque.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência específica (opcional)
    
    Returns:
        Dict com anomalias detectadas
    """
    try:
        # Filtrar por gerência se especificado
        if gerencia:
            df_filtered = df[df['Gerência'] == gerencia].copy()
        else:
            df_filtered = df.copy()
        
        if df_filtered.empty:
            return {
                "status": "erro",
                "mensagem": "Nenhum dado encontrado",
                "anomalias": []
            }
        
        # Encontrar colunas de valores mensais
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
        
        if len(month_cols) < 3:
            return {
                "status": "aviso",
                "mensagem": "Dados insuficientes para detecção robusta de anomalias",
                "anomalias": []
            }
        
        anomalias = []
        
        # Análise por material
        if 'Material' in df_filtered.columns:
            for material in df_filtered['Material'].unique():
                if pd.isna(material):
                    continue
                    
                material_data = df_filtered[df_filtered['Material'] == material]
                
                # Extrair valores mensais para este material
                valores_mensais = []
                for col in month_cols:
                    valor = pd.to_numeric(material_data[col], errors='coerce').fillna(0).sum()
                    valores_mensais.append(valor)
                
                if len(valores_mensais) >= 3:
                    # Detectar anomalias usando método estatístico simples
                    media = np.mean(valores_mensais)
                    desvio = np.std(valores_mensais)
                    
                    if desvio > 0:
                        # Valores que estão além de 2 desvios padrão
                        for i, valor in enumerate(valores_mensais):
                            z_score = abs(valor - media) / desvio
                            if z_score > 2:  # Anomalia detectada
                                anomalias.append({
                                    "tipo": "valor_atipico",
                                    "material": material,
                                    "mes": f"Mês {i+1}",
                                    "valor": valor,
                                    "valor_esperado": media,
                                    "desvio_percentual": ((valor - media) / (media + 1)) * 100,
                                    "severidade": "alta" if z_score > 3 else "média"
                                })
        
        # Análise de crescimento súbito
        month_totals = []
        for col in month_cols:
            total = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum()
            month_totals.append(total)
        
        # Detectar crescimentos súbitos (>50% de um mês para outro)
        for i in range(1, len(month_totals)):
            if month_totals[i-1] > 0:
                crescimento = ((month_totals[i] - month_totals[i-1]) / month_totals[i-1]) * 100
                if crescimento > 50:
                    anomalias.append({
                        "tipo": "crescimento_subito",
                        "mes_anterior": f"Mês {i}",
                        "mes_atual": f"Mês {i+1}",
                        "valor_anterior": month_totals[i-1],
                        "valor_atual": month_totals[i],
                        "crescimento_percentual": crescimento,
                        "severidade": "alta" if crescimento > 100 else "média"
                    })
        
        return {
            "status": "sucesso",
            "anomalias": anomalias,
            "total_anomalias": len(anomalias),
            "interpretacao": _interpretar_anomalias(anomalias)
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro na detecção de anomalias: {str(e)}",
            "anomalias": []
        }

def _interpretar_anomalias(anomalias: List[Dict]) -> str:
    """Interpreta as anomalias detectadas."""
    if not anomalias:
        return "Nenhuma anomalia significativa detectada nos dados."
    
    alta_severidade = len([a for a in anomalias if a.get('severidade') == 'alta'])
    media_severidade = len([a for a in anomalias if a.get('severidade') == 'média'])
    
    interpretacao = f"Detectadas {len(anomalias)} anomalias: "
    if alta_severidade > 0:
        interpretacao += f"{alta_severidade} de alta severidade, "
    if media_severidade > 0:
        interpretacao += f"{media_severidade} de média severidade."
    
    return interpretacao.rstrip(', ') + "."

def prescriptive_analysis(df: pd.DataFrame, gerencia: str = None) -> Dict[str, Any]:
    """
    Análise prescritiva com recomendações de ações.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência específica (opcional)
    
    Returns:
        Dict com recomendações de ações
    """
    try:
        # Filtrar por gerência se especificado
        if gerencia:
            df_filtered = df[df['Gerência'] == gerencia].copy()
        else:
            df_filtered = df.copy()
        
        if df_filtered.empty:
            return {
                "status": "erro",
                "mensagem": "Nenhum dado encontrado",
                "recomendacoes": []
            }
        
        recomendacoes = []
        
        # Análise dos materiais com maior valor
        if 'Material' in df_filtered.columns:
            # Encontrar colunas de valores
            month_patterns = ['valor mês', 'valor_mes', 'mês']
            month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
            
            if month_cols:
                # Calcular valor total por material
                material_values = {}
                for material in df_filtered['Material'].unique():
                    if pd.isna(material):
                        continue
                    
                    material_data = df_filtered[df_filtered['Material'] == material]
                    total_value = 0
                    for col in month_cols:
                        total_value += pd.to_numeric(material_data[col], errors='coerce').fillna(0).sum()
                    
                    material_values[material] = total_value
                
                # Top 5 materiais com maior valor
                top_materials = sorted(material_values.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for material, valor in top_materials:
                    if valor > 0:
                        # Recomendações baseadas no valor
                        if valor > np.percentile(list(material_values.values()), 80):
                            recomendacoes.append({
                                "tipo": "reducao_estoque",
                                "prioridade": "alta",
                                "material": material,
                                "valor_atual": valor,
                                "acao": f"Priorizar redução do estoque de {material}",
                                "detalhes": f"Material representa alto valor ({valor:,.2f}). Considere remanejamento ou liquidação.",
                                "impacto_estimado": valor * 0.3  # 30% de redução potencial
                            })
        
        # Análise de tendências para recomendações
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
        
        if len(month_cols) >= 3:
            # Calcular tendência geral
            monthly_totals = []
            for col in month_cols:
                total = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum()
                monthly_totals.append(total)
            
            # Análise de tendência
            if len(monthly_totals) >= 3:
                recent_trend = np.mean(monthly_totals[-3:]) - np.mean(monthly_totals[:-3])
                
                if recent_trend > 0:
                    recomendacoes.append({
                        "tipo": "controle_crescimento",
                        "prioridade": "média",
                        "acao": "Implementar controles para reduzir crescimento do estoque",
                        "detalhes": f"Tendência de crescimento detectada (+{recent_trend:,.2f}). Revisar políticas de compra.",
                        "impacto_estimado": recent_trend * 0.5
                    })
                elif recent_trend < -monthly_totals[-1] * 0.1:  # Redução significativa
                    recomendacoes.append({
                        "tipo": "manter_estrategia",
                        "prioridade": "baixa",
                        "acao": "Manter estratégia atual de redução",
                        "detalhes": f"Tendência positiva de redução (-{abs(recent_trend):,.2f}). Continuar ações atuais.",
                        "impacto_estimado": abs(recent_trend)
                    })
        
        # Recomendações gerais baseadas no volume total
        total_value = sum(pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum() 
                         for col in month_cols if col in df_filtered.columns)
        
        if total_value > 0:
            # Recomendação de auditoria para valores altos
            if total_value > 1000000:  # Mais de 1 milhão
                recomendacoes.append({
                    "tipo": "auditoria",
                    "prioridade": "alta",
                    "acao": "Realizar auditoria completa do estoque",
                    "detalhes": f"Valor total elevado ({total_value:,.2f}). Auditoria pode identificar oportunidades de otimização.",
                    "impacto_estimado": total_value * 0.15
                })
        
        return {
            "status": "sucesso",
            "recomendacoes": recomendacoes,
            "total_recomendacoes": len(recomendacoes),
            "impacto_total_estimado": sum(r.get('impacto_estimado', 0) for r in recomendacoes),
            "interpretacao": _interpretar_recomendacoes(recomendacoes)
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro na análise prescritiva: {str(e)}",
            "recomendacoes": []
        }

def _interpretar_recomendacoes(recomendacoes: List[Dict]) -> str:
    """Interpreta as recomendações geradas."""
    if not recomendacoes:
        return "Nenhuma recomendação específica identificada com base nos dados atuais."
    
    alta_prioridade = len([r for r in recomendacoes if r.get('prioridade') == 'alta'])
    media_prioridade = len([r for r in recomendacoes if r.get('prioridade') == 'média'])
    
    interpretacao = f"Geradas {len(recomendacoes)} recomendações: "
    if alta_prioridade > 0:
        interpretacao += f"{alta_prioridade} de alta prioridade, "
    if media_prioridade > 0:
        interpretacao += f"{media_prioridade} de média prioridade."
    
    return interpretacao.rstrip(', ') + "."

def generate_natural_language_summary(df: pd.DataFrame, gerencia: str = None) -> Dict[str, Any]:
    """
    Gera resumo executivo em linguagem natural.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência específica (opcional)
    
    Returns:
        Dict com resumo em linguagem natural
    """
    try:
        # Filtrar por gerência se especificado
        if gerencia:
            df_filtered = df[df['Gerência'] == gerencia].copy()
            contexto = f"da gerência {gerencia}"
        else:
            df_filtered = df.copy()
            contexto = "geral"
        
        if df_filtered.empty:
            return {
                "status": "erro",
                "mensagem": "Nenhum dado encontrado para gerar resumo",
                "resumo": ""
            }
        
        # Calcular métricas básicas
        month_patterns = ['valor mês', 'valor_mes', 'mês']
        month_cols = _find_columns_by_pattern(df_filtered, month_patterns)
        
        if not month_cols:
            return {
                "status": "erro",
                "mensagem": "Colunas de valores mensais não encontradas",
                "resumo": ""
            }
        
        # Valor total
        total_value = sum(pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum() 
                         for col in month_cols)
        
        # Número de materiais únicos
        num_materials = df_filtered['Material'].nunique() if 'Material' in df_filtered.columns else 0
        
        # Quantidade total
        qty_patterns = ['quantidade', 'qtd']
        qty_cols = _find_columns_by_pattern(df_filtered, qty_patterns)
        total_qty = 0
        if qty_cols:
            total_qty = pd.to_numeric(df_filtered[qty_cols[0]], errors='coerce').fillna(0).sum()
        
        # Análise temporal
        monthly_totals = []
        for col in month_cols:
            total = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0).sum()
            monthly_totals.append(total)
        
        # Tendência
        tendencia_texto = "estável"
        if len(monthly_totals) >= 2:
            variacao = ((monthly_totals[-1] - monthly_totals[0]) / (monthly_totals[0] + 1)) * 100
            if variacao > 10:
                tendencia_texto = f"crescimento de {variacao:.1f}%"
            elif variacao < -10:
                tendencia_texto = f"redução de {abs(variacao):.1f}%"
        
        # Material com maior valor
        top_material = "não identificado"
        if 'Material' in df_filtered.columns and num_materials > 0:
            material_values = {}
            for material in df_filtered['Material'].unique():
                if pd.isna(material):
                    continue
                material_data = df_filtered[df_filtered['Material'] == material]
                total_mat_value = sum(pd.to_numeric(material_data[col], errors='coerce').fillna(0).sum() 
                                    for col in month_cols)
                material_values[material] = total_mat_value
            
            if material_values:
                top_material = max(material_values.items(), key=lambda x: x[1])[0]
        
        # Gerar resumo
        resumo = f"""
RESUMO EXECUTIVO - ESTOQUE EXCEDENTE {contexto.upper()}

SITUAÇÃO ATUAL:
• Valor total do estoque excedente: R$ {total_value:,.2f}
• Número de materiais diferentes: {num_materials}
• Quantidade total de itens: {int(total_qty):,}
• Material com maior impacto: {top_material}

TENDÊNCIA:
• Comportamento nos últimos meses: {tendencia_texto}
• Período analisado: {len(monthly_totals)} meses

PRINCIPAIS INSIGHTS:
• O valor médio por material é de R$ {(total_value/max(1, num_materials)):,.2f}
• {"Alto" if total_value > 1000000 else "Médio" if total_value > 100000 else "Baixo"} volume de estoque excedente detectado
• {"Atenção necessária para controlar crescimento" if "crescimento" in tendencia_texto else "Situação sob controle" if "redução" in tendencia_texto else "Monitoramento contínuo recomendado"}

PRÓXIMOS PASSOS RECOMENDADOS:
• Focar na gestão do material de maior impacto ({top_material})
• {"Implementar ações de redução urgentes" if total_value > 1000000 else "Manter monitoramento regular"}
• Revisar políticas de compra e estoque
        """.strip()
        
        return {
            "status": "sucesso",
            "resumo": resumo,
            "metricas": {
                "valor_total": total_value,
                "num_materiais": num_materials,
                "quantidade_total": total_qty,
                "top_material": top_material,
                "tendencia": tendencia_texto
            }
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao gerar resumo: {str(e)}",
            "resumo": ""
        }

def comprehensive_ai_analysis(df: pd.DataFrame, gerencia: str = None) -> Dict[str, Any]:
    """
    Executa todas as análises de IA de forma integrada.
    
    Args:
        df: DataFrame com dados de estoque
        gerencia: Nome da gerência específica (opcional)
    
    Returns:
        Dict com todas as análises de IA
    """
    try:
        return {
            "analise_preditiva": predictive_analysis(df, gerencia),
            "deteccao_anomalias": anomaly_detection(df, gerencia),
            "analise_prescritiva": prescriptive_analysis(df, gerencia),
            "resumo_executivo": generate_natural_language_summary(df, gerencia),
            "timestamp": datetime.now().isoformat(),
            "gerencia": gerencia or "Todas"
        }
    except Exception as e:
        return {
            "erro": f"Erro na análise integrada: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "gerencia": gerencia or "Todas"
        }

