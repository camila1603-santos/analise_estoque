"""
Integração de IA Generativa Real para o MVP de Estoque Excedente
Módulo que adiciona funcionalidades de IA Generativa ao código existente
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def generate_ai_insights_for_gerencia(kpis: Dict[str, Any], gerencia: str) -> Dict[str, Any]:
    """
    Gera insights de IA Generativa para uma gerência específica.
    Esta função pode ser integrada diretamente ao código existente.
    
    Args:
        kpis: Dicionário com KPIs calculados (do enhanced_analysis.py)
        gerencia: Nome da gerência
    
    Returns:
        Dict com insights gerados por IA
    """
    
    # Verificar se OpenAI está disponível
    if not OPENAI_AVAILABLE:
        return {
            "status": "erro",
            "mensagem": "OpenAI não disponível",
            "resumo_executivo": f"Análise tradicional para {gerencia}",
            "recomendacoes": ["Revisar dados manualmente", "Implementar controles básicos"]
        }
    
    try:
        # Configurar cliente OpenAI (usando variáveis de ambiente já configuradas)
        client = OpenAI()
        
        # Extrair dados dos KPIs
        valor_total = kpis.get('valor_total', 0)
        num_materiais = kpis.get('numero_materiais', 0)
        variacao_mensal = kpis.get('variacao_mensal', 0)
        
        # Criar prompt contextualizado
        prompt = f"""
Você é um consultor especialista em gestão de estoque. Analise os dados da {gerencia} e gere insights executivos.

DADOS:
- Gerência: {gerencia}
- Valor Total do Estoque Excedente: R$ {valor_total:,.2f}
- Número de Materiais: {num_materiais}
- Variação Mensal: {variacao_mensal:.1f}%

Gere um resumo executivo de 2-3 parágrafos e 3-5 recomendações práticas.
Use linguagem profissional e objetiva.
"""

        # Fazer chamada para OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor especialista em gestão de estoque e supply chain."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Processar resposta
        ai_response = response.choices[0].message.content
        
        # Dividir em resumo e recomendações (processamento simples)
        lines = ai_response.split('\n')
        resumo_lines = []
        recomendacoes_lines = []
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if 'recomenda' in line.lower() or 'sugest' in line.lower() or line.startswith('•') or line.startswith('-'):
                in_recommendations = True
            
            if in_recommendations:
                if line.startswith('•') or line.startswith('-') or line.startswith('1.') or line.startswith('2.'):
                    recomendacoes_lines.append(line)
            else:
                resumo_lines.append(line)
        
        # Se não conseguiu separar, usar resposta completa como resumo
        if not resumo_lines:
            resumo_lines = [ai_response]
        
        if not recomendacoes_lines:
            recomendacoes_lines = ["Revisar dados detalhadamente", "Implementar monitoramento contínuo", "Buscar oportunidades de otimização"]
        
        return {
            "status": "sucesso",
            "resumo_executivo": ' '.join(resumo_lines),
            "recomendacoes": recomendacoes_lines,
            "timestamp": datetime.now().isoformat(),
            "tokens_utilizados": response.usage.total_tokens if hasattr(response, 'usage') else 0,
            "modelo": "gpt-3.5-turbo"
        }
        
    except Exception as e:
        # Fallback para análise tradicional
        return {
            "status": "fallback",
            "mensagem": f"IA indisponível: {str(e)}",
            "resumo_executivo": f"""
A {gerencia} apresenta um estoque excedente de R$ {valor_total:,.2f} distribuído em {num_materiais} materiais diferentes. 
A variação mensal de {variacao_mensal:.1f}% {'indica tendência de crescimento que requer atenção' if variacao_mensal > 0 else 'mostra redução positiva no estoque'}.
É recomendado focar nos materiais de maior valor e implementar controles mais rigorosos.
            """.strip(),
            "recomendacoes": [
                f"Priorizar gestão dos {min(10, num_materiais)} materiais de maior valor",
                "Implementar revisão semanal dos indicadores",
                "Estabelecer metas de redução por categoria",
                "Revisar políticas de compra e estoque de segurança"
            ]
        }

def integrate_ai_with_existing_analysis(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integra IA Generativa com as análises existentes do enhanced_analysis.py
    
    Args:
        analysis_result: Resultado da análise existente
    
    Returns:
        Análise enriquecida com IA Generativa
    """
    
    gerencia = analysis_result.get('gerencia', 'Desconhecida')
    kpis = analysis_result.get('kpis', {})
    
    # Gerar insights de IA
    ai_insights = generate_ai_insights_for_gerencia(kpis, gerencia)
    
    # Adicionar IA aos resultados existentes
    analysis_result['ai_generativa'] = ai_insights
    analysis_result['enhanced_with_ai'] = True
    analysis_result['ai_timestamp'] = datetime.now().isoformat()
    
    return analysis_result

# Função para testar a integração
def test_ai_integration():
    """Testa a integração de IA Generativa."""
    
    # Dados de exemplo (similar ao que vem do enhanced_analysis.py)
    sample_kpis = {
        'valor_total': 1500000.00,
        'numero_materiais': 45,
        'variacao_mensal': -12.5,
        'quantidade_total': 1200
    }
    
    sample_analysis = {
        'gerencia': 'Operações',
        'kpis': sample_kpis,
        'timestamp': datetime.now().isoformat()
    }
    
    # Testar integração
    enhanced_analysis = integrate_ai_with_existing_analysis(sample_analysis)
    
    print("=== TESTE DE INTEGRAÇÃO DE IA GENERATIVA ===")
    print(f"Gerência: {enhanced_analysis['gerencia']}")
    print(f"IA Status: {enhanced_analysis['ai_generativa']['status']}")
    print(f"Resumo Executivo:")
    print(enhanced_analysis['ai_generativa']['resumo_executivo'])
    print(f"\nRecomendações:")
    for i, rec in enumerate(enhanced_analysis['ai_generativa']['recomendacoes'], 1):
        print(f"{i}. {rec}")
    
    return enhanced_analysis

if __name__ == "__main__":
    # Executar teste
    result = test_ai_integration()
    
    # Salvar resultado para verificação
    with open('/home/ubuntu/ai_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        