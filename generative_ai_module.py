"""
Módulo de IA Generativa para Análise de Estoque Excedente
Integra OpenAI GPT para geração de insights, recomendações e relatórios automatizados.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class GenerativeAIAnalyzer:
    """
    Classe principal para análises de IA generativa em dados de estoque excedente.
    Utiliza OpenAI GPT para gerar insights inteligentes e recomendações personalizadas.
    """
    
    def __init__(self):
        """Inicializa o analisador de IA generativa."""
        self.client = None
        self.model = "gpt-3.5-turbo"
        
        if OPENAI_AVAILABLE:
            try:
                # Configurar cliente OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                api_base = os.getenv('OPENAI_API_BASE')
                
                if api_key:
                    if api_base:
                        self.client = OpenAI(api_key=api_key, base_url=api_base)
                    else:
                        self.client = OpenAI(api_key=api_key)
                    
                    print("✅ IA Generativa inicializada com sucesso!")
                else:
                    print("⚠️ OPENAI_API_KEY não encontrada. IA Generativa desabilitada.")
            except Exception as e:
                print(f"❌ Erro ao inicializar IA Generativa: {str(e)}")
                self.client = None
        else:
            print("⚠️ Biblioteca OpenAI não disponível. IA Generativa desabilitada.")
    
    def is_available(self) -> bool:
        """Verifica se a IA generativa está disponível."""
        return self.client is not None
    
    def generate_executive_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um resumo executivo inteligente usando IA generativa.
        
        Args:
            analysis_data: Dados completos da análise de estoque
            
        Returns:
            Dict com resumo executivo gerado por IA
        """
        if not self.is_available():
            return {
                "status": "erro",
                "mensagem": "IA Generativa não disponível",
                "resumo": "Resumo não pôde ser gerado automaticamente."
            }
        
        try:
            # Preparar dados para o prompt
            gerencia = analysis_data.get("gerencia", "Não especificada")
            kpis = analysis_data.get("kpis", {})
            ai_analysis = analysis_data.get("ai_analysis", {})
            
            # Extrair métricas principais
            valor_total = kpis.get("valor_total", 0)
            num_materiais = kpis.get("numero_materiais", 0)
            variacao_mensal = kpis.get("variacao_mensal", 0)
            
            # Extrair insights de IA
            previsoes = ai_analysis.get("analise_preditiva", {}).get("previsoes", [])
            anomalias = ai_analysis.get("deteccao_anomalias", {}).get("anomalias", [])
            recomendacoes = ai_analysis.get("analise_prescritiva", {}).get("recomendacoes", [])
            
            # Construir prompt estruturado
            prompt = f"""
Você é um consultor especialista em gestão de estoque e análise de dados. Analise os dados abaixo e gere um resumo executivo profissional e estratégico.

DADOS DA ANÁLISE:
- Gerência: {gerencia}
- Valor Total do Estoque Excedente: R$ {valor_total:,.2f}
- Número de Materiais: {num_materiais}
- Variação Mensal: {variacao_mensal:.1f}%
- Previsões (próximos 3 meses): {previsoes}
- Número de Anomalias Detectadas: {len(anomalias)}
- Número de Recomendações: {len(recomendacoes)}

INSTRUÇÕES:
1. Crie um resumo executivo de 3-4 parágrafos
2. Foque nos pontos mais críticos e oportunidades
3. Use linguagem profissional e objetiva
4. Inclua insights sobre tendências e riscos
5. Sugira próximos passos estratégicos
6. Use formatação em markdown

Gere o resumo executivo:
"""

            # Fazer chamada para OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um consultor especialista em gestão de estoque e análise de dados empresariais."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            resumo_gerado = response.choices[0].message.content
            
            return {
                "status": "sucesso",
                "resumo": resumo_gerado,
                "timestamp": datetime.now().isoformat(),
                "modelo_usado": self.model,
                "tokens_utilizados": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar resumo executivo: {str(e)}",
                "resumo": "Não foi possível gerar o resumo executivo automaticamente."
            }
    
    def generate_strategic_recommendations(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera recomendações estratégicas personalizadas usando IA generativa.
        
        Args:
            analysis_data: Dados completos da análise de estoque
            
        Returns:
            Dict com recomendações estratégicas geradas por IA
        """
        if not self.is_available():
            return {
                "status": "erro",
                "mensagem": "IA Generativa não disponível",
                "recomendacoes": []
            }
        
        try:
            # Preparar contexto para IA
            gerencia = analysis_data.get("gerencia", "Não especificada")
            kpis = analysis_data.get("kpis", {})
            ai_analysis = analysis_data.get("ai_analysis", {})
            
            # Extrair dados relevantes
            valor_total = kpis.get("valor_total", 0)
            tendencia = ai_analysis.get("analise_preditiva", {}).get("tendencia", "indefinida")
            anomalias = ai_analysis.get("deteccao_anomalias", {}).get("anomalias", [])
            
            prompt = f"""
Você é um consultor Black Belt em Lean Six Sigma especializado em gestão de estoque. Analise a situação e gere recomendações estratégicas específicas.

SITUAÇÃO ATUAL:
- Gerência: {gerencia}
- Valor do Estoque Excedente: R$ {valor_total:,.2f}
- Tendência Identificada: {tendencia}
- Anomalias Detectadas: {len(anomalias)}

CONTEXTO:
- Esta é uma análise de estoque excedente que impacta o capital de giro
- O objetivo é reduzir custos e otimizar a gestão de materiais
- As recomendações devem ser práticas e implementáveis

INSTRUÇÕES:
1. Gere 5-7 recomendações estratégicas específicas
2. Priorize por impacto e facilidade de implementação
3. Inclua prazos estimados para cada ação
4. Considere aspectos financeiros, operacionais e de risco
5. Use formato estruturado com título, descrição e benefícios esperados

Gere as recomendações estratégicas:
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um consultor Black Belt em Lean Six Sigma especializado em gestão de estoque e otimização de processos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.6
            )
            
            recomendacoes_texto = response.choices[0].message.content
            
            return {
                "status": "sucesso",
                "recomendacoes_texto": recomendacoes_texto,
                "timestamp": datetime.now().isoformat(),
                "modelo_usado": self.model,
                "tokens_utilizados": response.usage.total_tokens if hasattr(response, 'usage') else 0
            }
            
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar recomendações: {str(e)}",
                "recomendacoes_texto": "Não foi possível gerar recomendações automaticamente."
            }
    
    def generate_risk_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera análise de riscos usando IA generativa.
        
        Args:
            analysis_data: Dados completos da análise de estoque
            
        Returns:
            Dict com análise de riscos gerada por IA
        """
        if not self.is_available():
            return {
                "status": "erro",
                "mensagem": "IA Generativa não disponível",
                "analise_riscos": "Análise de riscos não disponível."
            }
        
        try:
            gerencia = analysis_data.get("gerencia", "Não especificada")
            kpis = analysis_data.get("kpis", {})
            ai_analysis = analysis_data.get("ai_analysis", {})
            
            valor_total = kpis.get("valor_total", 0)
            variacao_mensal = kpis.get("variacao_mensal", 0)
            anomalias = ai_analysis.get("deteccao_anomalias", {}).get("anomalias", [])
            previsoes = ai_analysis.get("analise_preditiva", {}).get("previsoes", [])
            
            prompt = f"""
