"""
IA Generativa Inteligente usando Templates Adaptativos
Simula funcionalidades de IA Generativa através de templates inteligentes baseados em dados
"""

import random
from typing import Dict, Any, List
from datetime import datetime

class SmartAIGenerator:
    """
    Gerador de IA que usa templates inteligentes para simular IA Generativa.
    Analisa os dados e gera insights contextualizados de forma inteligente.
    """
    
    def __init__(self):
        self.templates_resumo = {
            'crescimento_alto': [
                "A {gerencia} apresenta um crescimento significativo de {variacao:.1f}% no estoque excedente, totalizando R$ {valor:,.2f} em {materiais} materiais diferentes. Este crescimento requer atenção imediata para evitar impactos no capital de giro.",
                "Observa-se na {gerencia} um aumento expressivo de {variacao:.1f}% no valor do estoque excedente, atingindo R$ {valor:,.2f}. Com {materiais} materiais em excesso, é fundamental implementar ações corretivas urgentes."
            ],
            'crescimento_moderado': [
                "A {gerencia} registra crescimento moderado de {variacao:.1f}% no estoque excedente, com valor atual de R$ {valor:,.2f} distribuído em {materiais} materiais. Situação controlável com ações preventivas adequadas.",
                "Na {gerencia}, o estoque excedente cresceu {variacao:.1f}%, totalizando R$ {valor:,.2f} em {materiais} itens. O crescimento está dentro de parâmetros gerenciáveis, mas requer monitoramento contínuo."
            ],
            'estavel': [
                "A {gerencia} mantém estabilidade no estoque excedente com variação de {variacao:.1f}%, apresentando R$ {valor:,.2f} em {materiais} materiais. A situação atual permite planejamento estratégico de médio prazo.",
                "O estoque excedente da {gerencia} permanece estável com {variacao:.1f}% de variação, totalizando R$ {valor:,.2f}. Esta estabilidade em {materiais} materiais indica controle efetivo dos processos."
            ],
            'reducao_moderada': [
                "A {gerencia} demonstra progresso positivo com redução de {variacao:.1f}% no estoque excedente, mantendo R$ {valor:,.2f} em {materiais} materiais. As ações implementadas mostram efetividade.",
                "Observa-se melhoria na {gerencia} com diminuição de {variacao:.1f}% do estoque excedente para R$ {valor:,.2f}. A gestão de {materiais} materiais está evoluindo positivamente."
            ],
            'reducao_alta': [
                "A {gerencia} alcança excelente performance com redução de {variacao:.1f}% no estoque excedente, chegando a R$ {valor:,.2f} em {materiais} materiais. Resultado exemplar que deve ser mantido e replicado.",
                "Destaque para a {gerencia} que obteve redução significativa de {variacao:.1f}% no estoque excedente, totalizando R$ {valor:,.2f}. A gestão eficiente de {materiais} materiais serve como benchmark interno."
            ]
        }
        
        self.templates_recomendacoes = {
            'alto_valor': [
                "Implementar revisão semanal dos materiais de maior valor (>R$ 50.000)",
                "Estabelecer parcerias para remanejamento interno dos itens críticos",
                "Negociar devolução ou consignação com fornecedores principais",
                "Criar comitê de gestão de estoque para decisões rápidas"
            ],
            'medio_valor': [
                "Revisar políticas de compra para materiais de médio valor",
                "Implementar sistema de alertas para novos excessos",
                "Estabelecer metas trimestrais de redução por categoria",
                "Treinar equipe em técnicas de gestão lean de estoque"
            ],
            'baixo_valor': [
                "Focar em liquidação rápida de materiais de baixo valor",
                "Implementar processo de doação para itens obsoletos",
                "Revisar níveis mínimos de estoque de segurança",
                "Otimizar frequência de compras para reduzir excessos"
            ],
            'crescimento': [
                "URGENTE: Suspender novas compras até análise detalhada",
                "Investigar causas do crescimento com equipe de compras",
                "Implementar controle diário dos principais materiais",
                "Estabelecer plano de contingência para liquidação"
            ],
            'reducao': [
                "Manter estratégia atual que está gerando resultados positivos",
                "Documentar melhores práticas para replicação",
                "Estabelecer metas mais ambiciosas para próximo período",
                "Compartilhar sucessos com outras gerências"
            ]
        }
    
    def classify_situation(self, variacao: float, valor: float) -> str:
        """Classifica a situação baseada nos dados."""
        if variacao > 15:
            return 'crescimento_alto'
        elif variacao > 5:
            return 'crescimento_moderado'
        elif -5 <= variacao <= 5:
            return 'estavel'
        elif -15 <= variacao < -5:
            return 'reducao_moderada'
        else:
            return 'reducao_alta'
    
    def classify_value_level(self, valor: float, materiais: int) -> str:
        """Classifica o nível de valor."""
        valor_medio = valor / max(1, materiais)
        
        if valor_medio > 100000:
            return 'alto_valor'
        elif valor_medio > 25000:
            return 'medio_valor'
        else:
            return 'baixo_valor'
    
    def generate_executive_summary(self, kpis: Dict[str, Any], gerencia: str) -> str:
        """Gera resumo executivo inteligente."""
        valor_total = kpis.get('valor_total', 0)
        num_materiais = kpis.get('numero_materiais', 0)
        variacao_mensal = kpis.get('variacao_mensal', 0)
        
        # Classificar situação
        situacao = self.classify_situation(variacao_mensal, valor_total)
        
        # Selecionar template apropriado
        templates = self.templates_resumo[situacao]
        template = random.choice(templates)
        
        # Gerar resumo contextualizado
        resumo_principal = template.format(
            gerencia=gerencia,
            variacao=abs(variacao_mensal),
            valor=valor_total,
            materiais=num_materiais
        )
        
        # Adicionar insights adicionais
        valor_medio = valor_total / max(1, num_materiais)
        
        insights_adicionais = []
        
        if valor_medio > 50000:
            insights_adicionais.append(f"O valor médio por material de R$ {valor_medio:,.0f} indica necessidade de gestão especializada para itens de alto valor.")
        
        if num_materiais > 50:
            insights_adicionais.append(f"A diversidade de {num_materiais} materiais diferentes sugere oportunidades de consolidação e padronização.")
        elif num_materiais < 10:
            insights_adicionais.append(f"O número reduzido de {num_materiais} materiais permite gestão mais focada e personalizada.")
        
        if variacao_mensal > 20:
            insights_adicionais.append("O crescimento acelerado requer investigação imediata das causas raiz.")
        elif variacao_mensal < -20:
            insights_adicionais.append("A redução expressiva demonstra efetividade das ações implementadas.")
        
        # Combinar resumo principal com insights
        resumo_completo = resumo_principal
        if insights_adicionais:
            resumo_completo += " " + " ".join(insights_adicionais)
        
        return resumo_completo
    
    def generate_smart_recommendations(self, kpis: Dict[str, Any], gerencia: str) -> List[str]:
        """Gera recomendações inteligentes baseadas nos dados."""
        valor_total = kpis.get('valor_total', 0)
        num_materiais = kpis.get('numero_materiais', 0)
        variacao_mensal = kpis.get('variacao_mensal', 0)
        
        recomendacoes = []
        
        # Recomendações baseadas no valor
        nivel_valor = self.classify_value_level(valor_total, num_materiais)
        recomendacoes.extend(random.sample(self.templates_recomendacoes[nivel_valor], 2))
        
        # Recomendações baseadas na tendência
        if variacao_mensal > 5:
            recomendacoes.extend(random.sample(self.templates_recomendacoes['crescimento'], 2))
        elif variacao_mensal < -5:
            recomendacoes.extend(random.sample(self.templates_recomendacoes['reducao'], 1))
        
        # Recomendações específicas por contexto
        if valor_total > 1000000:
            recomendacoes.append("Considerar auditoria externa especializada devido ao alto valor envolvido")
        
        if num_materiais > 100:
            recomendacoes.append("Implementar classificação ABC para priorização de ações")
        
        # Personalização por gerência
        gerencia_lower = gerencia.lower()
        if 'operac' in gerencia_lower:
            recomendacoes.append("Integrar gestão de estoque com planejamento de produção")
        elif 'qualidade' in gerencia_lower:
            recomendacoes.append("Revisar critérios de qualificação para reduzir rejeições")
        elif 'manutenc' in gerencia_lower:
            recomendacoes.append("Otimizar estoque de peças de reposição baseado em criticidade")
        
        # Remover duplicatas e limitar quantidade
        recomendacoes = list(dict.fromkeys(recomendacoes))[:6]
        
        return recomendacoes
    
    def generate_risk_analysis(self, kpis: Dict[str, Any], gerencia: str) -> str:
        """Gera análise de riscos contextualizada."""
        valor_total = kpis.get('valor_total', 0)
        variacao_mensal = kpis.get('variacao_mensal', 0)
        num_materiais = kpis.get('numero_materiais', 0)
        
        riscos = []
        
        # Análise de risco financeiro
        if valor_total > 2000000:
            riscos.append("🔴 RISCO ALTO: Valor elevado impacta significativamente o capital de giro")
        elif valor_total > 500000:
            riscos.append("🟡 RISCO MÉDIO: Valor considerável requer monitoramento contínuo")
        
        # Análise de risco operacional
        if variacao_mensal > 25:
            riscos.append("🔴 RISCO ALTO: Crescimento acelerado indica perda de controle")
        elif variacao_mensal > 10:
            riscos.append("🟡 RISCO MÉDIO: Tendência de crescimento requer atenção")
        
        # Análise de risco de obsolescência
        valor_medio = valor_total / max(1, num_materiais)
        if valor_medio > 100000:
            riscos.append("🟡 RISCO MÉDIO: Materiais de alto valor unitário com risco de obsolescência")
        
        # Oportunidades
        oportunidades = []
        if variacao_mensal < -10:
            oportunidades.append("🟢 OPORTUNIDADE: Tendência de redução permite otimização adicional")
        
        if num_materiais < 20:
            oportunidades.append("🟢 OPORTUNIDADE: Número reduzido de materiais facilita gestão focada")
        
        # Compilar análise
        analise = "ANÁLISE DE RISCOS E OPORTUNIDADES:\n\n"
        
        if riscos:
            analise += "RISCOS IDENTIFICADOS:\n"
            for risco in riscos:
                analise += f"• {risco}\n"
            analise += "\n"
        
        if oportunidades:
            analise += "OPORTUNIDADES IDENTIFICADAS:\n"
            for oportunidade in oportunidades:
                analise += f"• {oportunidade}\n"
        
        if not riscos and not oportunidades:
            analise += "Situação estável sem riscos críticos identificados. Manter monitoramento regular."
        
        return analise.strip()

