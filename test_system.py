"""
Script de teste para o sistema de análise de estoque excedente.
"""

import pandas as pd
import os
import sys

# Adicionar diretório atual ao path
sys.path.append('/home/ubuntu')

def test_with_sample_data():
    """Testa o sistema com os dados de exemplo."""
    try:
        print("🧪 Iniciando teste do sistema...")
        
        # Carregar dados de exemplo
        df = pd.read_excel('/home/ubuntu/upload/Todas_Areas_Expandidas.xlsx')
        print(f"✅ Dados carregados: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        # Testar detecção de gerências
        from enhanced_analysis import get_unique_gerencias
        gerencias = get_unique_gerencias(df)
        print(f"✅ Gerências detectadas: {gerencias}")
        
        if not gerencias:
            print("❌ Nenhuma gerência encontrada!")
            return False
        
        # Testar análise de uma gerência
        from enhanced_analysis import comprehensive_gerencia_analysis
        primeira_gerencia = gerencias[0]
        print(f"🔍 Testando análise da gerência: {primeira_gerencia}")
        
        analysis = comprehensive_gerencia_analysis(df, primeira_gerencia)
        
        if analysis.get("status") == "sucesso":
            print("✅ Análise da gerência executada com sucesso!")
            
            # Mostrar alguns resultados
            kpis = analysis.get("kpis", {})
            print(f"   - Valor total: R$ {kpis.get('valor_total', 0):,.2f}")
            print(f"   - Número de materiais: {kpis.get('numero_materiais', 0)}")
            print(f"   - Variação mensal: {kpis.get('variacao_mensal', 0):.1f}%")
        else:
            print(f"❌ Erro na análise: {analysis.get('erro', 'Erro desconhecido')}")
            return False
        
        # Testar geração de gráficos
        from enhanced_charts import generate_all_charts_for_gerencia
        print("📊 Testando geração de gráficos...")
        
        charts = generate_all_charts_for_gerencia(analysis)
        print(f"✅ {len(charts)} gráficos gerados: {list(charts.keys())}")
        
        # Testar geração de PDF
        print("📄 Testando geração de PDF...")
        from enhanced_pdf_generator import generate_pdf_for_gerencia
        
        test_pdf_path = "/home/ubuntu/teste_relatorio.pdf"
        generate_pdf_for_gerencia(analysis, test_pdf_path)
        
        if os.path.exists(test_pdf_path):
            print(f"✅ PDF gerado com sucesso: {test_pdf_path}")
            print(f"   Tamanho do arquivo: {os.path.getsize(test_pdf_path)} bytes")
        else:
            print("❌ Erro na geração do PDF!")
            return False
        
        print("\n🎉 Todos os testes passaram com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_sample_data()
    if success:
        print("\n✅ Sistema pronto para uso!")
    else:
        print("\n❌ Sistema apresentou problemas nos testes.")