Você é um analista de riscos especializado em gestão de estoque. Analise os dados e identifique os principais riscos e oportunidades.

DADOS PARA ANÁLISE:
- Gerência: {gerencia}
- Valor em Risco: R$ {valor_total:,.2f}
- Variação Mensal: {variacao_mensal:.1f}%
- Anomalias Detectadas: {len(anomalias)}
- Tendência das Previsões: {previsoes}

INSTRUÇÕES:
1. Identifique 3-5 principais riscos
2. Avalie probabilidade e impacto de cada risco
3. Sugira medidas de mitigação
4. Identifique oportunidades de melhoria
5. Use classificação: ALTO, MÉDIO, BAIXO para cada risco

Gere a análise de riscos:
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um analista de riscos especializado em gestão de estoque e supply chain."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            analise_riscos = response.choices[0].message.content
            
            return {
                "status": "sucesso",
                "analise_riscos": analise_riscos,
                "timestamp": datetime.now().isoformat(),
                "modelo_usado": self.model
            }
            
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar análise de riscos: {str(e)}",
                "analise_riscos": "Não foi possível gerar análise de riscos automaticamente."
            }
    
    def generate_comprehensive_insights(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera insights abrangentes combinando todas as funcionalidades de IA generativa.
        
        Args:
            analysis_data: Dados completos da análise de estoque
            
        Returns:
            Dict com todos os insights gerados por IA
        """
        try:
            # Gerar todos os tipos de análise
            resumo_executivo = self.generate_executive_summary(analysis_data)
            recomendacoes = self.generate_strategic_recommendations(analysis_data)
            analise_riscos = self.generate_risk_analysis(analysis_data)
            
            return {
                "status": "sucesso",
                "resumo_executivo": resumo_executivo,
                "recomendacoes_estrategicas": recomendacoes,
                "analise_riscos": analise_riscos,
                "timestamp": datetime.now().isoformat(),
                "ia_disponivel": self.is_available()
            }
            
        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar insights abrangentes: {str(e)}",
                "ia_disponivel": self.is_available()
            }

# Função de conveniência para uso direto
def generate_ai_insights(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função de conveniência para gerar insights de IA.
    
    Args:
        analysis_data: Dados da análise de estoque
        
    Returns:
        Dict com insights gerados por IA
    """
    analyzer = GenerativeAIAnalyzer()
    return analyzer.generate_comprehensive_insights(analysis_data)

# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo para teste
    example_data = {
        "gerencia": "Operações",
        "kpis": {
            "valor_total": 1500000.00,
            "numero_materiais": 45,
            "variacao_mensal": -12.5
        },
        "ai_analysis": {
            "analise_preditiva": {
                "previsoes": [1400000, 1350000, 1300000],
                "tendencia": "decrescimento"
            },
            "deteccao_anomalias": {
                "anomalias": [{"tipo": "valor_atipico", "severidade": "alta"}]
            },
            "analise_prescritiva": {
                "recomendacoes": [{"tipo": "reducao_estoque", "prioridade": "alta"}]
            }
        }
    }
    
    # Testar IA generativa
    analyzer = GenerativeAIAnalyzer()
    if analyzer.is_available():
        insights = analyzer.generate_comprehensive_insights(example_data)
        print("✅ Teste de IA Generativa realizado com sucesso!")
        print(f"Status: {insights.get('status')}")
    else:
        print("⚠️ IA Generativa não disponível para teste.")