def generate_ai_insights_enhanced(kpis: Dict[str, Any], gerencia: str) -> Dict[str, Any]:
    """
    Função principal que gera insights de IA usando templates inteligentes.
    Esta função substitui a dependência do OpenAI por lógica inteligente.
    """
    
    generator = SmartAIGenerator()
    
    try:
        # Gerar componentes da análise
        resumo_executivo = generator.generate_executive_summary(kpis, gerencia)
        recomendacoes = generator.generate_smart_recommendations(kpis, gerencia)
        analise_riscos = generator.generate_risk_analysis(kpis, gerencia)
        
        return {
            "status": "sucesso",
            "resumo_executivo": resumo_executivo,
            "recomendacoes": recomendacoes,
            "analise_riscos": analise_riscos,
            "timestamp": datetime.now().isoformat(),
            "modelo": "SmartAI_Templates_v1.0",
            "tipo_ia": "Template-Based Generative AI"
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro na geração de insights: {str(e)}",
            "resumo_executivo": f"Análise básica para {gerencia}",
            "recomendacoes": ["Revisar dados", "Implementar controles"],
            "analise_riscos": "Análise de riscos não disponível"
        }

# Função de integração com o código existente
def integrate_smart_ai_with_analysis(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integra IA Generativa inteligente com as análises existentes.
    """
    
    gerencia = analysis_result.get('gerencia', 'Desconhecida')
    kpis = analysis_result.get('kpis', {})
    
    # Gerar insights de IA
    ai_insights = generate_ai_insights_enhanced(kpis, gerencia)
    
    # Adicionar IA aos resultados existentes
    analysis_result['ai_generativa'] = ai_insights
    analysis_result['enhanced_with_ai'] = True
    analysis_result['ai_timestamp'] = datetime.now().isoformat()
    
    return analysis_result

# Teste da funcionalidade
if __name__ == "__main__":
    # Dados de teste
    test_kpis = {
        'valor_total': 1500000.00,
        'numero_materiais': 45,
        'variacao_mensal': -12.5,
        'quantidade_total': 1200
    }
    
    test_analysis = {
        'gerencia': 'Operações',
        'kpis': test_kpis,
        'timestamp': datetime.now().isoformat()
    }
    
    # Testar integração
    enhanced_analysis = integrate_smart_ai_with_analysis(test_analysis)
    
    print("=== TESTE DE IA GENERATIVA INTELIGENTE ===")
    print(f"Gerência: {enhanced_analysis['gerencia']}")
    print(f"IA Status: {enhanced_analysis['ai_generativa']['status']}")
    print(f"Modelo: {enhanced_analysis['ai_generativa']['modelo']}")
    print(f"\nResumo Executivo:")
    print(enhanced_analysis['ai_generativa']['resumo_executivo'])
    print(f"\nRecomendações:")
    for i, rec in enumerate(enhanced_analysis['ai_generativa']['recomendacoes'], 1):
        print(f"{i}. {rec}")
    print(f"\n{enhanced_analysis['ai_generativa']['analise_riscos']}")

