# 📊 Análise Inteligente de Estoque Excedente

![Status do Projeto](https://img.shields.io/badge/Status-MVP-orange?style=for-the-badge)
![Metodologia](https://img.shields.io/badge/Metodologia-Lean%20Six%20Sigma-green?style=for-the-badge)
![Tecnologia](https://img.shields.io/badge/Tecnologia-IA%20Híbrida-blue?style=for-the-badge)

Sistema completo para **análise, visualização e geração de relatórios de estoque excedente**, integrando **IA Clássica** (preditiva, prescritiva e detecção de anomalias) e **IA Generativa** (resumos executivos via LLMs da OpenAI).

---

## 🎓 Contexto do Projeto (Lean Six Sigma)

Este sistema foi desenvolvido como **Trabalho de Conclusão** para **obtenção do certificado de Green Belt em Lean Six Sigma**, aplicado a um problema real de negócio relacionado à **gestão e otimização de estoque excedente**.

O projeto está inserido em uma iniciativa de **melhoria contínua**, seguindo a metodologia **DMAIC**, com foco principal na fase **Improve**, propondo uma solução tecnológica para apoiar a tomada de decisão gerencial, reduzir desperdícios e aumentar a visibilidade dos dados de estoque.

> [!IMPORTANT]
> 🔁 Trata-se de um **MVP (Minimum Viable Product)**, concebido para evoluir continuamente. Novas funcionalidades, refinamentos analíticos e integrações fazem parte do ciclo de melhoria contínua Lean.

---

## 🚀 Principais Funcionalidades

| Categoria | Funcionalidades |
| :--- | :--- |
| **Dados & KPIs** | Upload de CSV, KPIs automáticos por gerência (Valor, Qtd, Materiais, Variação Mensal). |
| **Visualização** | Gráficos dinâmicos de evolução mensal, Top materiais e Dashboard completo. |
| **IA Clássica** | Análise preditiva (3 meses), detecção de anomalias e recomendações prescritivas. |
| **IA Generativa** | Resumos executivos em linguagem natural e sugestão de ações prioritárias via OpenAI. |
| **Exportação** | Relatórios em PDF com gráficos, CSV processado e exportação em lote (ZIP). |

---

## 🏗️ Estrutura do Projeto

```text
analise_estoque/
├── src
│   ├── ai
│   │   ├── __init__.py
│   │   ├── classic_ai.py
│   │   └── generative_llm.py
│   ├── ui\logs
│   │   └── app.log
│   └── utils
│       ├── __init__.py
│       ├── columns.py
│       └── formatting.py
├── .env.example
├── analysis.py
├── charts.py
├── main_app.py
├── pdf.py
├── .gitignore
├── README.md
└── requirements.txt

```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/analise_estoque.git
cd analise_estoque
```

### 2. Configurar Ambiente
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente (Windows)
.venv\Scripts\activate     
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
USE_LLM=1
OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

---

## ▶️ Execução

Inicie a aplicação Streamlit:
```bash
streamlit run main_app.py
```
Acesse em seu navegador: `http://localhost:8501`

---

## 📂 Formato de Dados (CSV)

O sistema espera um arquivo CSV com as seguintes colunas obrigatórias:

| Coluna | Descrição |
| :--- | :--- |
| **Gerência** | Nome do setor ou departamento responsável. |
| **Material** | Identificação do item em estoque. |
| **Quantidade** | Saldo atual do material. |
| **Valor Mês XX** | Colunas de valores históricos (ex: Valor Mês 01 a Valor Mês 12). |

---

## 🔍 Visão Técnica & Negócios

### Stack Tecnológica
- **Processamento:** Pandas & NumPy.
- **Visualização:** Matplotlib, Seaborn & Streamlit.
- **Relatórios:** ReportLab.
- **Inteligência:** `polyfit` (Tendências), `IsolationForest` (Anomalias) e OpenAI API (LLM).

### Impacto no Negócio
- **Controle Proativo:** Gestão antecipada do excedente.
- **Redução de Custos:** Recomendações baseadas em dados para mitigar desperdícios.
- **Governança:** Relatórios padronizados para auditorias e tomada de decisão executiva.

---

## 🛠️ Roadmap (Fase Improve – DMAIC)

- [x] KPIs automatizados por gerência
- [x] Geração de gráficos e dashboards
- [x] Relatórios PDF detalhados
- [x] IA Clássica para insights
- [x] IA Generativa para resumos executivos
- [ ] Integração nativa com Power BI
- [ ] Módulo de feedback para aprendizado contínuo
- [ ] API REST para integração externa

---

## 👨‍💻 Contribuição

1. Faça um **Fork** do projeto.
2. Crie uma **Branch** para sua feature (`git checkout -b feature/nova-funcionalidade`).
3. Faça o **Commit** de suas alterações (`git commit -m 'Adiciona nova funcionalidade'`).
4. Faça o **Push** para a Branch (`git push origin feature/nova-funcionalidade`).
5. Abra um **Pull Request**.

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License**.
