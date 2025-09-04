# 📊 Análise Inteligente de Estoque Excedente

Sistema completo para **análise, visualização e geração de relatórios de estoque excedente**, integrando **IA Clássica** (preditiva, prescritiva e detecção de anomalias) e **IA Generativa** (resumos executivos via LLMs da OpenAI).  

Este projeto faz parte de uma iniciativa de **melhoria contínua (fase Improve do DMAIC)** voltada para **otimização da gestão de estoque excedente**.

---

## 🚀 Principais Funcionalidades

- **Upload de CSV** com dados de estoque excedente (por Gerência, Material, Quantidade, Valores Mensais).
- **KPIs automáticos** por gerência:
  - Valor total
  - Quantidade total
  - Número de materiais
  - Valor médio por material
  - Variação mensal
- **Gráficos dinâmicos**:
  - Evolução mensal
  - Top materiais
  - Dashboard completo
- **Relatórios em PDF** com capa, gráficos, tabela detalhada e análises de IA.
- **Integração com IA Clássica**:
  - Análise preditiva (tendências de 3 meses)
  - Detecção de anomalias (valores atípicos, crescimentos súbitos)
  - Análise prescritiva (recomendações de ação)
- **Integração com IA Generativa (OpenAI)**:
  - Resumo executivo em linguagem natural
  - Ações prioritárias sugeridas
- **Exportação**:
  - CSV processado
  - PDFs individuais ou em lote (ZIP)

---

## 🏗️ Estrutura do Projeto

```
├── analysis.py          # KPIs, evolução, top materiais, tabelas e análises completas por gerência
├── charts.py            # Gráficos (KPIs, evolução mensal, top materiais, dashboards)
├── main_app.py          # Interface Streamlit (upload, visualização, IA, relatórios)
├── pdf.py               # Geração de relatórios PDF detalhados
├── columns.py           # Identificação de colunas em DataFrames
├── formatting.py        # Funções utilitárias de formatação numérica/monetária
├── classic_ai.py        # IA Clássica: preditiva, anomalias, prescritiva, resumos
├── generative_llm.py    # IA Generativa via OpenAI (LLM-enabled)
└── requirements.txt     # Dependências do projeto
```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/estoque-excedente.git
cd estoque-excedente
```

### 2. Criar ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
Crie um arquivo `.env` na raiz com:

```env
# Ativar/desativar LLM
USE_LLM=1

# Chave da API OpenAI
OPENAI_API_KEY=sk-xxxx

# Modelo e temperatura (opcional)
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

---

## ▶️ Execução

Inicie a aplicação Streamlit:

```bash
streamlit run main_app.py
```

Abra no navegador: [http://localhost:8501](http://localhost:8501)

---

## 📂 Formato esperado do CSV

Colunas obrigatórias:

- **Gerência**
- **Material**
- **Quantidade**
- **Valor Mês 01 … Valor Mês 12**

Exemplo:

| Gerência     | Área   | Material | Quantidade | Valor Mês 01 | Valor Mês 02 | Valor Mês 03 |
|--------------|--------|----------|------------|--------------|--------------|--------------|
| Operações    | Norte  | MAT001   | 120        | 10000        | 12000        | 15000        |
| Qualidade    | Sul    | MAT002   | 80         | 8000         | 7500         | 7000         |

---

## 📑 Fluxo de Uso

1. **Upload do CSV** via interface.
2. **Seleção das Gerências** a analisar.
3. **Geração automática de análises**:
   - KPIs, gráficos, tabelas
   - Insights de IA Clássica
   - Resumo Executivo (IA Generativa, se habilitada)
4. **Exportação**:
   - CSV processado consolidado
   - PDFs individuais ou em lote

---

## 🔍 Visão Técnica

- **Pandas** para manipulação de dados.
- **Matplotlib + Seaborn** para gráficos.
- **Streamlit** para UI interativa.
- **ReportLab** para PDFs.
- **IA Clássica**:
  - `numpy.polyfit` para tendências lineares
  - `IsolationForest` / Z-score para anomalias
  - Heurísticas para recomendações
- **IA Generativa**:
  - Integração com API da OpenAI (Chat Completions).
  - Prompts customizados em português.

---

## 📈 Visão de Negócios

O sistema permite:

- **Controle proativo** do estoque excedente.
- **Detecção precoce** de desvios e anomalias.
- **Recomendações prescritivas** para reduzir custos.
- **Resumos executivos** que facilitam decisões estratégicas.
- **KPIs claros** para monitoramento contínuo.
- **Documentação e relatórios** para auditorias e gestão.

---

## 🛠️ Roadmap (fase Improve – DMAIC)

- [x] KPIs automatizados por gerência
- [x] Geração de gráficos e dashboards
- [x] Relatórios PDF detalhados
- [x] IA Clássica para insights
- [x] IA Generativa para resumos executivos
- [ ] Integração nativa com Power BI
- [ ] Módulo de feedback para aprendizado contínuo
- [ ] API REST para integração com sistemas externos

---

## 👨‍💻 Contribuição

1. Faça um fork do repositório.
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`).
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License**.  
