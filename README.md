# Sistema de Análise Inteligente de Estoque Excedente

## 📋 Descrição

Sistema avançado para análise de estoque excedente com Inteligência Artificial, que gera relatórios PDF individuais por gerência com dashboards completos, KPIs, gráficos e análises preditivas.

## 🚀 Funcionalidades Principais

### 📊 Dashboard de Visão Geral
- **Tabela de dados** formatada por gerência
- **KPIs Principais**: Valor total, variação mensal, número de itens
- **Evolução Temporal**: Gráfico de tendência dos últimos 12 meses
- **Top 10 Materiais**: Ranking por valor de impacto

### 🤖 Análises de Inteligência Artificial

#### 1. Análise Preditiva
- Previsão de valores de estoque excedente para próximos meses
- Identificação de tendências (crescimento, redução, estabilidade)
- Cálculo de intervalos de confiança

#### 2. Detecção de Anomalias
- Identificação automática de valores atípicos
- Detecção de crescimentos súbitos
- Classificação por severidade (alta, média, baixa)

#### 3. Análise Prescritiva
- Recomendações específicas de ações
- Priorização por impacto estimado
- Sugestões de remanejamento e otimização

#### 4. Resumo em Linguagem Natural
- Geração automática de insights
- Resumo executivo personalizado
- Interpretação clara dos dados

## 📁 Estrutura dos Arquivos

### Arquivos Principais
- `enhanced_app.py` - Interface Streamlit principal
- `enhanced_analysis.py` - Módulo de análise de dados por gerência
- `ai_analysis.py` - Módulo de análises de IA
- `enhanced_charts.py` - Geração de gráficos e visualizações
- `enhanced_pdf_generator.py` - Gerador de PDFs por gerência

### Arquivos de Configuração
- `requirements.txt` - Dependências do projeto
- `README.md` - Documentação completa
- `test_system.py` - Script de testes

### Arquivos Originais (Referência)
- `app.py` - Aplicação original
- `core.py` - Funções básicas originais
- `kpis.py` - KPIs originais
- `pdf_generator.py` - Gerador PDF original

## 🛠️ Instalação e Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar Aplicação
```bash
streamlit run enhanced_app.py
```

### 3. Testar Sistema
```bash
python test_system.py
```

## 📊 Formato do Arquivo CSV

O arquivo CSV deve conter as seguintes colunas:

| Coluna | Descrição | Obrigatória |
|--------|-----------|-------------|
| Gerência | Nome da gerência | ✅ |
| Material | Identificação do material | ✅ |
| Área | Área dentro da gerência | ✅ |
| Quantidade | Quantidade do material | ✅ |
| Valor Mês 01-12 | Valores mensais | ✅ |

### Exemplo de Estrutura
```csv
Gerência,Área,Material,Quantidade,Valor Mês 01,Valor Mês 02,Valor Mês 03
Operações,Produção A,Material A,100,100000,95000,90000
Logística,Armazenagem,Material B,75,75000,70000,68000
```

## 🎯 Como Usar

### 1. Upload do Arquivo
- Acesse a aplicação Streamlit
- Faça upload do arquivo CSV com dados de estoque
- O sistema detectará automaticamente as gerências

### 2. Geração de Relatórios
- Clique em "Gerar Relatórios PDF"
- O sistema executará todas as análises de IA
- Será gerado um PDF individual para cada gerência

### 3. Download dos Resultados
- Baixe o arquivo ZIP com todos os PDFs
- Cada PDF contém análise completa da respectiva gerência

## 📈 Conteúdo dos Relatórios PDF

### Seção 1: Visão Geral e KPIs
- Cartões com métricas principais
- Gráfico de evolução mensal
- Ranking dos top 10 materiais

### Seção 2: Análises de IA
- Resumo executivo automatizado
- Gráfico de previsões futuras
- Detecção de anomalias
- Recomendações de ações

### Seção 3: Dados Detalhados
- Tabela completa dos dados da gerência
- Valores formatados em moeda brasileira

## 🔧 Personalização

### Modificar Análises de IA
Edite o arquivo `ai_analysis.py` para:
- Ajustar algoritmos de previsão
- Modificar critérios de detecção de anomalias
- Personalizar recomendações

### Customizar Visualizações
Edite o arquivo `enhanced_charts.py` para:
- Alterar cores e estilos dos gráficos
- Modificar layouts dos dashboards
- Adicionar novos tipos de visualização

### Ajustar Layout do PDF
Edite o arquivo `enhanced_pdf_generator.py` para:
- Modificar estrutura das páginas
- Alterar formatação de texto
- Personalizar estilos visuais

## 🧪 Testes

O sistema inclui testes automatizados que verificam:
- ✅ Carregamento de dados
- ✅ Detecção de gerências
- ✅ Execução de análises
- ✅ Geração de gráficos
- ✅ Criação de PDFs

Execute `python test_system.py` para validar o funcionamento.

## 📋 Requisitos do Sistema

### Python 3.11+
### Bibliotecas Principais
- `streamlit` - Interface web
- `pandas` - Manipulação de dados
- `matplotlib` - Gráficos básicos
- `seaborn` - Visualizações estatísticas
- `reportlab` - Geração de PDFs
- `scikit-learn` - Algoritmos de ML
- `statsmodels` - Análises estatísticas

## 🎉 Principais Melhorias

### Em relação ao sistema original:

1. **Análises de IA Integradas**
   - Previsões automáticas
   - Detecção de anomalias
   - Recomendações inteligentes

2. **PDFs Separados por Gerência**
   - Relatórios individualizados
   - Download em lote via ZIP
   - Conteúdo específico por gerência

3. **Visualizações Aprimoradas**
   - Dashboards interativos
   - Gráficos profissionais
   - KPIs visuais

4. **Interface Melhorada**
   - Design moderno
   - Feedback em tempo real
   - Análise prévia opcional

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Execute o script de teste para validar o sistema
3. Confirme que o arquivo CSV está no formato correto
4. Verifique os logs de erro na interface Streamlit

## 📝 Licença

Sistema desenvolvido para análise interna de estoque excedente.
Todos os direitos reservados.

